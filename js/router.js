// Blog Template - Router
const Router = {
  routes: {},
  current: '/',
  history: [],
  
  init() {
    window.addEventListener('hashchange', () => this.handle());
    window.addEventListener('popstate', (e) => { if (e.state?.route) this.go(e.state.route, false); });
    this.handle();
  },
  
  register(path, fn) { this.routes[path] = fn; },
  
  go(path, push = true) {
    if (this.current) Store.setScroll(this.current, window.scrollY);
    if (push) { window.history.pushState({ route: path }, '', '#' + path); this.history.push(this.current); }
    this.current = path;
    this.handle(path, push);
  },
  
  handle(path, push) {
    path = path || window.location.hash.slice(1) || '/';
    const { route, params } = this.parse(path);
    const fn = this.routes[route];
    if (fn) {
      try { fn(params); } catch (e) { console.error('[Router]', e); }
      const saved = Store.getScroll(path);
      if (saved && !push) setTimeout(() => window.scrollTo(0, saved), 50);
      else window.scrollTo(0, 0);
    } else {
      const el = document.getElementById('main-content');
      if (el) el.innerHTML = '<div class="container" style="padding:100px 0;text-align:center"><h1 style="font-size:4rem;color:var(--primary)">404</h1><h2>Page Not Found</h2><p style="margin:16px 0 32px;color:var(--text-secondary)"><a href="#/" class="btn btn-primary" style="color:#fff;text-decoration:none">Go Home</a></p></div>';
    }
  },
  
  parse(path) {
    const parts = path.split('/').filter(Boolean);
    const params = {};
    if (!parts.length) return { route: '/', params };
    
    // Subtopic: /cat/:id/sub/:id
    if (parts[0] === 'cat' && parts.length >= 4 && parts[2] === 'sub') {
      params.cat = parts[1]; params.sub = parts[3];
      return { route: '/cat/:cat/sub/:sub', params };
    }
    // Category: /cat/:id
    if (parts[0] === 'cat' && parts.length >= 2) {
      params.cat = parts[1];
      return { route: '/cat/:cat', params };
    }
    // Post: /post/:id
    if (parts[0] === 'post' && parts.length >= 2) {
      params.id = parts[1];
      return { route: '/post/:id', params };
    }
    // Author: /author/:id
    if (parts[0] === 'author' && parts.length >= 2) {
      params.id = parts[1];
      return { route: '/author/:id', params };
    }
    // Static pages
    if (['about', 'glossary', 'faqs', 'downloads', 'search'].includes(parts[0])) {
      return { route: '/' + parts[0], params };
    }
    return { route: '/', params };
  }
};