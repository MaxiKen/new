/* =====================================================================
   Admin Studio — passwords, sessions, audit log and access policies
   Passwords can be set, changed or removed at any time for both the
   admin and every author.
   ===================================================================== */

const Security = {
  /* ---------------- password dialog ---------------- */
  /**
   * opts.target  account object {id, username, has_password}  -> admin acting on someone else
   * opts.name    display name of that person
   * opts.first   friendly first-run wording
   */
  passwordDialog(opts = {}) {
    const self = !opts.target || opts.target.id === A.me.id;
    const has = self ? A.me.has_password : !!opts.target.has_password;
    const who = self ? 'your account' : esc(opts.name || opts.target.username);

    openModal(`
      <h2>${has ? 'Change password' : 'Set a password'}</h2>
      <p class="muted" style="font-size:.83rem">
        ${opts.first
          ? 'Right now anyone who knows the username can sign in. Add a password to lock the studio down — you can remove it again whenever you like.'
          : `Password for ${who}. Leaving it empty means signing in without a password.`}
      </p>

      ${self && has ? `<div class="fg" style="margin-top:16px"><label>Current password</label>
        <input class="fc" id="pw-cur" type="password" autocomplete="current-password" autofocus></div>` : ''}

      <div class="fg" style="${self && has ? '' : 'margin-top:16px'}"><label>New password</label>
        <div class="pw-wrap">
          <input class="fc" id="pw-new" type="password" autocomplete="new-password" ${self && has ? '' : 'autofocus'}>
          <button type="button" class="pw-eye" data-act="security:eye">👁</button>
        </div>
        <div class="hint" id="pw-meter">At least 6 characters. A short phrase works well.</div>
      </div>

      <div class="fg"><label>Repeat new password</label>
        <input class="fc" id="pw-new2" type="password" autocomplete="new-password"></div>

      <label class="check"><input type="checkbox" id="pw-revoke" checked>
        Sign ${self ? 'my' : 'their'} other devices out</label>

      <div class="m-act">
        ${has ? `<button class="btn btn-o" data-act="security:remove-pass"
                   data-target="${attr(opts.target?.id || '')}" style="margin-right:auto">Remove password</button>` : ''}
        <button class="btn btn-o" data-act="modal:close">${opts.first ? 'Later' : 'Cancel'}</button>
        <button class="btn btn-p" data-act="security:save-pass" data-target="${attr(opts.target?.id || '')}">Save password</button>
      </div>`, { small: true });

    document.getElementById('pw-new').addEventListener('input', (e) => {
      const v = e.target.value;
      const score = (v.length >= 8) + (v.length >= 12) + /[A-Z]/.test(v) + /[0-9]/.test(v) + /[^A-Za-z0-9]/.test(v);
      const labels = ['Too short', 'Weak', 'Fair', 'Good', 'Strong', 'Excellent'];
      const colors = ['var(--err)', 'var(--err)', 'var(--warn)', 'var(--info)', 'var(--ok)', 'var(--ok)'];
      const el = document.getElementById('pw-meter');
      if (!v) { el.textContent = 'At least 6 characters. A short phrase works well.'; el.style.color = ''; return; }
      el.textContent = labels[Math.min(score, 5)];
      el.style.color = colors[Math.min(score, 5)];
    });
  },

  async savePassword(targetId) {
    const nw = val('pw-new'), nw2 = val('pw-new2');
    if (!nw) { toast('Type the new password', 'err'); return; }
    if (nw !== nw2) { toast('The two passwords do not match', 'err'); return; }
    if (nw.length < 6) { toast('Use at least 6 characters', 'err'); return; }

    const revoke = checked('pw-revoke');
    const r = targetId
      ? await A.act('api_admin_set_password', { p_account_id: targetId, p_new: nw, p_revoke: revoke })
      : await A.act('api_set_password', { p_current: val('pw-cur') || null, p_new: nw, p_revoke_others: revoke });
    if (!r) return;
    closeModal();
    await this.afterAccountChange(targetId);
  },

  async removePassword(targetId) {
    const ok = await confirmDialog({
      title: 'Remove the password?', okLabel: 'Remove it', danger: true,
      body: `<p>Sign-in will only ask for the username. You can set a new password at any time.</p>`
    });
    if (!ok) return;
    const cur = val('pw-cur');
    const r = targetId
      ? await A.act('api_admin_set_password', { p_account_id: targetId, p_new: null })
      : await A.act('api_set_password', { p_current: cur || null, p_new: null });
    if (!r) return;
    closeModal();
    await this.afterAccountChange(targetId);
  },

  async afterAccountChange(targetId) {
    const s = await A.call('api_session');
    A.me = s.account;
    document.getElementById('nopass-banner').style.display = A.me.has_password ? 'none' : '';
    if (A.page === 'security' || A.page === 'authors') A.go(A.page);
  },

  /* ---------------- sessions ---------------- */
  async sessionsDialog(accountId, name) {
    const rows = await A.list('sessions', accountId ? { account_id: accountId } : {});
    openModal(`<h2>Active sessions${name ? ' · ' + esc(name) : ''}</h2>
      <p class="muted" style="font-size:.8rem">Every browser that is currently signed in.</p>
      <div style="margin-top:14px">
        ${rows.length ? rows.map(s => `
          <div class="list-item">
            <div class="li-main">
              <div class="t-title">${esc(deviceLabel(s.user_agent))} ${s.current ? '<span class="pill p-ok">this device</span>' : ''}</div>
              <div class="t-sub">${esc(s.ip || 'unknown IP')} · started ${fmtDate(s.created_at, true)} ·
                last used ${fmtAgo(s.last_seen_at)} · expires ${fmtDate(s.expires_at, true)}</div>
            </div>
            ${s.current ? '' : `<button class="btn btn-o btn-s" data-act="security:revoke" data-id="${attr(s.id)}"
              data-account="${attr(accountId || '')}">Sign out</button>`}
          </div>`).join('') : '<p class="muted">No active sessions.</p>'}
      </div>
      <div class="m-act">
        <button class="btn btn-o" data-act="security:revoke-all" data-account="${attr(accountId || '')}"
          style="margin-right:auto">Sign out everywhere else</button>
        <button class="btn btn-p" data-act="modal:close">Done</button>
      </div>`, {});
  }
};

