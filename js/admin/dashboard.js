/* =====================================================================
   Admin Studio — dashboard (role aware)
   ===================================================================== */

Pages.dashboard = async function (params, el) {
  const s = await A.call('api_stats');
  el.innerHTML = A.isAdmin ? adminDash(s) : authorDash(s);
};

function statCard(n, label, sub) {
  return `<div class="stat"><div class="n">${n ?? 0}</div><div class="l">${esc(label)}</div>
          ${sub ? `<div class="sub">${sub}</div>` : ''}</div>`;
}

function adminDash(s) {
  const review = s.pending_review || [];
  const checklist = [];
  if (!A.me.has_password) checklist.push(`<li>Protect the studio — <a href="#" data-act="security:password">set your admin password</a></li>`);
  if ((s.authors || 0) === 0) checklist.push(`<li>Add your first author — <a href="#" data-act="go" data-page="authors">Authors</a></li>`);
  if ((s.posts_total || 0) === 0) checklist.push(`<li>Write the first post — <a href="#" data-act="post:new">New post</a></li>`);
  if ((s.accounts_nopass || 0) > 1) checklist.push(`<li>${s.accounts_nopass} accounts still have no password — <a href="#" data-act="go" data-page="security">review access</a></li>`);

  return `
    <div class="page-head">
      <div><h1>Dashboard</h1><p>Everything happening across the blog.</p></div>
      <div class="head-actions">
        <button class="btn btn-o" data-act="go" data-page="posts">All posts</button>
        <button class="btn btn-p" data-act="post:new">✎ New post</button>
      </div>
    </div>

    ${checklist.length ? `<div class="alert alert-info"><strong>Next steps</strong><ul style="margin:6px 0 0 18px">${checklist.join('')}</ul></div>` : ''}

    <div class="grid g3" style="margin-bottom:16px">
      ${statCard(s.posts_published, 'Published posts', `${s.posts_total || 0} total`)}
      ${statCard(s.posts_draft, 'Drafts', `${s.posts_scheduled || 0} scheduled`)}
      ${statCard(s.posts_review, 'Awaiting review', review.length ? 'needs your attention' : 'all clear')}
      ${statCard(s.views_total, 'Total views', `${s.views_7d || 0} in the last 7 days`)}
      ${statCard(s.authors, 'Authors', `${s.active_sessions || 0} active sessions`)}
      ${statCard(s.messages_unread, 'Unread messages', `${s.subscribers || 0} subscribers`)}
    </div>

    <div class="grid g2">
      <div>
        ${review.length ? `
        <div class="card">
          <div class="card-hd"><h2>Waiting for review</h2><span class="pill p-warn">${review.length}</span></div>
          ${review.map(p => `
            <div class="list-item">
              <div class="li-main">
                <div class="t-title">${esc(p.title)}</div>
                <div class="t-sub">by ${esc(p.author_name)} · submitted ${fmtAgo(p.submitted_at)}</div>
              </div>
              <button class="btn btn-o btn-s" data-act="post:edit" data-id="${attr(p.id)}">Open</button>
              <button class="btn btn-g btn-s" data-act="post:approve" data-id="${attr(p.id)}">Approve</button>
              <button class="btn btn-o btn-s" data-act="post:reject" data-id="${attr(p.id)}">Send back</button>
            </div>`).join('')}
        </div>` : ''}

        <div class="card">
          <div class="card-hd"><h2>Recently edited</h2>
            <button class="btn btn-ghost btn-s" data-act="go" data-page="posts">See all →</button></div>
          ${(s.recent_posts || []).length ? (s.recent_posts || []).map(p => `
            <div class="list-item">
              <div class="li-main">
                <div class="t-title">${esc(p.title)}</div>
                <div class="t-sub">${esc(p.author_name)} · ${fmtAgo(p.ts)} · ${p.views || 0} views</div>
              </div>
              ${statusPill(p.status)}
              <button class="btn btn-o btn-s" data-act="post:edit" data-id="${attr(p.id)}">Edit</button>
            </div>`).join('') : `<p class="muted">No posts yet.</p>`}
        </div>
      </div>

      <div>
        <div class="card">
          <div class="card-hd"><h2>Most read</h2></div>
          ${(s.top_posts || []).length ? (s.top_posts || []).map((p, i) => `
            <div class="list-item">
              <strong style="color:var(--tx-3);width:18px">${i + 1}</strong>
              <div class="li-main"><div class="t-title">${esc(p.title)}</div></div>
              <span class="pill p-mute">${p.views} views</span>
            </div>`).join('') : `<p class="muted">Views are counted as soon as readers open your posts.</p>`}
        </div>

        <div class="card">
          <div class="card-hd"><h2>Library</h2></div>
          <div class="kv"><span>Categories</span><strong>${s.categories || 0}</strong></div>
          <div class="kv"><span>Subtopics</span><strong>${s.subtopics || 0}</strong></div>
          <div class="kv"><span>Downloads</span><strong>${s.downloads || 0}</strong></div>
          <div class="kv"><span>Glossary terms</span><strong>${s.glossary || 0}</strong></div>
          <div class="kv"><span>FAQs</span><strong>${s.faqs || 0}</strong></div>
          <div class="kv"><span>Words written</span><strong>${(s.words_total || 0).toLocaleString()}</strong></div>
        </div>

        <div class="card">
          <div class="card-hd"><h2>Latest activity</h2>
            <button class="btn btn-ghost btn-s" data-act="go" data-page="security">Audit log →</button></div>
          ${(s.activity || []).length ? (s.activity || []).map(a => `
            <div class="kv"><span>${esc(a.actor)} · ${esc(a.action.replace(/_/g, ' '))}
              ${a.entity_id ? `<em class="muted">${esc(a.entity_id)}</em>` : ''}</span>
              <span class="t-sub">${fmtAgo(a.created_at)}</span></div>`).join('')
            : `<p class="muted">Nothing logged yet.</p>`}
        </div>
      </div>
    </div>`;
}

