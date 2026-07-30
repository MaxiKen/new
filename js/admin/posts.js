/* =====================================================================
   Admin Studio — posts list + writing desk
   Admins see every post and may publish as any author.
   Authors only ever see and touch their own posts.
   ===================================================================== */

const PostsUI = {
  rows: [],
  page: 1,
  size: 12,
  f: { q: '', status: 'all', cat: '', author: '' },

  async load() {
    this.rows = await A.list('posts');
  },

  filtered() {
    const q = this.f.q.toLowerCase();
    return this.rows.filter(p =>
      (this.f.status === 'all' || p.status === this.f.status) &&
      (!this.f.cat || p.category === this.f.cat) &&
      (!this.f.author || p.author === this.f.author) &&
      (!q || (p.title || '').toLowerCase().includes(q) || (p.id || '').toLowerCase().includes(q) ||
        (p.tags || []).join(' ').toLowerCase().includes(q)));
  },

  counts() {
    const c = { all: this.rows.length };
    ['published', 'draft', 'review', 'scheduled', 'archived'].forEach(s =>
      c[s] = this.rows.filter(p => p.status === s).length);
    return c;
  },

  render() {
    const el = document.getElementById('posts-body');
    if (!el) return;
    const list = this.filtered();
    const p = paginate(list, this.page, this.size);
    this.page = p.page;

    el.innerHTML = `
      <div class="t-wrap">
        <table>
          <thead><tr>
            <th style="width:26px"><input type="checkbox" data-act="post:sel-all"></th>
            <th>Title</th>
            ${A.isAdmin ? '<th>Author</th>' : ''}
            <th>Category</th><th>Status</th><th class="nowrap">Updated</th><th>Views</th><th></th>
          </tr></thead>
          <tbody>
            ${p.items.length ? p.items.map(row => this.row(row)).join('')
              : emptyRow(A.isAdmin ? 8 : 7, list.length === 0 && this.rows.length === 0
                  ? 'No posts yet — create your first one.' : 'No posts match these filters.')}
          </tbody>
        </table>
      </div>
      ${pagerHTML(p, 'post:page')}`;

    document.getElementById('posts-count').textContent =
      `${p.total} post${p.total === 1 ? '' : 's'}`;
  },

  row(p) {
    const sched = p.status === 'scheduled' && p.scheduled_for
      ? `<div class="t-sub">goes live ${fmtDate(p.scheduled_for, true)}</div>` : '';
    return `<tr>
      <td><input type="checkbox" class="post-check" value="${attr(p.id)}"></td>
      <td>
        <div class="t-title">${esc(p.title)} ${p.is_featured ? '<span class="pill p-info">★ featured</span>' : ''}</div>
        <div class="t-sub">/${esc(p.id)} · ${p.reading_minutes || 1} min read</div>
        ${p.review_note ? `<div class="t-sub" style="color:var(--warn)">↩ ${esc(p.review_note)}</div>` : ''}
        ${sched}
      </td>
      ${A.isAdmin ? `<td class="nowrap">${esc(p.author_name || '—')}</td>` : ''}
      <td class="nowrap"><div>${esc(p.category_title || p.category)}</div>
        <div class="t-sub">${esc(p.subtopic_title || '')}</div></td>
      <td>${statusPill(p.status)}</td>
      <td class="nowrap t-sub">${fmtAgo(p.updated_at || p.created_at)}</td>
      <td class="t-sub">${p.views || 0}</td>
      <td><div class="t-actions">
        <button class="btn btn-o btn-s" data-act="post:edit" data-id="${attr(p.id)}">Edit</button>
        <button class="btn btn-o btn-s" data-act="post:menu" data-id="${attr(p.id)}">⋯</button>
      </div></td>
    </tr>`;
  }
};