function deviceLabel(ua) {
  if (!ua) return 'Unknown device';
  const os = /Windows/.test(ua) ? 'Windows' : /Android/.test(ua) ? 'Android'
    : /iPhone|iPad/.test(ua) ? 'iOS' : /Mac OS X/.test(ua) ? 'macOS' : /Linux/.test(ua) ? 'Linux' : 'Device';
  const br = /Edg\//.test(ua) ? 'Edge' : /OPR\//.test(ua) ? 'Opera' : /Chrome\//.test(ua) ? 'Chrome'
    : /Safari\//.test(ua) ? 'Safari' : /Firefox\//.test(ua) ? 'Firefox' : 'Browser';
  return `${br} on ${os}`;
}

A.on('security:password', () => Security.passwordDialog({}));
A.on('security:save-pass', (d) => Security.savePassword(d.target || null));
A.on('security:remove-pass', (d) => Security.removePassword(d.target || null));
A.on('security:eye', (d, el) => {
  const i = document.getElementById('pw-new');
  i.type = i.type === 'password' ? 'text' : 'password';
});
A.on('security:sessions', (d) => Security.sessionsDialog(d.account || null, d.name));
A.on('security:revoke', async (d) => {
  await A.act('api_revoke_session', { p_session_id: d.id });
  Security.sessionsDialog(d.account || null);
});
A.on('security:revoke-all', async (d) => {
  const ok = await confirmDialog({
    title: 'Sign out every other device?', okLabel: 'Sign them out',
    body: '<p>This session stays signed in.</p>'
  });
  if (!ok) return;
  await A.act('api_revoke_all_sessions', { p_account_id: d.account || null });
  closeModal();
});

/* =====================================================================
   Security page
   ===================================================================== */