function authorDash(s) {
  const profile = A.me.profile || {};
  const missing = ['avatar', 'bio', 'role', 'specialization'].filter(k => !profile[k]);
  return `
    <div class="page-head">
      <div><h1>Hello, ${esc((A.me.display_name || '').split(' ')[0] || A.me.username)} 👋</h1>
        <p>Your writing at a glance.</p></div>
      <div class="head-actions">
        <button class="btn btn-o" data-act="go" data-page="posts">My posts</button>
        <button class="btn btn-p" data-act="post:new">✎ New post</button>
      </div>
    </div>

    ${!A.me.has_password ? `<div class="alert alert-warn">
        Your account has no password yet — anyone with your username could sign in.
        <a href="#" data-act="security:password"><strong>Set one now</strong></a>.</div>` : ''}
    ${missing.length ? `<div class="alert alert-info">
        Your public profile is missing ${esc(missing.join(', '))}.
        <a href="#" data-act="go" data-page="profile"><strong>Complete your profile</strong></a> so readers get to know you.</div>` : ''}

    <div class="grid g3" style="margin-bottom:16px">
      ${statCard(s.posts_published, 'Published')}
      ${statCard(s.posts_draft, 'Drafts')}
      ${statCard(s.posts_review, 'In review')}
      ${statCard(s.posts_scheduled, 'Scheduled')}
      ${statCard(s.views_total, 'Total views', `${s.views_7d || 0} in the last 7 days`)}
      ${statCard((s.words_total || 0).toLocaleString(), 'Words written')}
    </div>

    <div class="grid g2">
      <div class="card">
        <div class="card-hd"><h2>Continue where you left off</h2>
          <button class="btn btn-ghost btn-s" data-act="go" data-page="posts">All →</button></div>
        ${(s.recent_posts || []).length ? (s.recent_posts || []).map(p => `
          <div class="list-item">
            <div class="li-main"><div class="t-title">${esc(p.title)}</div>
              <div class="t-sub">${fmtAgo(p.ts)} · ${p.views || 0} views</div></div>
            ${statusPill(p.status)}
            <button class="btn btn-o btn-s" data-act="post:edit" data-id="${attr(p.id)}">Edit</button>
          </div>`).join('') : `<p class="muted">You have not written anything yet. Hit <strong>New post</strong> to start.</p>`}
      </div>

      <div>
        <div class="card">
          <div class="card-hd"><h2>Your most read</h2></div>
          ${(s.top_posts || []).length ? (s.top_posts || []).map((p, i) => `
            <div class="list-item"><strong style="color:var(--tx-3);width:18px">${i + 1}</strong>
              <div class="li-main"><div class="t-title">${esc(p.title)}</div></div>
              <span class="pill p-mute">${p.views} views</span></div>`).join('')
            : `<p class="muted">No views recorded yet.</p>`}
        </div>
        <div class="card">
          <div class="card-hd"><h2>Publishing rules</h2></div>
          <div class="kv"><span>Publish without approval</span>
            <strong>${A.editorial.require_approval === true || A.editorial.authors_can_publish === false ? 'No — the admin reviews first' : 'Yes'}</strong></div>
          <div class="kv"><span>Schedule posts</span><strong>${A.editorial.authors_can_schedule === false ? 'Admin only' : 'Allowed'}</strong></div>
          <div class="kv"><span>Delete own posts</span><strong>${A.editorial.authors_can_delete === false ? 'Admin only' : 'Allowed'}</strong></div>
          <div class="kv"><span>Upload media</span><strong>${A.editorial.authors_can_upload === false ? 'Admin only' : 'Allowed'}</strong></div>
        </div>
      </div>
    </div>`;
}