Pages.posts = async function (params, el) {
  await PostsUI.load();
  const c = PostsUI.counts();
  const tabs = [['all', 'All'], ['published', 'Published'], ['draft', 'Drafts'],
                ['review', 'In review'], ['scheduled', 'Scheduled'], ['archived', 'Archived']];

  el.innerHTML = `
    <div class="page-head">
      <div><h1>${A.isAdmin ? 'Posts' : 'My posts'}</h1>
        <p id="posts-count" class="muted"></p></div>
      <div class="head-actions">
        <button class="btn btn-p" data-act="post:new">✎ New post</button>
      </div>
    </div>

    <div class="filters">
      <div class="seg">${tabs.map(([k, l]) =>
        `<button class="${PostsUI.f.status === k ? 'on' : ''}" data-act="post:tab" data-status="${k}">${l} <span class="muted">${c[k] || 0}</span></button>`).join('')}</div>
      <div class="search-box"><input class="fc" id="pf-q" placeholder="Search title, slug or tag…" value="${attr(PostsUI.f.q)}"></div>
      <select class="fc" id="pf-cat">
        <option value="">All categories</option>
        ${A.postCategories().map(x => `<option value="${attr(x.id)}" ${PostsUI.f.cat === x.id ? 'selected' : ''}>${esc(x.title)}</option>`).join('')}
      </select>
      ${A.isAdmin ? `<select class="fc" id="pf-author">
        <option value="">All authors</option>
        ${(A.cache.authors || []).map(x => `<option value="${attr(x.id)}" ${PostsUI.f.author === x.id ? 'selected' : ''}>${esc(x.name)}</option>`).join('')}
      </select>` : ''}
    </div>

    <div class="card pad0">
      <div class="bulkbar" id="bulkbar" style="display:none">
        <strong id="bulk-n">0 selected</strong>
        <button class="btn btn-o btn-s" data-act="post:bulk" data-do="publish">Publish</button>
        <button class="btn btn-o btn-s" data-act="post:bulk" data-do="unpublish">Move to drafts</button>
        <button class="btn btn-o btn-s" data-act="post:bulk" data-do="archive">Archive</button>
        <button class="btn btn-d btn-s" data-act="post:bulk" data-do="delete">Delete</button>
      </div>
      <div id="posts-body"></div>
    </div>`;

  PostsUI.render();

  document.getElementById('pf-q').addEventListener('input', debounce(e => {
    PostsUI.f.q = e.target.value.trim(); PostsUI.page = 1; PostsUI.render();
  }, 200));
  document.getElementById('pf-cat').addEventListener('change', e => {
    PostsUI.f.cat = e.target.value; PostsUI.page = 1; PostsUI.render();
  });
  document.getElementById('pf-author')?.addEventListener('change', e => {
    PostsUI.f.author = e.target.value; PostsUI.page = 1; PostsUI.render();
  });
  document.addEventListener('change', bulkWatch);
};

function bulkWatch(e) {
  if (!e.target.classList?.contains('post-check')) return;
  const n = document.querySelectorAll('.post-check:checked').length;
  const bar = document.getElementById('bulkbar');
  if (!bar) return;
  bar.style.display = n ? '' : 'none';
  document.getElementById('bulk-n').textContent = `${n} selected`;
}

A.on('post:tab', (d) => { PostsUI.f.status = d.status; PostsUI.page = 1; A.go('posts'); });
A.on('post:page', (d) => { PostsUI.page = +d.pageN; PostsUI.render(); });
A.on('post:sel-all', (d, el) => {
  document.querySelectorAll('.post-check').forEach(c => { c.checked = el.checked; });
  bulkWatch({ target: { classList: { contains: () => true } } });
});

A.on('post:bulk', async (d) => {
  const ids = [...document.querySelectorAll('.post-check:checked')].map(c => c.value);
  if (!ids.length) return;
  if (d.do === 'delete' && !await confirmDialog({
    title: `Delete ${ids.length} post(s)?`, danger: true, okLabel: 'Delete',
    body: '<p>This cannot be undone.</p>'
  })) return;
  for (const id of ids) await A.act('api_post_action', { p_id: id, p_action: d.do }, false);
  toast(`${ids.length} post(s) updated`, 'ok');
  A.go('posts');
});