Pages.security = async function (params, el) {
  const [sessions, audit] = await Promise.all([
    A.list('sessions'),
    A.list('audit', { limit: 200 }).catch(() => [])
  ]);
  const accounts = A.isAdmin ? await A.list('accounts') : [];
  const cfg = A.isAdmin ? await A.get('settings') : null;

  el.innerHTML = `
    <div class="page-head">
      <div><h1>Security</h1><p>Passwords, devices and — for the admin — who may do what.</p></div>
    </div>

    <div class="grid g2">
      <div class="card">
        <div class="card-hd"><h2>Your account</h2>${A.isAdmin ? '<span class="pill p-info">Administrator</span>' : '<span class="pill p-mute">Author</span>'}</div>
        <div class="kv"><span>Username</span><strong>@${esc(A.me.username)}</strong></div>
        <div class="kv"><span>Password</span>
          <strong>${A.me.has_password
            ? `Set <span class="muted">· ${fmtAgo(A.me.password_set_at)}</span>`
            : '<span class="pill p-warn">none — anyone with your username can sign in</span>'}</strong></div>
        <div class="kv"><span>Last sign-in</span><span>${fmtDate(A.me.last_login_at, true)}</span></div>
        <div class="kv"><span>Total sign-ins</span><span>${A.me.login_count || 0}</span></div>
        <div class="row" style="margin-top:14px">
          <button class="btn btn-p" data-act="security:password">
            ${A.me.has_password ? 'Change password' : 'Set a password'}</button>
          <button class="btn btn-o" data-act="security:sessions">Manage devices (${sessions.length})</button>
        </div>
        ${A.me.username === 'admin' ? `<div class="hint" style="margin-top:10px">
          The admin username is fixed and cannot be renamed or deleted.</div>` : ''}
      </div>

      <div class="card">
        <div class="card-hd"><h2>Signed-in devices</h2></div>
        ${sessions.map(s => `<div class="list-item">
            <div class="li-main"><div class="t-title">${esc(deviceLabel(s.user_agent))}
              ${s.current ? '<span class="pill p-ok">this device</span>' : ''}</div>
              <div class="t-sub">${esc(s.ip || 'unknown IP')} · last used ${fmtAgo(s.last_seen_at)}</div></div>
            ${s.current ? '' : `<button class="btn btn-o btn-s" data-act="security:revoke" data-id="${attr(s.id)}">Sign out</button>`}
          </div>`).join('') || '<p class="muted">No other devices.</p>'}
      </div>
    </div>

    ${A.isAdmin ? adminSecurity(accounts, cfg) : ''}

    <div class="card">
      <div class="card-hd"><h2>${A.isAdmin ? 'Audit log' : 'Your recent activity'}</h2>
        ${A.isAdmin ? '<div class="search-box"><input class="fc" id="au-q" placeholder="Filter…"></div>' : ''}</div>
      <div class="t-wrap"><table>
        <thead><tr><th>When</th>${A.isAdmin ? '<th>Who</th>' : ''}<th>Action</th><th>Item</th><th>Details</th></tr></thead>
        <tbody id="audit-body">${auditRows(audit)}</tbody>
      </table></div>
    </div>`;

  document.getElementById('au-q')?.addEventListener('input', debounce((e) => {
    const q = e.target.value.toLowerCase();
    document.getElementById('audit-body').innerHTML = auditRows(audit.filter(a =>
      JSON.stringify(a).toLowerCase().includes(q)));
  }, 200));
};

function auditRows(rows) {
  if (!rows.length) return emptyRow(5, 'Nothing logged yet.');
  return rows.map(a => `<tr>
    <td class="nowrap t-sub">${fmtDate(a.created_at, true)}</td>
    ${A.isAdmin ? `<td class="nowrap">${esc(a.actor || '—')}
      <div class="t-sub">${esc(a.actor_role || '')}</div></td>` : ''}
    <td>${actionPill(a.action)}</td>
    <td class="t-sub">${esc(a.entity || '')}${a.entity_id ? ' · ' + esc(a.entity_id) : ''}</td>
    <td class="t-sub">${esc(shortDetail(a.detail))}</td>
  </tr>`).join('');
}
function actionPill(action) {
  const danger = /delete|removed|failed|disabled|revoked/.test(action);
  const good = /created|published|login|approve|saved|set/.test(action);
  const cls = danger ? 'p-err' : good ? 'p-ok' : 'p-mute';
  return `<span class="pill ${cls}">${esc(String(action).replace(/_/g, ' '))}</span>`;
}
function shortDetail(d) {
  if (!d || typeof d !== 'object') return '';
  const s = Object.entries(d).filter(([, v]) => v !== null && v !== '' && v !== false)
    .map(([k, v]) => `${k}: ${typeof v === 'object' ? JSON.stringify(v) : v}`).join(' · ');
  return s.length > 90 ? s.slice(0, 90) + '…' : s;
}

