/* =====================================================================
   Admin Studio — authors & profiles
   Admin: create authors (no password), manage their logins and profiles.
   Author: edit their own public profile.
   ===================================================================== */

Pages.authors = async function (params, el) {
  const people = await A.list('authors');
  A.cache.people = people;
  A.cache.authors = people.map(p => p.author);

  el.innerHTML = `
    <div class="page-head">
      <div><h1>Authors</h1><p>${people.length} author${people.length === 1 ? '' : 's'} ·
        new authors start without a password until you or they set one.</p></div>
      <div class="head-actions"><button class="btn btn-p" data-act="author:new">＋ New author</button></div>
    </div>

    <div class="card pad0">
      <div class="t-wrap"><table>
        <thead><tr><th>Author</th><th>Login</th><th>Password</th><th>Posts</th><th>Last seen</th><th></th></tr></thead>
        <tbody>
          ${people.length ? people.map(p => authorRow(p)).join('') : emptyRow(6, 'No authors yet — add the first one.')}
        </tbody>
      </table></div>
    </div>

    <div class="alert alert-info">
      <strong>How author accounts work.</strong> You create the author, the studio creates a matching username with
      <em>no password</em>. They can sign in immediately with just their username and set a password themselves,
      or you can set one for them. Passwords can be removed again at any time.
    </div>`;
};

function authorRow(p) {
  const a = p.author, acc = p.account, st = p.stats || {};
  const locked = acc?.locked_until && new Date(acc.locked_until) > new Date();
  return `<tr>
    <td>
      <div class="person">${avatarHTML(a.avatar, a.name, 38)}
        <div><div class="t-title">${esc(a.name)}${a.is_visible === false ? ' <span class="pill p-mute">hidden</span>' : ''}</div>
          <div class="t-sub">${esc(a.role || 'Author')}${a.specialization ? ' · ' + esc(a.specialization) : ''}</div></div></div>
    </td>
    <td>
      ${acc
        ? `<div class="nowrap">@${esc(acc.username)}</div>
           <div class="t-sub">${acc.is_active === false ? '<span class="pill p-err">disabled</span>'
              : locked ? '<span class="pill p-warn">locked</span>' : '<span class="pill p-ok">active</span>'}</div>`
        : `<span class="pill p-mute">no login</span>`}
    </td>
    <td>${acc
      ? (acc.has_password ? `<span class="pill p-ok">set</span><div class="t-sub">${fmtAgo(acc.password_set_at)}</div>`
                          : `<span class="pill p-warn">none</span><div class="t-sub">signs in freely</div>`)
      : '—'}</td>
    <td class="t-sub">${st.published || 0} live · ${st.pending || 0} pending<div class="t-sub">${st.views || 0} views</div></td>
    <td class="t-sub nowrap">${acc ? fmtAgo(acc.last_login_at) : '—'}</td>
    <td><div class="t-actions">
      <button class="btn btn-o btn-s" data-act="author:profile" data-id="${attr(a.id)}">Profile</button>
      <button class="btn btn-o btn-s" data-act="author:menu" data-id="${attr(a.id)}">⋯</button>
    </div></td>
  </tr>`;
}