A.on('post:menu', async (d) => {
  const p = PostsUI.rows.find(x => x.id === d.id);
  if (!p) return;
  const canDelete = A.isAdmin || A.editorial.authors_can_delete !== false;
  const opts = [];
  if (p.status !== 'published') opts.push(['publish', A.isAdmin ? '🚀 Publish now' : '🚀 Publish']);
  if (p.status === 'published') opts.push(['unpublish', '📝 Move back to drafts']);
  if (p.status === 'review' && A.isAdmin) opts.push(['approve', '✅ Approve & publish'], ['reject', '↩ Send back to author']);
  if (p.status !== 'review' && !A.isAdmin) opts.push(['submit', '📤 Submit for review']);
  if (A.isAdmin) opts.push([p.is_featured ? 'unfeature' : 'feature', p.is_featured ? '☆ Remove from featured' : '★ Mark as featured']);
  opts.push(['duplicate', '⧉ Duplicate'], ['revisions', '🕘 Revision history']);
  if (p.status === 'published') opts.push(['view', '🌐 Open on the site']);
  if (p.status !== 'archived') opts.push(['archive', '🗄 Archive']);
  if (canDelete) opts.push(['delete', '🗑 Delete']);

  openModal(`<h2>${esc(p.title)}</h2>
    <p class="muted" style="font-size:.8rem">/${esc(p.id)} · ${esc(p.author_name || '')} · ${p.views || 0} views</p>
    <div class="stack" style="margin-top:14px">
      ${opts.map(([k, l]) => `<button class="btn ${k === 'delete' ? 'btn-d' : 'btn-o'}" style="justify-content:flex-start"
          data-act="post:do" data-id="${attr(p.id)}" data-do="${k}">${l}</button>`).join('')}
    </div>
    <div class="m-act"><button class="btn btn-ghost" data-act="modal:close">Close</button></div>`, { small: true });
});

A.on('modal:close', () => closeModal());

A.on('post:do', async (d) => {
  closeModal();
  const id = d.id;
  if (d.do === 'view') { window.open('index.html#/post/' + encodeURIComponent(id), '_blank'); return; }
  if (d.do === 'revisions') return Editor.revisions(id);
  if (d.do === 'reject') return rejectDialog(id);
  if (d.do === 'delete') {
    const ok = await confirmDialog({
      title: 'Delete this post?', danger: true, okLabel: 'Delete for good',
      body: '<p>The post and its revision history will be removed. This cannot be undone.</p>'
    });
    if (!ok) return;
  }
  const r = await A.act('api_post_action', { p_id: id, p_action: d.do });
  if (r) A.go('posts');
});

A.on('post:approve', async (d) => { await A.act('api_post_action', { p_id: d.id, p_action: 'approve' }); A.go(A.page); });
A.on('post:reject', (d) => rejectDialog(d.id));

function rejectDialog(id) {
  openModal(`<h2>Send back to the author</h2>
    <div class="fg"><label>What should be changed?</label>
      <textarea class="fc" id="rj-note" autofocus placeholder="Add a short note for the author…"></textarea></div>
    <div class="m-act"><button class="btn btn-o" data-act="modal:close">Cancel</button>
      <button class="btn btn-w" data-act="post:reject-go" data-id="${attr(id)}">Send back</button></div>`, { small: true });
}
A.on('post:reject-go', async (d) => {
  const note = val('rj-note');
  closeModal();
  await A.act('api_post_action', { p_id: d.id, p_action: 'reject', p_value: { note } });
  A.go(A.page);
});

/* =====================================================================
   Writing desk
   ===================================================================== */