function adminSecurity(accounts, cfg) {
  const ed = cfg?.editorial || {}, sec = cfg?.security || {};
  return `
    <div class="card pad0">
      <div style="padding:18px 18px 0"><div class="card-hd"><h2>All accounts</h2>
        <p class="muted">Set or clear passwords for anyone. Removing a password lets that person sign in with just their username.</p></div></div>
      <div class="t-wrap"><table>
        <thead><tr><th>Account</th><th>Role</th><th>Password</th><th>Status</th><th>Last sign-in</th><th>Devices</th><th></th></tr></thead>
        <tbody>${accounts.map(ac => {
          const locked = ac.locked_until && new Date(ac.locked_until) > new Date();
          return `<tr>
            <td><div class="t-title">${esc(ac.display_name)}</div><div class="t-sub">@${esc(ac.username)}</div></td>
            <td>${ac.role === 'admin' ? '<span class="pill p-info">Admin</span>' : '<span class="pill p-mute">Author</span>'}</td>
            <td>${ac.has_password ? '<span class="pill p-ok">set</span>' : '<span class="pill p-warn">none</span>'}</td>
            <td>${ac.is_active === false ? '<span class="pill p-err">disabled</span>'
                 : locked ? '<span class="pill p-warn">locked</span>' : '<span class="pill p-ok">active</span>'}</td>
            <td class="t-sub nowrap">${fmtAgo(ac.last_login_at)}</td>
            <td class="t-sub">${ac.active_sessions || 0}</td>
            <td><div class="t-actions">
              <button class="btn btn-o btn-s" data-act="security:acc-pass" data-id="${attr(ac.id)}"
                data-name="${attr(ac.display_name)}" data-has="${ac.has_password ? '1' : ''}">Password</button>
              <button class="btn btn-o btn-s" data-act="security:sessions" data-account="${attr(ac.id)}"
                data-name="${attr(ac.display_name)}">Devices</button>
            </div></td>
          </tr>`;
        }).join('')}</tbody>
      </table></div>
    </div>

    <div class="grid g2">
      <div class="card">
        <div class="card-hd"><h2>What authors may do</h2></div>
        <label class="switch"><input type="checkbox" id="ed-approve" ${ed.require_approval ? 'checked' : ''}>
          <span class="sw-txt">Review posts before they go live<small>Authors submit, you approve</small></span></label>
        <label class="switch"><input type="checkbox" id="ed-publish" ${ed.authors_can_publish !== false ? 'checked' : ''}>
          <span class="sw-txt">Authors can publish<small>Turn off to force the review queue</small></span></label>
        <label class="switch"><input type="checkbox" id="ed-schedule" ${ed.authors_can_schedule !== false ? 'checked' : ''}>
          <span class="sw-txt">Authors can schedule posts<small>Pick a future date and time</small></span></label>
        <label class="switch"><input type="checkbox" id="ed-delete" ${ed.authors_can_delete !== false ? 'checked' : ''}>
          <span class="sw-txt">Authors can delete their posts<small>Otherwise only you can</small></span></label>
        <label class="switch"><input type="checkbox" id="ed-upload" ${ed.authors_can_upload !== false ? 'checked' : ''}>
          <span class="sw-txt">Authors can upload media<small>Images inside their posts</small></span></label>
        <button class="btn btn-p" style="margin-top:12px" data-act="security:save-policy">Save rules</button>
      </div>

      <div class="card">
        <div class="card-hd"><h2>Sign-in policy</h2></div>
        <div class="row">
          <div class="fg"><label>Session length (hours)</label>
            <input class="fc" type="number" min="1" max="720" id="sec-hours" value="${sec.session_hours ?? 12}"></div>
          <div class="fg"><label>"Keep me signed in" (days)</label>
            <input class="fc" type="number" min="1" max="365" id="sec-days" value="${sec.remember_days ?? 30}"></div>
        </div>
        <div class="row">
          <div class="fg"><label>Failed attempts before lock</label>
            <input class="fc" type="number" min="3" max="50" id="sec-att" value="${sec.max_attempts ?? 8}"></div>
          <div class="fg"><label>Lock duration (minutes)</label>
            <input class="fc" type="number" min="1" max="1440" id="sec-lock" value="${sec.lockout_minutes ?? 15}"></div>
        </div>
        <div class="fg"><label>Minimum password length</label>
          <input class="fc" type="number" min="4" max="64" id="sec-min" value="${sec.min_password_length ?? 6}"></div>
        <label class="switch"><input type="checkbox" id="sec-nopass" ${sec.allow_passwordless !== false ? 'checked' : ''}>
          <span class="sw-txt">Allow accounts without a password<small>Turn off to require a password for everyone</small></span></label>
        <button class="btn btn-p" style="margin-top:12px" data-act="security:save-policy">Save policy</button>
      </div>
    </div>`;
}

A.on('security:acc-pass', (d) => Security.passwordDialog({
  target: { id: d.id, has_password: !!d.has, username: d.name }, name: d.name
}));

A.on('security:save-policy', async () => {
  const r = await A.act('api_save_settings', {
    p_data: {
      editorial: {
        require_approval: checked('ed-approve'),
        authors_can_publish: checked('ed-publish'),
        authors_can_schedule: checked('ed-schedule'),
        authors_can_delete: checked('ed-delete'),
        authors_can_upload: checked('ed-upload')
      },
      security: {
        session_hours: Number(val('sec-hours') || 12),
        remember_days: Number(val('sec-days') || 30),
        max_attempts: Number(val('sec-att') || 8),
        lockout_minutes: Number(val('sec-lock') || 15),
        min_password_length: Number(val('sec-min') || 6),
        allow_passwordless: checked('sec-nopass')
      }
    }
  }, 'Rules saved');
  if (r) {
    const s = await A.call('api_session');
    A.editorial = s.editorial || {};
  }
});