/* ---------------------------------------------------------------- */
/* create                                                            */
/* ---------------------------------------------------------------- */
A.on('author:new', () => {
  openModal(`
    <h2>New author</h2>
    <p class="muted" style="font-size:.82rem">They will be able to sign in right away — no password needed until one is set.</p>
    <div class="row" style="margin-top:16px">
      <div class="fg"><label>Full name <span class="req">*</span></label>
        <input class="fc" id="na-name" autofocus placeholder="Jane Doe"></div>
      <div class="fg"><label>Profile ID (URL)</label>
        <input class="fc" id="na-id" placeholder="jane-doe"></div>
    </div>
    <div class="row">
      <div class="fg"><label>Username for signing in</label>
        <input class="fc" id="na-user" placeholder="jane-doe" autocomplete="off"></div>
      <div class="fg"><label>Job title</label>
        <input class="fc" id="na-role" placeholder="Staff writer"></div>
    </div>
    <div class="row">
      <div class="fg"><label>Email</label><input class="fc" id="na-email" type="email" placeholder="jane@example.com"></div>
      <div class="fg"><label>Specialization</label><input class="fc" id="na-spec" placeholder="Product, design"></div>
    </div>
    <div class="fg"><label>Short bio</label><textarea class="fc" id="na-bio" placeholder="A sentence or two for the public profile."></textarea></div>
    <details style="margin-top:6px">
      <summary style="cursor:pointer;font-size:.82rem;color:var(--tx-2)">Set a password now (optional)</summary>
      <div class="fg" style="margin-top:10px"><label>Password</label>
        <input class="fc" id="na-pass" type="text" autocomplete="new-password" placeholder="Leave empty for passwordless sign-in">
        <div class="hint">You can always add or remove it later, and so can the author.</div></div>
    </details>
    <div class="m-act">
      <button class="btn btn-o" data-act="modal:close">Cancel</button>
      <button class="btn btn-p" data-act="author:create">Create author</button>
    </div>`, { });
  document.getElementById('na-name').addEventListener('input', (e) => {
    const s = slugify(e.target.value);
    if (!document.getElementById('na-id').dataset.t) setVal('na-id', s);
    if (!document.getElementById('na-user').dataset.t) setVal('na-user', s);
  });
  ['na-id', 'na-user'].forEach(id =>
    document.getElementById(id).addEventListener('input', (e) => { e.target.dataset.t = '1'; }));
});

A.on('author:create', async () => {
  const name = val('na-name');
  if (!name) { toast('A name is required', 'err'); return; }
  const r = await A.act('api_save_author', {
    p_data: {
      id: val('na-id') || slugify(name), name, username: val('na-user') || slugify(name),
      role: val('na-role'), email: val('na-email'), specialization: val('na-spec'),
      bio: val('na-bio'), create_account: true
    }
  });
  if (!r) return;
  const pass = val('na-pass');
  if (pass && r.account_id) {
    await A.act('api_admin_set_password', { p_account_id: r.account_id, p_new: pass }, false);
  }
  closeModal();
  A.go('authors');
});

/* ---------------------------------------------------------------- */
/* per-author actions                                                */
/* ---------------------------------------------------------------- */
A.on('author:menu', (d) => {
  const p = (A.cache.people || []).find(x => x.author.id === d.id);
  if (!p) return;
  const acc = p.account;
  const rows = [
    ['profile', '🪪 Edit public profile'],
    ['write', '✎ Write a post as ' + p.author.name]
  ];
  if (acc) {
    rows.push([acc.has_password ? 'password' : 'password', acc.has_password ? '🔑 Change or remove password' : '🔑 Set a password']);
    rows.push(['username', '@ Change username']);
    rows.push(['sessions', '💻 Active sessions']);
    if (acc.locked_until && new Date(acc.locked_until) > new Date()) rows.push(['unlock', '🔓 Unlock account']);
    rows.push([acc.is_active === false ? 'enable' : 'disable',
               acc.is_active === false ? '✅ Enable sign-in' : '⛔ Disable sign-in']);
  } else {
    rows.push(['create-login', '＋ Give this author a login']);
  }
  rows.push(['delete', '🗑 Remove author']);

  openModal(`<h2>${esc(p.author.name)}</h2>
    <p class="muted" style="font-size:.8rem">${acc ? '@' + esc(acc.username) : 'no login yet'} ·
      ${p.stats?.total || 0} posts</p>
    <div class="stack" style="margin-top:14px">
      ${rows.map(([k, l]) => `<button class="btn ${k === 'delete' ? 'btn-d' : 'btn-o'}" style="justify-content:flex-start"
        data-act="author:do" data-do="${k}" data-id="${attr(p.author.id)}">${l}</button>`).join('')}
    </div>
    <div class="m-act"><button class="btn btn-ghost" data-act="modal:close">Close</button></div>`, { small: true });
});