const Editor = {
  post: null,
  quill: null,
  dirty: false,
  isNew: false,
  autosaveTimer: null,

  backupKey(id) { return 'blog_studio_draft_' + (id || 'new'); },

  async open(params) {
    this.isNew = !params?.id;
    this.dirty = false;
    if (this.isNew) {
      this.post = {
        id: '', title: '', excerpt: '', content: '', category: A.postCategories()[0]?.id || '',
        subtopic: '', author: params?.author || A.myAuthorId || '', tags: [], status: 'draft',
        published_date: new Date().toISOString().slice(0, 10), seo: {}, is_featured: false
      };
    } else {
      this.post = await A.get('post', params.id);
      if (!this.post) { toast('That post no longer exists', 'err'); A.go('posts'); return; }
      this.post.tags = this.post.tags || [];
      this.post.seo = this.post.seo || {};
    }
    this.render();
  },

  statusOptions() {
    const canPublish = A.isAdmin || (A.editorial.authors_can_publish !== false && A.editorial.require_approval !== true);
    const canSchedule = A.isAdmin || A.editorial.authors_can_schedule !== false;
    const out = [['draft', 'Draft — only visible here']];
    if (!A.isAdmin) out.push(['review', 'Submit for review']);
    if (canSchedule) out.push(['scheduled', 'Scheduled — publish later']);
    if (canPublish) out.push(['published', 'Published — live on the site']);
    if (A.isAdmin) out.push(['review', 'In review'], ['archived', 'Archived']);
    const seen = new Set();
    return out.filter(([k]) => !seen.has(k) && seen.add(k));
  },

  render() {
    const p = this.post;
    const el = document.getElementById('page');
    const subs = (A.cache.subtopics || []).filter(s => s.category_id === p.category);

    el.innerHTML = `
      <div class="page-head">
        <div>
          <button class="btn btn-ghost btn-s" data-act="editor:back">← Back to posts</button>
          <h1 style="margin-top:6px">${this.isNew ? 'New post' : 'Edit post'}</h1>
          <p class="muted" id="save-state">${this.isNew ? 'Not saved yet' : 'Last saved ' + fmtAgo(p.updated_at)}</p>
        </div>
        <div class="head-actions">
          <button class="btn btn-o" data-act="editor:preview">👁 Preview</button>
          <button class="btn btn-o" data-act="editor:save" data-mode="draft">Save draft</button>
          ${this.primaryButton()}
        </div>
      </div>

      <div class="editor-grid">
        <div>
          <div class="card">
            <input class="editor-title" id="e-title" placeholder="Post title" value="${attr(p.title)}">
            <div class="slug-row">
              <span>${esc(location.host)}/#/post/</span>
              <input id="e-slug" value="${attr(p.id)}" placeholder="post-slug">
              <button class="btn btn-ghost btn-s" data-act="editor:reslug">regenerate</button>
            </div>
            <div id="e-editor"></div>
            <div class="metrics">
              <span id="m-words">0 words</span><span id="m-read">1 min read</span>
              <span id="m-chars">0 characters</span>
            </div>
          </div>

          <div class="card">
            <div class="card-hd"><h2>Summary</h2>
              <button class="btn btn-ghost btn-s" data-act="editor:auto-excerpt">Generate from content</button></div>
            <textarea class="fc" id="e-excerpt" maxlength="400"
              placeholder="One or two sentences shown on cards and in search results.">${esc(p.excerpt || '')}</textarea>
          </div>

          <div class="card">
            <div class="card-hd"><h2>Search engine preview</h2></div>
            <div class="row">
              <div class="fg"><label>Meta title</label>
                <input class="fc" id="e-seo-t" value="${attr(p.seo?.meta_title || '')}" placeholder="${attr(p.title || 'Post title')}"></div>
              <div class="fg"><label>Canonical URL</label>
                <input class="fc" id="e-seo-c" value="${attr(p.seo?.canonical || '')}" placeholder="https://…"></div>
            </div>
            <div class="fg"><label>Meta description</label>
              <textarea class="fc" id="e-seo-d" maxlength="320" style="min-height:60px">${esc(p.seo?.meta_description || '')}</textarea></div>
            <label class="switch"><input type="checkbox" id="e-seo-nx" ${p.seo?.noindex ? 'checked' : ''}>
              <span class="sw-txt">Hide from search engines<small>Adds a noindex hint for this post</small></span></label>
          </div>
        </div>

        <div>
          <div class="side-card">
            <h3>Publishing</h3>
            <div class="fg"><label>Status</label>
              <select class="fc" id="e-status">
                ${this.statusOptions().map(([k, l]) =>
                  `<option value="${k}" ${p.status === k ? 'selected' : ''}>${esc(l)}</option>`).join('')}
              </select></div>
            <div class="fg" id="sched-wrap" style="display:${p.status === 'scheduled' ? '' : 'none'}">
              <label>Publish at</label>
              <input class="fc" type="datetime-local" id="e-sched"
                value="${p.scheduled_for ? new Date(p.scheduled_for).toISOString().slice(0, 16) : ''}">
            </div>
            <div class="fg"><label>Display date</label>
              <input class="fc" type="date" id="e-date" value="${attr((p.published_date || '').slice(0, 10))}"></div>
            <div class="fg"><label>Author</label>
              ${A.isAdmin
                ? `<select class="fc" id="e-author">
                     ${(A.cache.authors || []).map(x =>
                       `<option value="${attr(x.id)}" ${p.author === x.id ? 'selected' : ''}>${esc(x.name)}</option>`).join('')}
                   </select>
                   <div class="hint">As the admin you can publish on behalf of any author.</div>`
                : `<input class="fc" value="${attr(A.me.display_name)}" disabled>
                   <input type="hidden" id="e-author" value="${attr(A.myAuthorId || '')}">`}
            </div>
            ${A.isAdmin ? `<label class="switch"><input type="checkbox" id="e-featured" ${p.is_featured ? 'checked' : ''}>
              <span class="sw-txt">Featured post<small>Highlighted on the home page</small></span></label>` : ''}
            ${p.review_note ? `<div class="alert alert-warn" style="margin-top:10px">Review note: ${esc(p.review_note)}</div>` : ''}
          </div>

          <div class="side-card">
            <h3>Placement</h3>
            <div class="fg"><label>Category <span class="req">*</span></label>
              <select class="fc" id="e-cat">
                <option value="">Choose…</option>
                ${A.postCategories().map(c =>
                  `<option value="${attr(c.id)}" ${p.category === c.id ? 'selected' : ''}>${esc(c.title)}</option>`).join('')}
              </select></div>
            <div class="fg"><label>Subtopic</label>
              <select class="fc" id="e-sub">
                <option value="">— none —</option>
                ${subs.map(s => `<option value="${attr(s.id)}" ${p.subtopic === s.id ? 'selected' : ''}>${esc(s.title)}</option>`).join('')}
              </select></div>
            <div class="fg"><label>Tags</label>
              <input class="fc" id="e-tags" value="${attr((p.tags || []).join(', '))}" placeholder="comma, separated">
              <div class="hint">Readers can click a tag to find related posts.</div></div>
          </div>

          <div class="side-card">
            <h3>Cover image</h3>
            ${Upload.field('cover', { label: '', bucket: 'post-images', value: p.featured_image, hint: 'Recommended 1200×630px' })}
            <div class="fg"><label>Alt text</label>
              <input class="fc" id="e-alt" value="${attr(p.featured_image_alt || '')}" placeholder="Describe the image"></div>
          </div>

          ${!this.isNew ? `<div class="side-card">
            <h3>History</h3>
            <div class="kv"><span>Created</span><span>${fmtDate(p.created_at, true)}</span></div>
            <div class="kv"><span>Views</span><span>${p.views || 0}</span></div>
            <div class="kv"><span>Words</span><span>${p.word_count || 0}</span></div>
            <button class="btn btn-o btn-s" style="margin-top:10px" data-act="editor:revisions" data-id="${attr(p.id)}">🕘 Revision history</button>
            ${(A.isAdmin || A.editorial.authors_can_delete !== false)
              ? `<button class="btn btn-d btn-s" style="margin-top:8px" data-act="editor:delete" data-id="${attr(p.id)}">🗑 Delete post</button>` : ''}
          </div>` : ''}
        </div>
      </div>`;

    this.mountQuill();
    this.bind();
    this.restoreBackup();
  },

  primaryButton() {
    const p = this.post;
    const canPublish = A.isAdmin || (A.editorial.authors_can_publish !== false && A.editorial.require_approval !== true);
    if (p.status === 'published') return `<button class="btn btn-p" data-act="editor:save" data-mode="keep">Update post</button>`;
    if (!canPublish) return `<button class="btn btn-p" data-act="editor:save" data-mode="review">Submit for review</button>`;
    return `<button class="btn btn-p" data-act="editor:save" data-mode="publish">🚀 Publish</button>`;
  },

  mountQuill() {
    this.quill = new Quill('#e-editor', {
      theme: 'snow',
      placeholder: 'Write your story…',
      modules: {
        toolbar: {
          container: [
            [{ header: [2, 3, 4, false] }],
            ['bold', 'italic', 'underline', 'strike'],
            [{ list: 'ordered' }, { list: 'bullet' }, { indent: '-1' }, { indent: '+1' }],
            ['blockquote', 'code-block'],
            ['link', 'image', 'video'],
            [{ align: [] }], [{ color: [] }, { background: [] }],
            ['clean']
          ],
          handlers: {
            image: () => this.insertImage()
          }
        }
      }
    });
    if (this.post.content) this.quill.root.innerHTML = this.post.content;
    this.updateMetrics();
    this.quill.on('text-change', () => { this.touch(); this.updateMetrics(); });
  },

  insertImage() {
    const input = document.createElement('input');
    input.type = 'file'; input.accept = 'image/*';
    input.onchange = async () => {
      const f = input.files?.[0];
      if (!f) return;
      toast('Uploading image…', 'info');
      const ext = (f.name.split('.').pop() || 'jpg').toLowerCase();
      const path = `${slugify(f.name.replace(/\.[^/.]+$/, '')) || 'image'}-${Date.now().toString(36)}.${ext}`;
      const { error } = await A.db.storage.from('post-images').upload(path, f, { cacheControl: '3600' });
      if (error) { toast('Upload failed: ' + error.message, 'err'); return; }
      const { data } = A.db.storage.from('post-images').getPublicUrl(path);
      const range = this.quill.getSelection(true);
      this.quill.insertEmbed(range.index, 'image', data.publicUrl, 'user');
      this.quill.setSelection(range.index + 1);
      A.call('api_save_entry', {
        p_entity: 'media',
        p_data: { url: data.publicUrl, bucket: 'post-images', path, filename: f.name, mime: f.type, size_bytes: String(f.size) }
      }).catch(() => {});
      toast('Image added', 'ok');
    };
    input.click();
  },

  updateMetrics() {
    const text = stripTags(this.quill?.root.innerHTML || '');
    const words = text ? text.split(/\s+/).length : 0;
    document.getElementById('m-words').textContent = words.toLocaleString() + ' words';
    document.getElementById('m-read').textContent = Math.max(1, Math.ceil(words / 200)) + ' min read';
    document.getElementById('m-chars').textContent = text.length.toLocaleString() + ' characters';
  },

  bind() {
    const title = document.getElementById('e-title');
    title.addEventListener('input', () => {
      this.touch();
      if (this.isNew && !document.getElementById('e-slug').dataset.touched)
        document.getElementById('e-slug').value = slugify(title.value);
    });
    document.getElementById('e-slug').addEventListener('input', (e) => {
      e.target.dataset.touched = '1'; this.touch();
    });
    document.getElementById('e-cat').addEventListener('change', (e) => {
      const subs = (A.cache.subtopics || []).filter(s => s.category_id === e.target.value);
      document.getElementById('e-sub').innerHTML =
        '<option value="">— none —</option>' +
        subs.map(s => `<option value="${attr(s.id)}">${esc(s.title)}</option>`).join('');
      this.touch();
    });
    document.getElementById('e-status').addEventListener('change', (e) => {
      document.getElementById('sched-wrap').style.display = e.target.value === 'scheduled' ? '' : 'none';
      this.touch();
    });
    document.querySelectorAll('#page input, #page select, #page textarea')
      .forEach(i => i.addEventListener('change', () => this.touch()));

    clearInterval(this.autosaveTimer);
    this.autosaveTimer = setInterval(() => this.backup(), 6000);
  },

  touch() {
    this.dirty = true;
    const el = document.getElementById('save-state');
    if (el) el.textContent = 'Unsaved changes';
  },

  collect() {
    const status = val('e-status');
    return {
      id: val('e-slug') || slugify(val('e-title')),
      was_id: this.isNew ? '' : this.post.id,
      title: val('e-title'),
      excerpt: val('e-excerpt'),
      content: this.quill.root.innerHTML,
      category: val('e-cat'),
      subtopic: val('e-sub'),
      author: val('e-author'),
      published_date: val('e-date'),
      tags: val('e-tags').split(',').map(t => t.trim()).filter(Boolean),
      featured_image: Upload.value('cover'),
      featured_image_alt: val('e-alt'),
      is_featured: checked('e-featured'),
      status,
      scheduled_for: status === 'scheduled' && val('e-sched') ? new Date(val('e-sched')).toISOString() : null,
      seo: {
        meta_title: val('e-seo-t'), meta_description: val('e-seo-d'),
        canonical: val('e-seo-c'), noindex: checked('e-seo-nx')
      }
    };
  },

  backup() {
    if (!this.dirty) return;
    try {
      localStorage.setItem(this.backupKey(this.post.id),
        JSON.stringify({ at: Date.now(), data: this.collect() }));
    } catch (e) {}
  },

  restoreBackup() {
    try {
      const raw = localStorage.getItem(this.backupKey(this.post.id));
      if (!raw) return;
      const { at, data } = JSON.parse(raw);
      const saved = this.post.updated_at ? new Date(this.post.updated_at).getTime() : 0;
      if (at <= saved + 2000) { localStorage.removeItem(this.backupKey(this.post.id)); return; }
      if (!data.title && !stripTags(data.content)) return;
      openModal(`<h2>Recover unsaved work?</h2>
        <div class="modal-body">We found changes from ${fmtAgo(at)} that were never saved to the server.</div>
        <div class="m-act">
          <button class="btn btn-o" data-act="editor:discard-backup">Discard</button>
          <button class="btn btn-p" data-act="editor:apply-backup">Recover them</button>
        </div>`, { small: true });
      this._backup = data;
    } catch (e) {}
  },

  applyBackup() {
    const d = this._backup;
    if (!d) return;
    setVal('e-title', d.title); setVal('e-slug', d.id); setVal('e-excerpt', d.excerpt);
    setVal('e-tags', (d.tags || []).join(', '));
    this.quill.root.innerHTML = d.content || '';
    this.updateMetrics(); this.touch();
    closeModal();
    toast('Recovered your draft', 'ok');
  },

  async save(mode) {
    const data = this.collect();
    if (!data.title) { toast('Give the post a title first', 'err'); document.getElementById('e-title').focus(); return; }
    if (!data.category) { toast('Choose a category', 'err'); return; }
    if (mode === 'draft') data.status = 'draft';
    if (mode === 'publish') data.status = 'published';
    if (mode === 'review') data.status = 'review';

    const btns = document.querySelectorAll('[data-act="editor:save"]');
    btns.forEach(b => b.disabled = true);
    const r = await A.act('api_save_post', { p_data: data });
    btns.forEach(b => b.disabled = false);
    if (!r) return;

    try { localStorage.removeItem(this.backupKey(this.post.id)); } catch (e) {}
    this.dirty = false;
    this.post = r.post || this.post;
    this.isNew = false;
    A.go('editor', { id: r.id });
  },

  async revisions(id) {
    const rows = await A.list('revisions', { post_id: id });
    openModal(`<h2>Revision history</h2>
      <p class="muted" style="font-size:.8rem">The last 25 versions are kept automatically every time the text changes.</p>
      <div style="margin-top:14px">
        ${rows.length ? rows.map(r => `
          <div class="list-item">
            <div class="li-main"><div class="t-title">${esc(r.title || 'Untitled')}</div>
              <div class="t-sub">${fmtDate(r.created_at, true)} · ${r.chars} characters · ${esc(r.saved_by_name || '')}</div></div>
            <button class="btn btn-o btn-s" data-act="editor:rev-view" data-id="${r.id}">View</button>
            <button class="btn btn-p btn-s" data-act="editor:rev-restore" data-post="${attr(id)}" data-id="${r.id}">Restore</button>
          </div>`).join('') : '<p class="muted">No earlier versions yet.</p>'}
      </div>
      <div class="m-act"><button class="btn btn-o" data-act="modal:close">Close</button></div>`, { wide: true });
  }
};

