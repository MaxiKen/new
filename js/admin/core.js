/* =====================================================================
   Admin Studio — core
   Session handling, RPC client, and the small UI kit shared by every
   screen of the panel.
   ===================================================================== */

const A = {
  db: null,
  token: null,
  me: null,                 // { id, username, role, author_id, has_password, ... }
  editorial: {},
  page: null,
  cache: {},                // categories / subtopics / authors kept in memory
  handlers: {},

  get isAdmin() { return this.me?.role === 'admin'; },
  get myAuthorId() { return this.me?.author_id || null; },

  /* ---------------------------------------------------------------- */
  /* boot                                                              */
  /* ---------------------------------------------------------------- */
  async boot() {
    if (typeof ENV === 'undefined' || !ENV?.SUPABASE_URL || !window.supabase) {
      document.getElementById('boot-error').style.display = 'block';
      return;
    }
    this.db = window.supabase.createClient(ENV.SUPABASE_URL, ENV.SUPABASE_ANON_KEY, {
      auth: { persistSession: false, autoRefreshToken: false }
    });

    this.bindGlobalEvents();

    this.token = Session.read();
    if (this.token) {
      try {
        const s = await this.rpc('api_session', { p_token: this.token });
        if (s?.ok) { await this.startApp(s); return; }
      } catch (e) { /* fall through to login */ }
      Session.clear();
      this.token = null;
    }
    await Login.show();
  },

  /* ---------------------------------------------------------------- */
  /* rpc                                                               */
  /* ---------------------------------------------------------------- */
  async rpc(fn, args = {}) {
    const { data, error } = await this.db.rpc(fn, args);
    if (error) {
      const msg = error.message || 'Request failed';
      if (/AUTH_REQUIRED/.test(msg)) { this.sessionExpired(); throw new Error('AUTH_REQUIRED'); }
      if (/FORBIDDEN/.test(msg)) throw new Error('You do not have permission to do that.');
      console.warn('[rpc]', fn, error);
      throw new Error(msg);
    }
    return data;
  },

  /** RPC that already carries the session token */
  call(fn, args = {}) { return this.rpc(fn, { p_token: this.token, ...args }); },

  /** call + surface {ok:false,message} results as toasts. Returns data or null */
  async act(fn, args = {}, okMsg) {
    try {
      const r = await this.call(fn, args);
      if (r && r.ok === false) { toast(r.message || r.error || 'That did not work', 'err'); return null; }
      if (okMsg !== false) toast(okMsg || r?.message || 'Saved', 'ok');
      return r;
    } catch (e) {
      if (e.message !== 'AUTH_REQUIRED') toast(e.message, 'err');
      return null;
    }
  },

  list(entity, options = {}) { return this.call('api_list', { p_entity: entity, p_options: options }); },
  get(entity, id) { return this.call('api_get', { p_entity: entity, p_id: id === undefined ? null : String(id) }); },

  /* ---------------------------------------------------------------- */
  /* session lifecycle                                                 */
  /* ---------------------------------------------------------------- */
  async startApp(session) {
    this.me = session.account;
    this.editorial = session.editorial || {};
    document.getElementById('login-view').style.display = 'none';
    document.getElementById('app-view').style.display = '';
    this.renderChrome();
    await this.refreshTaxonomy();
    const first = this.isAdmin ? 'dashboard' : 'dashboard';
    this.go(location.hash.replace('#', '') || first);
    if (session.must_set_password || (this.isAdmin && !this.me.has_password)) {
      document.getElementById('nopass-banner').style.display = '';
    }
  },

  sessionExpired() {
    Session.clear();
    this.token = null; this.me = null;
    document.getElementById('app-view').style.display = 'none';
    Login.show('Your session ended. Please sign in again.');
  },

  async logout() {
    try { await this.call('api_logout'); } catch (e) {}
    Session.clear();
    location.hash = '';
    location.reload();
  },

  /* ---------------------------------------------------------------- */
  /* shared data                                                       */
  /* ---------------------------------------------------------------- */
  async refreshTaxonomy() {
    const [cats, subs, authors] = await Promise.all([
      this.list('categories').catch(() => []),
      this.list('subtopics').catch(() => []),
      this.list('authors').catch(() => [])
    ]);
    this.cache.categories = cats || [];
    this.cache.subtopics = subs || [];
    this.cache.authors = (authors || []).map(a => a.author);
    this.cache.people = authors || [];
  },
  catTitle(id) { return this.cache.categories?.find(c => c.id === id)?.title || id || '—'; },
  subTitle(id) { return this.cache.subtopics?.find(s => s.id === id)?.title || id || '—'; },
  authorName(id) { return this.cache.authors?.find(a => a.id === id)?.name || id || 'Unassigned'; },
  /** categories that can hold blog posts */
  postCategories() {
    return (this.cache.categories || []).filter(c => !['downloads', 'glossary', 'faqs', 'about'].includes(c.type));
  },

  /* ---------------------------------------------------------------- */
  /* navigation                                                        */
  /* ---------------------------------------------------------------- */
  nav: [
    { id: 'dashboard',   label: 'Dashboard',    icon: '📊', roles: ['admin', 'author'] },
    { id: 'posts',       label: 'Posts',        icon: '📝', roles: ['admin'] },
    { id: 'posts',       label: 'My posts',     icon: '📝', roles: ['author'] },
    { id: 'authors',     label: 'Authors',      icon: '👥', roles: ['admin'] },
    { id: 'profile',     label: 'My profile',   icon: '🪪', roles: ['author'] },
    { id: 'media',       label: 'Media',        icon: '🖼️', roles: ['admin', 'author'] },
    { id: 'categories',  label: 'Categories',   icon: '📁', roles: ['admin'] },
    { id: 'downloads',   label: 'Downloads',    icon: '📥', roles: ['admin'] },
    { id: 'glossary',    label: 'Glossary',     icon: '📖', roles: ['admin'] },
    { id: 'faqs',        label: 'FAQs',         icon: '❓', roles: ['admin'] },
    { id: 'about',       label: 'About page',   icon: 'ℹ️', roles: ['admin'] },
    { id: 'messages',    label: 'Messages',     icon: '💬', roles: ['admin'] },
    { id: 'subscribers', label: 'Subscribers',  icon: '📧', roles: ['admin'] },
    { id: 'settings',    label: 'Settings',     icon: '⚙️', roles: ['admin'] },
    { id: 'security',    label: 'Security',     icon: '🔐', roles: ['admin', 'author'] }
  ],

  renderChrome() {
    const role = this.me.role;
    document.getElementById('sb-nav').innerHTML = this.nav
      .filter(n => n.roles.includes(role))
      .map(n => `<button class="nl" data-act="go" data-page="${n.id}"><span>${n.icon}</span>${esc(n.label)}</button>`)
      .join('');

    const name = this.me.display_name || this.me.username;
    document.getElementById('user-chip').innerHTML =
      `${avatarHTML(this.me.avatar, name, 30)}
       <div class="uc-txt">
         <strong>${esc(name)}</strong>
         <small>${this.isAdmin ? 'Administrator' : 'Author'} · @${esc(this.me.username)}</small>
       </div>`;

    document.getElementById('sb-role').textContent = this.isAdmin ? 'Administrator' : 'Author';
  },

  go(page, params) {
    const known = this.nav.some(n => n.id === page && n.roles.includes(this.me.role)) ||
                  ['editor'].includes(page);
    if (!known) page = 'dashboard';
    this.page = page;
    document.querySelectorAll('#sb-nav .nl').forEach(b =>
      b.classList.toggle('on', b.dataset.page === page));
    closeSidebar();
    if (page !== 'editor') history.replaceState(null, '', '#' + page);
    const el = document.getElementById('page');
    el.innerHTML = '<div class="loading"><div class="spin"></div></div>';
    const fn = Pages[page];
    if (!fn) { el.innerHTML = '<div class="card">Page not found.</div>'; return; }
    Promise.resolve(fn(params, el)).catch(e => {
      if (e.message === 'AUTH_REQUIRED') return;
      el.innerHTML = `<div class="card"><h2>Something went wrong</h2><p class="muted">${esc(e.message)}</p></div>`;
    });
    window.scrollTo(0, 0);
  },

  /* ---------------------------------------------------------------- */
  /* event delegation:  data-act="name" + data-* payload               */
  /* ---------------------------------------------------------------- */
  on(name, fn) { this.handlers[name] = fn; },

  bindGlobalEvents() {
    document.addEventListener('click', (e) => {
      const el = e.target.closest('[data-act]');
      if (!el) return;
      const act = el.dataset.act;
      if (act === 'go') { e.preventDefault(); this.go(el.dataset.page); return; }
      const fn = this.handlers[act];
      if (!fn) return;
      e.preventDefault();
      fn(el.dataset, el, e);
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeModal();
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's' && this.page === 'editor') {
        e.preventDefault();
        this.handlers['editor:save']?.({ mode: 'keep' });
      }
    });
    document.getElementById('sb-toggle')?.addEventListener('click', () => {
      document.getElementById('sidebar').classList.toggle('on');
      document.getElementById('sb-overlay').classList.toggle('on');
    });
    document.getElementById('sb-overlay')?.addEventListener('click', closeSidebar);
  }
};