A.on('author:do', async (d) => {
  const p = (A.cache.people || []).find(x => x.author.id === d.id);
  const acc = p?.account;
  closeModal();
  switch (d.do) {
    case 'profile': return A.go('profile', { id: d.id });
    case 'write': return A.go('editor', { author: d.id });
    case 'password': return Security.passwordDialog({ target: acc, name: p.author.name });
    case 'sessions': return Security.sessionsDialog(acc.id, p.author.name);
    case 'username': return usernameDialog(p);
    case 'unlock':
      await A.act('api_author_action', { p_id: d.id, p_action: 'unlock' });
      return A.go('authors');
    case 'enable':
    case 'disable': {
      const active = d.do === 'enable';
      if (!active && !await confirmDialog({
        title: 'Disable this login?', danger: true, okLabel: 'Disable',
        body: '<p>They will be signed out everywhere and cannot sign in again until you re-enable it. Their posts stay online.</p>'
      })) return;
      await A.act('api_author_action', { p_id: d.id, p_action: 'set_active', p_value: { active } });
      return A.go('authors');
    }
    case 'create-login': return usernameDialog(p, true);
    case 'delete': return deleteAuthorDialog(p);
  }
});

function usernameDialog(p, create) {
  openModal(`<h2>${create ? 'Create a login' : 'Change username'}</h2>
    <div class="fg" style="margin-top:12px"><label>Username</label>
      <input class="fc" id="un-name" autofocus autocomplete="off"
             value="${attr(p.account?.username || slugify(p.author.id))}">
      <div class="hint">Lower-case, no spaces. "admin" is reserved.</div></div>
    <div class="m-act"><button class="btn btn-o" data-act="modal:close">Cancel</button>
      <button class="btn btn-p" data-act="author:username-go" data-id="${attr(p.author.id)}">Save</button></div>`, { small: true });
}
A.on('author:username-go', async (d) => {
  const r = await A.act('api_author_action', {
    p_id: d.id, p_action: 'set_username', p_value: { username: slugify(val('un-name')) }
  });
  if (r) { closeModal(); A.go('authors'); }
});

function deleteAuthorDialog(p) {
  const others = (A.cache.authors || []).filter(a => a.id !== p.author.id);
  openModal(`<h2>Remove ${esc(p.author.name)}?</h2>
    <div class="modal-body">
      <p>Their login is removed too. Choose what happens to their ${p.stats?.total || 0} post(s).</p>
    </div>
    <div class="fg"><label>Posts</label>
      <select class="fc" id="da-mode">
        <option value="keep">Keep them online without an author</option>
        ${others.length ? `<option value="move">Move them to another author</option>` : ''}
        <option value="delete">Delete the posts as well</option>
      </select></div>
    <div class="fg" id="da-to-wrap" style="display:none"><label>New author</label>
      <select class="fc" id="da-to">${others.map(a => `<option value="${attr(a.id)}">${esc(a.name)}</option>`).join('')}</select></div>
    <div class="m-act"><button class="btn btn-o" data-act="modal:close">Cancel</button>
      <button class="btn btn-d" data-act="author:delete-go" data-id="${attr(p.author.id)}">Remove author</button></div>`, { small: true });
  document.getElementById('da-mode').addEventListener('change', (e) => {
    document.getElementById('da-to-wrap').style.display = e.target.value === 'move' ? '' : 'none';
  });
}
A.on('author:delete-go', async (d) => {
  const mode = val('da-mode');
  const value = mode === 'move' ? { reassign_to: val('da-to') }
              : mode === 'delete' ? { delete_posts: true } : {};
  closeModal();
  const r = await A.act('api_author_action', { p_id: d.id, p_action: 'delete', p_value: value });
  if (r) { await A.refreshTaxonomy(); A.go('authors'); }
});

