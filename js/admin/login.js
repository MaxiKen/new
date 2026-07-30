/* =====================================================================
   Admin Studio — sign-in screen
   Shown for every visit to the admin route until a valid session exists.
   ===================================================================== */

const Login = {
  busy: false,

  async show(notice) {
    const view = document.getElementById('login-view');
    view.style.display = '';
    document.getElementById('app-view').style.display = 'none';

    let setup = null;
    try { setup = await A.rpc('api_admin_status'); } catch (e) { /* offline / not installed */ }

    const lastUser = (() => { try { return localStorage.getItem('blog_studio_user') || ''; } catch (e) { return ''; } })();

    view.innerHTML = `
      <div class="login-wrap">
        <form class="login-card" id="login-form" autocomplete="on">
          <div class="login-brand">
            <div class="login-logo">✎</div>
            <h1>Studio sign in</h1>
            <p class="muted">Admins and authors manage the blog from here.</p>
          </div>

          ${notice ? `<div class="alert alert-warn">${esc(notice)}</div>` : ''}
          ${setup && setup.installed === false
            ? `<div class="alert alert-err">The database is not set up yet. Run <code>supabase-schema.sql</code> in the Supabase SQL editor, then reload.</div>`
            : ''}
          ${setup?.needs_setup
            ? `<div class="alert alert-info"><strong>First time here?</strong> Sign in with the username
               <code>admin</code> and an empty password — you will be asked to create one right after.</div>`
            : ''}

          <div class="fg">
            <label for="li-user">Username</label>
            <input class="fc" id="li-user" name="username" autocomplete="username" spellcheck="false"
                   placeholder="admin" value="${attr(lastUser)}" autofocus>
          </div>

          <div class="fg">
            <label for="li-pass">Password <span class="muted">— leave empty if none is set</span></label>
            <div class="pw-wrap">
              <input class="fc" id="li-pass" name="password" type="password" autocomplete="current-password"
                     placeholder="••••••••">
              <button type="button" class="pw-eye" id="li-eye" aria-label="Show password">👁</button>
            </div>
            <small class="muted" id="caps-hint" style="display:none;color:var(--warn)">Caps Lock is on</small>
          </div>

          <label class="check"><input type="checkbox" id="li-remember"> Keep me signed in on this device</label>

          <div class="alert alert-err" id="li-error" style="display:none"></div>

          <button class="btn btn-p btn-block" id="li-submit" type="submit">Sign in</button>

          <p class="login-foot">
            Accounts are created by the administrator.<br>
            Forgot your password? Ask the admin to clear it for you.
          </p>
        </form>
        <a class="login-back" href="index.html">← Back to the site</a>
      </div>`;

    const form = document.getElementById('login-form');
    const pass = document.getElementById('li-pass');

    form.addEventListener('submit', (e) => { e.preventDefault(); this.submit(); });
    document.getElementById('li-eye').addEventListener('click', () => {
      pass.type = pass.type === 'password' ? 'text' : 'password';
    });
    const caps = (e) => {
      const on = e.getModifierState && e.getModifierState('CapsLock');
      document.getElementById('caps-hint').style.display = on ? '' : 'none';
    };
    pass.addEventListener('keyup', caps);
    pass.addEventListener('keydown', caps);
  },

  error(msg) {
    const el = document.getElementById('li-error');
    el.innerHTML = msg;
    el.style.display = msg ? '' : 'none';
  },

  async submit() {
    if (this.busy) return;
    const username = val('li-user');
    const password = val('li-pass');
    const remember = checked('li-remember');
    if (!username) { this.error('Enter your username.'); document.getElementById('li-user').focus(); return; }

    this.busy = true;
    const btn = document.getElementById('li-submit');
    btn.disabled = true; btn.textContent = 'Signing in…';
    this.error('');

    try {
      const r = await A.rpc('api_login', {
        p_username: username,
        p_password: password || null,
        p_remember: remember,
        p_agent: navigator.userAgent
      });

      if (!r?.ok) {
        this.error(esc(r?.message || 'Sign in failed.'));
        if (r?.password_required) document.getElementById('li-pass').focus();
        return;
      }

      try { localStorage.setItem('blog_studio_user', username); } catch (e) {}
      Session.save(r.token, remember, r.expires_at);
      A.token = r.token;

      const session = await A.rpc('api_session', { p_token: r.token });
      await A.startApp(session);

      if (r.no_password) {
        setTimeout(() => Security.passwordDialog({
          first: true,
          admin: r.account?.role === 'admin'
        }), 400);
      }
    } catch (e) {
      this.error(esc(e.message || 'Could not reach the server.'));
    } finally {
      this.busy = false;
      btn.disabled = false; btn.textContent = 'Sign in';
    }
  }
};