/* ===================================================================== */
/* session storage                                                       */
/* ===================================================================== */
const Session = {
  KEY: 'blog_studio_session',
  save(token, remember, expires) {
    const payload = JSON.stringify({ token, expires });
    try {
      (remember ? localStorage : sessionStorage).setItem(this.KEY, payload);
      (remember ? sessionStorage : localStorage).removeItem(this.KEY);
    } catch (e) {}
  },
  read() {
    try {
      const raw = sessionStorage.getItem(this.KEY) || localStorage.getItem(this.KEY);
      if (!raw) return null;
      const { token, expires } = JSON.parse(raw);
      if (expires && new Date(expires) < new Date()) { this.clear(); return null; }
      return token;
    } catch (e) { return null; }
  },
  clear() {
    try { localStorage.removeItem(this.KEY); sessionStorage.removeItem(this.KEY); } catch (e) {}
  }
};

/* ===================================================================== */
/* tiny UI kit                                                           */
/* ===================================================================== */
function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
function attr(s) { return esc(s).replace(/\n/g, ' '); }

function toast(msg, kind = 'ok', ms = 3600) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'toast t-' + kind + ' on';
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.remove('on'), ms);
}

function openModal(html, opts = {}) {
  const bg = document.getElementById('modal-bg');
  const box = document.getElementById('modal');
  box.className = 'modal' + (opts.wide ? ' wide' : '') + (opts.small ? ' small' : '');
  box.innerHTML = html;
  bg.classList.add('on');
  document.body.style.overflow = 'hidden';
  setTimeout(() => box.querySelector('[autofocus]')?.focus(), 60);
}
function closeModal() {
  document.getElementById('modal-bg')?.classList.remove('on');
  document.body.style.overflow = '';
}
function closeSidebar() {
  document.getElementById('sidebar')?.classList.remove('on');
  document.getElementById('sb-overlay')?.classList.remove('on');
}