A.on('author:profile', (d) => A.go('profile', { id: d.id }));

/* =====================================================================
   Profile editor — used by authors for themselves and by the admin
   on behalf of any author.
   ===================================================================== */
Pages.profile = async function (params, el) {
  const id = params?.id || A.myAuthorId;
  if (!id) {
    el.innerHTML = `<div class="card"><h2>No author profile</h2>
      <p class="muted">The admin account is not an author. Create an author from the
      <a href="#" data-act="go" data-page="authors">Authors</a> page to publish under a byline.</p></div>`;
    return;
  }
  const a = await A.get('author', id);
  if (!a) { toast('Profile not found', 'err'); return A.go('dashboard'); }
  const mine = id === A.myAuthorId;
  const s = a.socials || {};

  el.innerHTML = `
    <div class="page-head">
      <div>
        ${A.isAdmin && !mine ? `<button class="btn btn-ghost btn-s" data-act="go" data-page="authors">← Back to authors</button>` : ''}
        <h1 style="margin-top:4px">${mine ? 'My profile' : esc(a.name)}</h1>
        <p class="muted">This is what readers see on every post and on the author page.</p>
      </div>
      <div class="head-actions">
        <button class="btn btn-o" data-act="profile:view" data-id="${attr(a.id)}">👁 Public page</button>
        <button class="btn btn-p" data-act="profile:save" data-id="${attr(a.id)}">Save profile</button>
      </div>
    </div>

    <div class="grid g2">
      <div>
        <div class="card">
          <div class="card-hd"><h2>Identity</h2></div>
          <div class="row">
            <div class="fg"><label>Display name <span class="req">*</span></label>
              <input class="fc" id="pr-name" value="${attr(a.name)}"></div>
            <div class="fg"><label>Job title</label>
              <input class="fc" id="pr-role" value="${attr(a.role || '')}" placeholder="Senior writer"></div>
          </div>
          <div class="row">
            <div class="fg"><label>Specialization</label>
              <input class="fc" id="pr-spec" value="${attr(a.specialization || '')}" placeholder="Fintech, policy"></div>
            <div class="fg"><label>Location</label>
              <input class="fc" id="pr-loc" value="${attr(a.location || '')}" placeholder="Lagos, Nigeria"></div>
          </div>
          <div class="fg"><label>Tagline</label>
            <input class="fc" id="pr-tag" value="${attr(a.tagline || '')}" placeholder="One line that sums you up"></div>
          <div class="fg"><label>About you</label>
            <textarea class="fc" id="pr-bio" style="min-height:130px"
              placeholder="Tell readers who you are and what you write about.">${esc(a.bio || '')}</textarea>
            <div class="hint">Shown on your author page and under your posts.</div></div>
          <div class="fg"><label>Areas of expertise</label>
            <input class="fc" id="pr-exp" value="${attr((a.expertise || []).join(', '))}" placeholder="comma, separated">
          </div>
        </div>

        <div class="card">
          <div class="card-hd"><h2>Contact &amp; links</h2></div>
          <div class="row">
            <div class="fg"><label>Public email</label><input class="fc" id="pr-email" type="email" value="${attr(a.email || '')}"></div>
            <div class="fg"><label>Phone</label><input class="fc" id="pr-phone" value="${attr(a.phone || '')}"></div>
          </div>
          <div class="fg"><label>Website</label><input class="fc" id="pr-web" value="${attr(a.website || '')}" placeholder="https://"></div>
          <div class="row">
            <div class="fg"><label>X / Twitter</label><input class="fc" id="pr-tw" value="${attr(s.twitter || '')}"></div>
            <div class="fg"><label>LinkedIn</label><input class="fc" id="pr-in" value="${attr(s.linkedin || '')}"></div>
          </div>
          <div class="row">
            <div class="fg"><label>Instagram</label><input class="fc" id="pr-ig" value="${attr(s.instagram || '')}"></div>
            <div class="fg"><label>Facebook</label><input class="fc" id="pr-fb" value="${attr(s.facebook || '')}"></div>
          </div>
          <div class="row">
            <div class="fg"><label>GitHub</label><input class="fc" id="pr-gh" value="${attr(s.github || '')}"></div>
            <div class="fg"><label>YouTube</label><input class="fc" id="pr-yt" value="${attr(s.youtube || '')}"></div>
          </div>
        </div>
      </div>

      <div>
        <div class="side-card">
          <h3>Photo</h3>
          ${Upload.field('avatar', { label: '', bucket: 'author-avatars', value: a.avatar, hint: 'Square image, at least 200×200px' })}
        </div>
        <div class="side-card">
          <h3>Cover image</h3>
          ${Upload.field('cover-img', { label: '', bucket: 'author-avatars', value: a.cover_image, hint: 'Wide banner for your author page' })}
        </div>
        ${A.isAdmin ? `<div class="side-card">
          <h3>Admin controls</h3>
          <label class="switch"><input type="checkbox" id="pr-visible" ${a.is_visible !== false ? 'checked' : ''}>
            <span class="sw-txt">Show on the site<small>Hide to keep the byline but drop the profile page</small></span></label>
          <div class="fg" style="margin-top:8px"><label>Sort order</label>
            <input class="fc" type="number" id="pr-sort" value="${a.sort_order || 0}"></div>
          <button class="btn btn-o btn-s" data-act="author:menu" data-id="${attr(a.id)}">Account &amp; password…</button>
        </div>` : `<div class="side-card">
          <h3>Your account</h3>
          <div class="kv"><span>Username</span><strong>@${esc(A.me.username)}</strong></div>
          <div class="kv"><span>Password</span><strong>${A.me.has_password ? 'Set' : 'None'}</strong></div>
          <button class="btn btn-o btn-s" style="margin-top:10px" data-act="security:password">
            ${A.me.has_password ? 'Change or remove password' : 'Set a password'}</button>
        </div>`}
        <div class="side-card">
          <h3>Profile ID</h3>
          <p class="muted" style="font-size:.78rem">Used in the address of your public page.</p>
          <code>#/author/${esc(a.id)}</code>
        </div>
      </div>
    </div>`;
};