Pages.editor = (params, el) => Editor.open(params);

A.on('post:new', (d) => A.go('editor', { author: d?.author }));
A.on('post:edit', (d) => A.go('editor', { id: d.id }));
A.on('editor:back', async () => {
  if (Editor.dirty && !await confirmDialog({
    title: 'Leave without saving?', danger: true, okLabel: 'Discard changes',
    body: '<p>Your latest edits are kept in this browser, but not on the server.</p>'
  })) return;
  A.go('posts');
});
A.on('editor:save', (d) => Editor.save(d.mode || 'keep'));
A.on('editor:reslug', () => { setVal('e-slug', slugify(val('e-title'))); Editor.touch(); });
A.on('editor:auto-excerpt', () => {
  const text = stripTags(Editor.quill.root.innerHTML).slice(0, 260);
  setVal('e-excerpt', text ? text.replace(/\s+\S*$/, '') + '…' : '');
  Editor.touch();
});
A.on('editor:preview', () => {
  const d = Editor.collect();
  openModal(`<h2>${esc(d.title || 'Untitled')}</h2>
    <p class="muted" style="font-size:.78rem">${esc(A.authorName(d.author))} · ${fmtDate(d.published_date)} ·
      ${A.catTitle(d.category)}</p>
    ${d.featured_image ? `<img src="${attr(d.featured_image)}" style="width:100%;border-radius:12px;margin:12px 0">` : ''}
    <div class="ql-editor" style="padding:0;margin-top:12px">${d.content}</div>
    <div class="m-act"><button class="btn btn-o" data-act="modal:close">Close preview</button></div>`, { wide: true });
});
A.on('editor:revisions', (d) => Editor.revisions(d.id));
A.on('editor:rev-view', async (d) => {
  const r = await A.get('revision', d.id);
  openModal(`<h2>${esc(r.title || 'Untitled')}</h2>
    <p class="muted" style="font-size:.78rem">Saved ${fmtDate(r.created_at, true)}</p>
    <div class="ql-editor" style="padding:0;margin-top:12px">${r.content || ''}</div>
    <div class="m-act"><button class="btn btn-o" data-act="modal:close">Close</button></div>`, { wide: true });
});
A.on('editor:rev-restore', async (d) => {
  closeModal();
  const r = await A.act('api_post_action', {
    p_id: d.post, p_action: 'restore_revision', p_value: { revision_id: Number(d.id) }
  });
  if (r) A.go('editor', { id: d.post });
});
A.on('editor:apply-backup', () => Editor.applyBackup());
A.on('editor:discard-backup', () => {
  try { localStorage.removeItem(Editor.backupKey(Editor.post.id)); } catch (e) {}
  closeModal();
});
A.on('editor:delete', async (d) => {
  const ok = await confirmDialog({
    title: 'Delete this post?', danger: true, okLabel: 'Delete for good',
    body: '<p>The post and its revisions will be removed permanently.</p>'
  });
  if (!ok) return;
  const r = await A.act('api_post_action', { p_id: d.id, p_action: 'delete' });
  if (r) A.go('posts');
});