/** promise-based confirm dialog */
function confirmDialog({ title, body, danger, okLabel = 'Confirm', cancelLabel = 'Cancel' }) {
  return new Promise(resolve => {
    openModal(
      `<h2>${esc(title)}</h2>
       <div class="modal-body">${body || ''}</div>
       <div class="m-act">
         <button class="btn btn-o" id="cd-no">${esc(cancelLabel)}</button>
         <button class="btn ${danger ? 'btn-d' : 'btn-p'}" id="cd-yes" autofocus>${esc(okLabel)}</button>
       </div>`, { small: true });
    document.getElementById('cd-no').onclick = () => { closeModal(); resolve(false); };
    document.getElementById('cd-yes').onclick = () => { closeModal(); resolve(true); };
  });
}

const val = (id) => document.getElementById(id)?.value.trim() ?? '';
const checked = (id) => !!document.getElementById(id)?.checked;
const setVal = (id, v) => { const el = document.getElementById(id); if (el) el.value = v ?? ''; };

function fmtDate(d, withTime) {
  if (!d) return '—';
  try {
    const dt = new Date(d);
    return dt.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }) +
      (withTime ? ' · ' + dt.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' }) : '');
  } catch (e) { return String(d); }
}
function fmtAgo(d) {
  if (!d) return 'never';
  const s = (Date.now() - new Date(d).getTime()) / 1000;
  if (s < 60) return 'just now';
  if (s < 3600) return Math.floor(s / 60) + 'm ago';
  if (s < 86400) return Math.floor(s / 3600) + 'h ago';
  if (s < 2592000) return Math.floor(s / 86400) + 'd ago';
  return fmtDate(d);
}
function fmtBytes(n) {
  if (!n) return '—';
  const u = ['B', 'KB', 'MB', 'GB'];
  let i = 0; n = Number(n);
  while (n >= 1024 && i < u.length - 1) { n /= 1024; i++; }
  return n.toFixed(n < 10 && i > 0 ? 1 : 0) + ' ' + u[i];
}
function slugify(s) {
  return String(s || '').toLowerCase().normalize('NFKD')
    .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 80);
}
function initials(name) {
  return String(name || '?').split(/\s+/).map(w => w[0]).join('').toUpperCase().slice(0, 2);
}
function avatarHTML(url, name, size = 34) {
  const s = `width:${size}px;height:${size}px;font-size:${Math.round(size / 2.6)}px`;
  return url
    ? `<img class="avatar" style="${s}" src="${attr(url)}" alt="" onerror="this.replaceWith(document.createRange().createContextualFragment('<span class=\\'avatar ph\\' style=\\'${s}\\'>${esc(initials(name))}</span>'))">`
    : `<span class="avatar ph" style="${s}">${esc(initials(name))}</span>`;
}
function stripTags(html) { return String(html || '').replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim(); }
function debounce(fn, ms = 250) {
  let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
}
function statusPill(s) {
  const map = {
    published: ['Published', 'p-ok'], draft: ['Draft', 'p-mute'], review: ['In review', 'p-warn'],
    scheduled: ['Scheduled', 'p-info'], archived: ['Archived', 'p-dark']
  };
  const [label, cls] = map[s] || [s || '—', 'p-mute'];
  return `<span class="pill ${cls}">${esc(label)}</span>`;
}
function emptyRow(cols, text) {
  return `<tr><td colspan="${cols}" class="empty">${esc(text)}</td></tr>`;
}