A.on('profile:view', (d) => window.open('index.html#/author/' + encodeURIComponent(d.id), '_blank'));

A.on('profile:save', async (d) => {
  const data = {
    id: d.id,
    name: val('pr-name'),
    role: val('pr-role'),
    specialization: val('pr-spec'),
    location: val('pr-loc'),
    tagline: val('pr-tag'),
    bio: val('pr-bio'),
    expertise: val('pr-exp').split(',').map(x => x.trim()).filter(Boolean),
    email: val('pr-email'),
    phone: val('pr-phone'),
    website: val('pr-web'),
    avatar: Upload.value('avatar'),
    cover_image: Upload.value('cover-img'),
    socials: {
      twitter: val('pr-tw'), linkedin: val('pr-in'), instagram: val('pr-ig'),
      facebook: val('pr-fb'), github: val('pr-gh'), youtube: val('pr-yt')
    },
    create_account: false
  };
  if (A.isAdmin) {
    data.is_visible = checked('pr-visible');
    data.sort_order = Number(val('pr-sort') || 0);
  }
  if (!data.name) { toast('A display name is required', 'err'); return; }
  const r = await A.act('api_save_author', { p_data: data });
  if (!r) return;
  await A.refreshTaxonomy();
  if (d.id === A.myAuthorId) {
    const s = await A.call('api_session');
    A.me = s.account;
    A.renderChrome();
  }
});