/* pagination ---------------------------------------------------------- */
function paginate(items, page, size) {
  const total = items.length, pages = Math.max(1, Math.ceil(total / size));
  const p = Math.min(Math.max(1, page), pages);
  return { items: items.slice((p - 1) * size, p * size), page: p, pages, total };
}
function pagerHTML(p, act) {
  if (p.pages <= 1) return '';
  let out = `<div class="pager"><button class="pg" data-act="${act}" data-page-n="${p.page - 1}" ${p.page <= 1 ? 'disabled' : ''}>‹</button>`;
  for (let i = 1; i <= p.pages; i++) {
    if (p.pages > 7 && i > 2 && i < p.pages - 1 && Math.abs(i - p.page) > 1) {
      if (i === 3) out += '<span class="dots">…</span>';
      continue;
    }
    out += `<button class="pg ${i === p.page ? 'on' : ''}" data-act="${act}" data-page-n="${i}">${i}</button>`;
  }
  return out + `<button class="pg" data-act="${act}" data-page-n="${p.page + 1}" ${p.page >= p.pages ? 'disabled' : ''}>›</button></div>`;
}

/* uploads -------------------------------------------------------------- */
const Upload = {
  /** renders a reusable image/file picker */
  field(id, { label, bucket, value, accept = 'image/*', hint }) {
    return `
      <div class="fg upload" id="uw-${id}">
        <label>${esc(label)}</label>
        <div class="up-box" data-act="upload:pick" data-id="${id}">
          <input type="file" id="uf-${id}" accept="${attr(accept)}" hidden data-bucket="${attr(bucket)}">
          <div class="up-prev" id="up-${id}">${value ? `<img src="${attr(value)}" alt="">` : '<span>📁 Click or drop a file here</span>'}</div>
        </div>
        <div class="up-row">
          <input class="fc" id="uv-${id}" value="${attr(value || '')}" placeholder="…or paste a URL">
          <button class="btn btn-o btn-s" data-act="upload:clear" data-id="${id}">Clear</button>
        </div>
        ${hint ? `<small class="muted">${esc(hint)}</small>` : ''}
      </div>`;
  },
  value(id) { return val('uv-' + id); },

  async send(file, bucket, id) {
    const prev = document.getElementById('up-' + id);
    if (prev) prev.innerHTML = '<span class="up-busy">Uploading…</span>';
    try {
      const ext = (file.name.split('.').pop() || 'bin').toLowerCase();
      const base = slugify(file.name.replace(/\.[^/.]+$/, '')) || 'file';
      const path = `${base}-${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}.${ext}`;
      const { error } = await A.db.storage.from(bucket).upload(path, file, { upsert: false, cacheControl: '3600' });
      if (error) throw error;
      const { data } = A.db.storage.from(bucket).getPublicUrl(path);
      const url = data.publicUrl;
      setVal('uv-' + id, url);
      if (prev) prev.innerHTML = file.type.startsWith('image/')
        ? `<img src="${attr(url)}" alt="">`
        : `<span>✅ ${esc(file.name)}</span>`;
      A.call('api_save_entry', {
        p_entity: 'media',
        p_data: { url, bucket, path, filename: file.name, mime: file.type, size_bytes: String(file.size) }
      }).catch(() => {});
      toast('Upload complete', 'ok');
      return url;
    } catch (e) {
      if (prev) prev.innerHTML = '<span>📁 Click or drop a file here</span>';
      toast('Upload failed: ' + (e.message || 'check the storage bucket'), 'err');
      return null;
    }
  }
};

A.on('upload:pick', (d) => document.getElementById('uf-' + d.id)?.click());
A.on('upload:clear', (d) => {
  setVal('uv-' + d.id, '');
  const p = document.getElementById('up-' + d.id);
  if (p) p.innerHTML = '<span>📁 Click or drop a file here</span>';
});
document.addEventListener('change', (e) => {
  const inp = e.target;
  if (inp.tagName === 'INPUT' && inp.type === 'file' && inp.id.startsWith('uf-') && inp.files?.[0]) {
    Upload.send(inp.files[0], inp.dataset.bucket, inp.id.slice(3));
  }
});
document.addEventListener('dragover', (e) => {
  const box = e.target.closest?.('.up-box');
  if (box) { e.preventDefault(); box.classList.add('drag'); }
});
document.addEventListener('dragleave', (e) => e.target.closest?.('.up-box')?.classList.remove('drag'));
document.addEventListener('drop', (e) => {
  const box = e.target.closest?.('.up-box');
  if (!box) return;
  e.preventDefault();
  box.classList.remove('drag');
  const f = e.dataTransfer.files?.[0];
  if (f) {
    const inp = box.querySelector('input[type=file]');
    Upload.send(f, inp.dataset.bucket, inp.id.slice(3));
  }
});

/* page registry — filled by the other modules -------------------------- */
const Pages = {};
