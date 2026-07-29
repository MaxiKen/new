// Blog Template - Main Application
const App = {
  async init() {
    try {
      DB.init();
      await new Promise(r => {
        if (DB.ready) return r();
        const t = setTimeout(r, 3000);
        window.addEventListener('db-ready', () => { clearTimeout(t); r(); }, { once: true });
      });
      await Content.init();
      this.applySettings();
      this.applyTheme(Store.getTheme() || 'light');
      this.setupEvents();
      this.registerRoutes();
      Router.init();
      this.renderNav();
      this.renderFooter();
      this.hideLoader();
    } catch (e) { console.error('[App]', e); this.hideLoader(); }
  },
  
  // Apply all settings to the page
  applySettings() {
    const site = Content.getSite();
    const seo = Content.getSEO();
    
    // Update page title
    document.title = seo.title || site.name || 'Blog';
    
    // Update site name in header
    const nameEl = document.getElementById('site-name');
    if (nameEl && site.name) {
      const parts = site.name.split(' ');
      if (parts.length > 1) {
        nameEl.innerHTML = parts.slice(0, -1).join(' ') + ' <span>' + parts[parts.length - 1] + '</span>';
      } else {
        nameEl.innerHTML = site.name;
      }
    }
    
    // Update loading screen text
    const lsText = document.getElementById('ls-text');
    if (lsText && site.name) lsText.innerHTML = site.name.replace(/(\S+)$/, '<span>$1</span>');
    
    // Update favicon
    if (site.favicon) {
      let link = document.querySelector("link[rel~='icon']");
      if (!link) { link = document.createElement('link'); link.rel = 'icon'; document.head.appendChild(link); }
      link.href = site.favicon;
    }
    
    // Update logo image
    const logoImg = document.getElementById('site-logo');
    if (logoImg && site.logo) { logoImg.src = site.logo; logoImg.alt = site.name || ''; logoImg.style.display = 'block'; }
    
    // Update meta description
    const metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc) metaDesc.setAttribute('content', seo.description || site.description || '');
    
    // Update OG tags
    const ogTitle = document.querySelector('meta[property="og:title"]');
    if (ogTitle) ogTitle.setAttribute('content', site.name || '');
    const ogDesc = document.querySelector('meta[property="og:description"]');
    if (ogDesc) ogDesc.setAttribute('content', site.description || '');
  },
  
  // ===== THEME =====
  applyTheme(t) {
    const themes = Content.getThemes();
    const colors = themes[t] || themes.light || {};
    document.documentElement.setAttribute('data-theme', t);
    Store.setTheme(t);
    const root = document.documentElement;
    Object.entries(colors).forEach(([k, v]) => { if (v) root.style.setProperty('--' + k.replace(/_/g, '-'), v); });
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', colors.primary || '#3b82f6');
  },
  
  toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    const next = current === 'light' ? 'dark' : 'light';
    this.applyTheme(next);
    this.toast('Theme: ' + (next === 'dark' ? 'Dark' : 'Light'));
  },
  
  // ===== EVENTS =====
  setupEvents() {
    document.getElementById('menu-toggle')?.addEventListener('click', () => this.toggleSidebar());
    document.getElementById('sidebar-close')?.addEventListener('click', () => this.closeSidebar());
    document.getElementById('sidebar-overlay')?.addEventListener('click', () => this.closeSidebar());
    document.getElementById('search-btn')?.addEventListener('click', () => this.openSearch());
    document.getElementById('search-close')?.addEventListener('click', () => this.closeSearch());
    document.getElementById('search-input')?.addEventListener('input', (e) => this.doSearch(e.target.value));
    document.getElementById('theme-toggle')?.addEventListener('click', () => this.toggleTheme());
    document.getElementById('fab-contact')?.addEventListener('click', () => this.toggleContact());
    document.getElementById('contact-close')?.addEventListener('click', () => this.closeContact());
    document.getElementById('contact-form')?.addEventListener('submit', (e) => { e.preventDefault(); this.sendContact(e.target); });
    document.getElementById('newsletter-form')?.addEventListener('submit', (e) => { e.preventDefault(); this.sendNewsletter(e.target); });
    document.getElementById('back-to-top')?.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
    window.addEventListener('scroll', () => { const b = document.getElementById('back-to-top'); if (b) b.classList.toggle('visible', window.scrollY > 300); });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { this.closeSearch(); this.closeContact(); this.closeSidebar(); }
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); this.openSearch(); }
    });
    // Pull to refresh
    let sy = 0, pulling = false;
    const main = document.getElementById('main-content');
    if (main) {
      main.addEventListener('touchstart', (e) => { if (window.scrollY === 0) { sy = e.touches[0].pageY; pulling = true; } });
      main.addEventListener('touchmove', (e) => { if (pulling && e.touches[0].pageY - sy > 100) document.getElementById('pull-to-refresh')?.classList.add('active'); });
      main.addEventListener('touchend', async () => {
        const ptr = document.getElementById('pull-to-refresh');
        if (ptr?.classList.contains('active')) {
          this.toast('Refreshing...');
          await Content.init();
          this.renderNav(); this.renderFooter();
          Router.handle();
          ptr.classList.remove('active');
          this.toast('Updated!');
        }
        pulling = false;
      });
    }
    // Connectivity
    const banner = document.getElementById('offline-banner');
    window.addEventListener('online', () => { banner?.classList.remove('visible'); this.toast('Back online!'); });
    window.addEventListener('offline', () => { banner?.classList.add('visible'); });
    if (!navigator.onLine) banner?.classList.add('visible');
    // SW
    if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(() => {});
  },
  
  // ===== ROUTES =====
  registerRoutes() {
    Router.register('/', () => this.renderHome());
    Router.register('/post/:id', (p) => this.renderPost(p.id));
    Router.register('/cat/:cat', (p) => this.renderCategory(p.cat));
    Router.register('/cat/:cat/sub/:sub', (p) => this.renderSubtopic(p.cat, p.sub));
    Router.register('/author/:id', (p) => this.renderAuthorPage(p.id));
    Router.register('/about', () => this.renderAbout());
    Router.register('/glossary', () => this.renderGlossary());
    Router.register('/faqs', () => this.renderFAQs());
    Router.register('/downloads', () => this.renderDownloads());
    Router.register('/search', () => this.renderSearchPage());
  },
  
  // ===== NAVIGATION =====
  renderNav() {
    const nav = document.getElementById('nav-menu');
    const desktop = document.getElementById('desktop-nav');
    if (!nav) return;
    const cats = Content.getVisibleCategories();
    let html = '';
    cats.forEach(cat => {
      const subs = Content.getVisibleSubtopics(cat.id);
      const isSpecial = ['downloads', 'glossary', 'faqs', 'about'].includes(cat.type);
      if (isSpecial || subs.length === 0) {
        const route = cat.type === 'about' ? '/about' : cat.type === 'downloads' ? '/downloads' : cat.type === 'glossary' ? '/glossary' : cat.type === 'faqs' ? '/faqs' : '/cat/' + cat.id;
        html += '<div class="nav-item"><div class="nav-item-header" onclick="App.go(\'' + route + '\')" style="cursor:pointer"><div class="nav-item-header-left"><div class="nav-item-icon">' + this.icon(cat.icon) + '</div><div class="nav-item-title">' + cat.title + '</div></div></div></div>';
      } else {
        html += '<div class="nav-item"><div class="nav-item-header" onclick="App.toggleNav(this)"><div class="nav-item-header-left"><div class="nav-item-icon">' + this.icon(cat.icon) + '</div><div class="nav-item-title">' + cat.title + '</div></div><div class="nav-item-arrow">' + this.icon('chevron-down') + '</div></div><div class="nav-submenu"><a class="nav-submenu-item" onclick="App.go(\'/cat/' + cat.id + '\')">All ' + cat.title + '</a>' + subs.map(s => '<a class="nav-submenu-item" onclick="App.go(\'/cat/' + cat.id + '/sub/' + s.id + '\')">' + s.title + '</a>').join('') + '</div></div>';
      }
    });
    nav.innerHTML = html;
    if (desktop) {
      let dh = '';
      cats.forEach(cat => {
        const subs = Content.getVisibleSubtopics(cat.id);
        const isSpecial = ['downloads', 'glossary', 'faqs', 'about'].includes(cat.type);
        if (isSpecial || subs.length === 0) {
          const route = cat.type === 'about' ? '/about' : cat.type === 'downloads' ? '/downloads' : cat.type === 'glossary' ? '/glossary' : cat.type === 'faqs' ? '/faqs' : '/cat/' + cat.id;
          dh += '<div class="desktop-nav-item"><a class="desktop-nav-link" onclick="App.go(\'' + route + '\')">' + cat.title + '</a></div>';
        } else {
          dh += '<div class="desktop-nav-item"><a class="desktop-nav-link" onclick="App.go(\'/cat/' + cat.id + '\')">' + cat.title + this.icon('chevron-down') + '</a><div class="desktop-dropdown">' + subs.map(s => '<a class="desktop-dropdown-item" onclick="App.go(\'/cat/' + cat.id + '/sub/' + s.id + '\')">' + s.title + '</a>').join('') + '</div></div>';
        }
      });
      desktop.innerHTML = dh;
    }
  },
  
  // ===== FOOTER =====
  renderFooter() {
    const footer = document.getElementById('footer');
    if (!footer) return;
    const site = Content.getSite();
    const footerData = Content.getFooter();
    const contact = Content.getContact();
    const cats = Content.getVisibleCategories().filter(c => !['about'].includes(c.type));
    
    // Contact info HTML
    const contactHtml = contact.email ? '<p style="color:rgba(255,255,255,0.8);margin-bottom:8px;font-size:0.9rem">' + this.icon('mail') + ' <a href="mailto:' + contact.email + '" style="color:rgba(255,255,255,0.8)">' + contact.email + '</a></p>' : '';
    
    footer.innerHTML = '<div class="container"><div class="footer-grid">' +
      // About section
      '<div class="footer-section"><h3 class="footer-section-title">' + (site.name || 'Blog') + '</h3>' +
      '<p style="color:rgba(255,255,255,0.8);margin-bottom:16px;line-height:1.6">' + (site.description || '') + '</p>' +
      contactHtml +
      '</div>' +
      // Quick Links
      '<div class="footer-section"><h3 class="footer-section-title">Quick Links</h3><div class="footer-links">' +
      '<a href="#/" class="footer-link" onclick="App.go(\'/\')">Home</a>' +
      '<a href="#/about" class="footer-link" onclick="App.go(\'/about\')">About</a>' +
      '<a href="#/glossary" class="footer-link" onclick="App.go(\'/glossary\')">Glossary</a>' +
      '<a href="#/faqs" class="footer-link" onclick="App.go(\'/faqs\')">FAQs</a>' +
      '<a href="#/downloads" class="footer-link" onclick="App.go(\'/downloads\')">Downloads</a>' +
      '</div></div>' +
      // Categories
      '<div class="footer-section"><h3 class="footer-section-title">Categories</h3><div class="footer-links">' +
      cats.map(c => '<a href="#/cat/' + c.id + '" class="footer-link" onclick="App.go(\'/cat/' + c.id + '\')">' + c.title + '</a>').join('') +
      '</div></div>' +
      // Newsletter
      '<div class="footer-section"><h3 class="footer-section-title">Newsletter</h3>' +
      '<p class="footer-newsletter-text">Subscribe for updates.</p>' +
      '<form class="footer-newsletter-form" id="newsletter-form" onsubmit="App.sendNewsletter(event);return false">' +
      '<input type="text" class="footer-newsletter-input" placeholder="Name" name="name" required>' +
      '<input type="email" class="footer-newsletter-input" placeholder="Email" name="email" required>' +
      '<button type="submit" class="footer-newsletter-btn">Subscribe</button></form></div>' +
      '</div>' +
      '<div class="footer-bottom"><p class="footer-copyright">' + (footerData.copyright || '') + '</p></div></div>';
  },
  
  // ===== PAGES =====
  renderHome() {
    const el = document.getElementById('main-content');
    if (!el) return;
    const site = Content.getSite();
    const featured = Content.getFeaturedPosts();
    // Filter out special category posts from recent
    const specialTypes = ['downloads', 'glossary', 'faqs', 'about'];
    const recent = Content.getRecentPosts(50).filter(p => {
      const cat = Content.getCategory(p.category);
      return cat && !specialTypes.includes(cat.type);
    }).slice(0, 9);
    const cats = Content.getVisibleCategories().filter(c => !specialTypes.includes(c.type));
    const heroStyle = site.hero_image ? ' style="background-image:url(\'' + site.hero_image + '\')"' : '';
    let html = '<section class="hero"' + heroStyle + '><div class="hero-content"><h1 class="hero-title">' + (site.hero_title || 'Welcome') + '</h1><p class="hero-subtitle">' + (site.hero_subtitle || '') + '</p><div class="hero-search"><input type="text" class="hero-search-input" placeholder="Search articles..." id="hero-search"><button class="hero-search-btn" onclick="App.heroSearch()">Search</button></div></div></section>';
    if (featured.length) {
      html += '<section class="section"><div class="container"><div class="section-header"><h2 class="section-title">Featured</h2></div><div class="posts-grid">' + featured.map((p, i) => this.card(p, i === 0)).join('') + '</div></div></section>';
    }
    html += '<section class="section" style="background:var(--background-alt)"><div class="container"><div class="section-header"><h2 class="section-title">Latest Articles</h2></div><div class="category-filter"><button class="category-filter-btn active" onclick="App.filterHome(\'all\',this)">All</button>' + cats.map(c => '<button class="category-filter-btn" onclick="App.filterHome(\'' + c.id + '\',this)">' + c.title + '</button>').join('') + '</div><div class="posts-grid" id="home-posts">' + recent.map(p => this.card(p)).join('') + '</div></div></section>';
    el.innerHTML = html;
    document.getElementById('hero-search')?.addEventListener('keypress', (e) => { if (e.key === 'Enter') App.heroSearch(); });
  },
  
  card(post, featured) {
    const cat = Content.getCategory(post.category);
    const author = Content.getAuthor(post.author);
    const rt = Content.calcReadTime(post);
    return '<article class="post-card' + (featured ? ' featured-post' : '') + '" onclick="App.go(\'/post/' + post.id + '\')"><div class="post-card-image"><img src="' + (post.featured_image || '') + '" alt="' + (post.featured_image_alt || post.title) + '" loading="lazy" onerror="this.style.display=\'none\'"><span class="post-card-category">' + (cat?.title || post.category) + '</span></div><div class="post-card-content"><div class="post-card-meta"><span>' + Content.fmtDate(post.published_date) + '</span><span>' + rt + '</span></div><h3 class="post-card-title">' + post.title + '</h3><p class="post-card-excerpt">' + (post.excerpt || '') + '</p><div class="post-card-footer"><div class="post-card-author"><div class="post-card-author-avatar">' + Content.initials(author?.name) + '</div><span class="post-card-author-name" onclick="event.stopPropagation();App.go(\'/author/' + post.author + '\')">' + (author?.name || '') + '</span></div><span class="post-card-reading-time">' + rt + '</span></div></div></article>';
  },
  
  renderPost(id) {
    const post = Content.getPost(id);
    if (!post) { Router.handle(); return; }
    const el = document.getElementById('main-content');
    if (!el) return;
    const cat = Content.getCategory(post.category);
    const sub = post.subtopic ? Content.getSubtopic(post.subtopic) : null;
    const author = Content.getAuthor(post.author);
    const rt = Content.calcReadTime(post);
    const related = Content.getRelatedPosts(post.id, 3);
    Store.markRead(post.id);
    el.innerHTML = '<article class="post-detail"><div class="post-detail-header"><nav class="post-detail-breadcrumb"><a href="#/" onclick="App.go(\'/\')">Home</a><span>/</span><a href="#/cat/' + post.category + '" onclick="App.go(\'/cat/' + post.category + '\')">' + (cat?.title || post.category) + '</a>' + (sub ? '<span>/</span><a href="#/cat/' + post.category + '/sub/' + post.subtopic + '" onclick="App.go(\'/cat/' + post.category + '/sub/' + post.subtopic + '\')">' + sub.title + '</a>' : '') + '</nav><h1 class="post-detail-title">' + post.title + '</h1><div class="post-detail-meta"><div class="post-detail-author" onclick="App.go(\'/author/' + post.author + '\')" style="cursor:pointer"><div class="post-detail-author-avatar">' + Content.initials(author?.name) + '</div><div class="post-detail-author-info"><span class="post-detail-author-name">' + (author?.name || '') + '</span><span class="post-detail-author-role">' + (author?.bio || '') + '</span></div></div><span class="post-detail-date">' + Content.fmtDate(post.published_date) + '</span><span class="post-detail-reading-time">' + rt + '</span></div></div>' + (post.featured_image ? '<figure class="post-detail-featured-image"><img src="' + post.featured_image + '" alt="' + (post.featured_image_alt || '') + '" onerror="this.style.display=\'none\'"></figure>' : '') + '<div class="article-content">' + (post.content || '') + '</div>' + (post.tags?.length ? '<div class="post-detail-tags"><strong>Tags:</strong>' + post.tags.map(t => '<span class="post-detail-tag" onclick="App.searchTag(\'' + t + '\')">' + t + '</span>').join('') + '</div>' : '') + '<div class="share-section"><h3 class="share-section-title">Share</h3><div class="share-buttons"><button class="share-btn" onclick="App.share(\'twitter\')">' + this.icon('twitter') + '</button><button class="share-btn" onclick="App.share(\'facebook\')">' + this.icon('facebook') + '</button><button class="share-btn" onclick="App.share(\'linkedin\')">' + this.icon('linkedin') + '</button><button class="share-btn" onclick="App.copyLink()">' + this.icon('link') + '</button></div></div>' + (related.length ? '<div class="related-posts"><h2 class="related-posts-title">Related</h2><div class="related-posts-grid">' + related.map(p => this.card(p)).join('') + '</div></div>' : '') + '</article>';
  },
  
  renderCategory(catId) {
    const cat = Content.getCategory(catId);
    if (!cat) { Router.handle(); return; }
    const el = document.getElementById('main-content');
    if (!el) return;
    const posts = Content.getPostsByCategory(catId);
    const subs = Content.getVisibleSubtopics(catId);
    el.innerHTML = '<section class="section"><div class="container"><div class="section-header"><h1 class="section-title">' + cat.title + '</h1><p class="section-subtitle">' + (cat.description || '') + '</p></div>' + (subs.length ? '<div class="category-filter" style="margin-bottom:32px"><button class="category-filter-btn active" onclick="App.filterCat(\'' + catId + '\',\'all\',this)">All</button>' + subs.map(s => '<button class="category-filter-btn" onclick="App.filterCat(\'' + catId + '\',\'' + s.id + '\',this)">' + s.title + '</button>').join('') + '</div>' : '') + '<div class="posts-grid" id="cat-posts">' + (posts.length ? posts.map(p => this.card(p)).join('') : '<p style="text-align:center;color:var(--text-secondary);padding:48px 0;grid-column:1/-1">No articles yet.</p>') + '</div></div></section>';
  },
  
  renderSubtopic(catId, subId) {
    const cat = Content.getCategory(catId);
    const sub = Content.getSubtopic(subId);
    if (!cat) { Router.handle(); return; }
    const el = document.getElementById('main-content');
    if (!el) return;
    const title = sub?.title || subId.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    const posts = Content.getPostsBySubtopic(subId);
    const subs = Content.getVisibleSubtopics(catId);
    el.innerHTML = '<section class="section"><div class="container"><div class="section-header"><nav class="post-detail-breadcrumb" style="justify-content:center;margin-bottom:16px"><a href="#/" onclick="App.go(\'/\')">Home</a><span>/</span><a href="#/cat/' + catId + '" onclick="App.go(\'/cat/' + catId + '\')">' + cat.title + '</a><span>/</span><span style="color:var(--text);font-weight:600">' + title + '</span></nav><h1 class="section-title">' + title + '</h1></div>' + (subs.length ? '<div class="category-filter" style="margin-bottom:32px"><button class="category-filter-btn" onclick="App.go(\'/cat/' + catId + '\')">All ' + cat.title + '</button>' + subs.map(s => '<button class="category-filter-btn' + (s.id === subId ? ' active' : '') + '" onclick="App.go(\'/cat/' + catId + '/sub/' + s.id + '\')">' + s.title + '</button>').join('') + '</div>' : '') + '<div class="posts-grid">' + (posts.length ? posts.map(p => this.card(p)).join('') : '<p style="text-align:center;color:var(--text-secondary);padding:48px 0;grid-column:1/-1">No articles yet.</p>') + '</div></div></section>';
  },
  
  renderAuthorPage(authorId) {
    const author = Content.getAuthor(authorId);
    if (!author) { Router.handle(); return; }
    const el = document.getElementById('main-content');
    if (!el) return;
    
    const posts = Content.getPostsByAuthor(authorId);
    const initials = Content.initials(author.name);
    
    el.innerHTML = '<section class="section"><div class="container">' +
      '<div style="text-align:center;margin-bottom:48px;padding:40px 20px;background:var(--surface);border-radius:16px;box-shadow:0 2px 12px var(--shadow)">' +
      '<div style="width:100px;height:100px;margin:0 auto 16px;border-radius:50%;background:var(--primary);color:white;display:flex;align-items:center;justify-content:center;font-size:2rem;font-weight:700">' + initials + '</div>' +
      '<h1 style="font-size:1.75rem;margin-bottom:8px;color:var(--text)">' + author.name + '</h1>' +
      (author.role ? '<p style="color:var(--primary);font-weight:600;margin-bottom:4px">' + author.role + '</p>' : '') +
      (author.specialization ? '<p style="color:var(--text-secondary);font-size:0.9rem;margin-bottom:12px">' + author.specialization + '</p>' : '') +
      (author.bio ? '<p style="color:var(--text-secondary);max-width:600px;margin:0 auto;line-height:1.7">' + author.bio + '</p>' : '') +
      '<p style="margin-top:16px;color:var(--text-muted);font-size:0.9rem">' + posts.length + ' article' + (posts.length !== 1 ? 's' : '') + ' published</p>' +
      '</div>' +
      '<div class="section-header"><h2 class="section-title">Articles by ' + author.name + '</h2></div>' +
      '<div class="posts-grid">' +
      (posts.length ? posts.map(p => this.card(p)).join('') : '<p style="text-align:center;color:var(--text-secondary);padding:48px 0;grid-column:1/-1">No articles yet.</p>') +
      '</div></div></section>';
  },

  renderAbout() {
    const el = document.getElementById('main-content');
    if (!el) return;
    const a = Content.getAbout();
    el.innerHTML = '<div class="about-container container"><div class="about-hero"><h1 class="about-hero-title">' + (a.title || 'About') + '</h1><p class="about-hero-subtitle">' + (a.subtitle || '') + '</p></div><div class="article-content">' + (a.body || '<p style="text-align:center;color:var(--text-secondary)">No content yet.</p>') + '</div></div>';
  },
  
  renderGlossary() {
    const el = document.getElementById('main-content');
    if (!el) return;
    const grouped = Content.getGlossaryByLetter();
    const letters = Object.keys(grouped);
    el.innerHTML = '<div class="glossary-container container"><div class="section-header"><h1 class="section-title">Glossary</h1><p class="section-subtitle">Terms and definitions</p></div><div class="glossary-search"><div class="glossary-search-icon">' + this.icon('search') + '</div><input type="text" class="glossary-search-input" placeholder="Search terms..." oninput="App.filterGlossary(this.value)"></div>' + (letters.length ? '<div class="glossary-letter-nav">' + letters.map(letter => '<button class="glossary-letter-btn" onclick="App.scrollToLetter(\'' + letter + '\')">' + letter + '</button>').join('') + '</div>' : '') + '<div id="glossary-content">' + letters.map(letter => '<div class="glossary-group" id="gl-' + letter + '"><h2 class="glossary-group-title">' + letter + '</h2>' + grouped[letter].map(t => '<div class="glossary-item"><h3 class="glossary-item-term">' + t.word + '</h3><p class="glossary-item-definition">' + t.definition + '</p></div>').join('') + '</div>').join('') + '</div></div>';
  },
  
  renderFAQs() {
    const el = document.getElementById('main-content');
    if (!el) return;
    const faqs = Content.faqs;
    el.innerHTML = '<div class="faqs-container container"><div class="section-header"><h1 class="section-title">FAQs</h1><p class="section-subtitle">Frequently asked questions</p></div><div class="glossary-search" style="margin-bottom:32px"><div class="glossary-search-icon">' + this.icon('search') + '</div><input type="text" class="glossary-search-input" placeholder="Search questions..." oninput="App.filterFAQs(this.value)"></div><div id="faqs-content">' + (faqs.length ? faqs.map(f => '<div class="faq-item"><div class="faq-question" onclick="App.toggleFAQ(this)"><span class="faq-question-text">' + f.question + '</span><span class="faq-question-icon">' + this.icon('chevron-down') + '</span></div><div class="faq-answer"><p>' + f.answer + '</p></div></div>').join('') : '<p style="text-align:center;color:var(--text-secondary);padding:48px">No FAQs yet.</p>') + '</div></div>';
  },
  
  filterFAQs(q) {
    const faqs = Content.faqs;
    const filtered = q ? faqs.filter(f => f.question.toLowerCase().includes(q.toLowerCase())) : faqs;
    const c = document.getElementById('faqs-content');
    if (!c) return;
    if (!filtered.length) { c.innerHTML = '<p style="text-align:center;color:var(--text-secondary);padding:48px">No questions found.</p>'; return; }
    c.innerHTML = filtered.map(f => '<div class="faq-item"><div class="faq-question" onclick="App.toggleFAQ(this)"><span class="faq-question-text">' + f.question + '</span><span class="faq-question-icon">' + this.icon('chevron-down') + '</span></div><div class="faq-answer"><p>' + f.answer + '</p></div></div>').join('');
  },
  
  renderDownloads() {
    const el = document.getElementById('main-content');
    if (!el) return;
    const dls = Content.getPublishedDownloads();
    el.innerHTML = '<div class="downloads-container container"><div class="section-header"><h1 class="section-title">Downloads</h1><p class="section-subtitle">Resources and files</p></div><div class="downloads-grid">' + (dls.length ? dls.map(d => '<div class="download-card"><div class="download-card-image"><img src="' + (d.thumbnail || '') + '" alt="' + d.name + '" loading="lazy" onerror="this.style.display=\'none\'"><span class="download-card-format">' + (d.file_format || 'FILE') + '</span></div><div class="download-card-content"><h3 class="download-card-title">' + d.name + '</h3><p class="download-card-description">' + (d.description || '') + '</p>' + (d.file_size ? '<div class="download-card-meta"><span>' + d.file_size + '</span></div>' : '') + '<a class="download-card-btn" href="' + (d.file_url || '#') + '" target="_blank" rel="noopener" style="text-decoration:none;color:#fff">' + this.icon('download') + ' Download</a></div></div>').join('') : '<p style="text-align:center;color:var(--text-secondary);padding:48px;grid-column:1/-1">No downloads yet.</p>') + '</div></div>';
  },
  
  renderSearchPage() {
    const el = document.getElementById('main-content');
    if (!el) return;
    el.innerHTML = '<section class="section"><div class="container"><div class="section-header"><h1 class="section-title">Search</h1></div><div style="max-width:600px;margin:0 auto"><input type="text" class="form-input" placeholder="Search..." id="page-search" style="width:100%;margin-bottom:32px" oninput="App.pageSearch(this.value)"><div id="page-results"><p style="text-align:center;color:var(--text-secondary)">Type to search.</p></div></div></div></section>';
  },
  
  // ===== ACTIONS =====
  go(path) { this.closeSidebar(); Router.go(path); },
  toggleSidebar() { document.getElementById('sidebar')?.classList.toggle('open'); document.getElementById('sidebar-overlay')?.classList.toggle('active'); document.getElementById('menu-toggle')?.classList.toggle('active'); document.body.style.overflow = document.getElementById('sidebar')?.classList.contains('open') ? 'hidden' : ''; },
  closeSidebar() { document.getElementById('sidebar')?.classList.remove('open'); document.getElementById('sidebar-overlay')?.classList.remove('active'); document.getElementById('menu-toggle')?.classList.remove('active'); document.body.style.overflow = ''; },
  toggleNav(el) { const item = el.closest('.nav-item'); if (!item) return; document.querySelectorAll('.nav-item.open').forEach(i => { if (i !== item) i.classList.remove('open'); }); item.classList.toggle('open'); },
  openSearch() { document.getElementById('search-modal')?.classList.add('active'); setTimeout(() => document.getElementById('search-input')?.focus(), 200); },
  closeSearch() { document.getElementById('search-modal')?.classList.remove('active'); },
  toggleContact() { document.getElementById('contact-modal')?.classList.toggle('active'); },
  closeContact() { document.getElementById('contact-modal')?.classList.remove('active'); },
  toggleFAQ(el) { el.closest('.faq-item')?.classList.toggle('open'); },
  heroSearch() { const i = document.getElementById('hero-search'); if (i?.value.trim()) { this.openSearch(); const s = document.getElementById('search-input'); if (s) { s.value = i.value.trim(); this.doSearch(i.value.trim()); } } },
  
  doSearch(query) {
    const c = document.getElementById('search-results');
    if (!c) return;
    if (!query || query.length < 2) { c.innerHTML = '<div class="search-empty">' + this.icon('search') + '<h3>Start typing</h3></div>'; return; }
    const results = Content.search(query);
    if (!results.length) { c.innerHTML = '<div class="search-empty">' + this.icon('search') + '<h3>No results</h3></div>'; return; }
    const esc = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const rx = new RegExp('(' + esc + ')', 'gi');
    c.innerHTML = results.map(r => {
      const cat = Content.getCategory(r.post.category);
      const badges = r.matches.map(m => '<span class="search-match-badge ' + m + '-match">' + m.charAt(0).toUpperCase() + m.slice(1) + '</span>').join('');
      const title = r.matches.includes('title') ? r.post.title.replace(rx, '<mark>$1</mark>') : r.post.title;
      const excerpt = r.matches.includes('excerpt') ? (r.post.excerpt || '').replace(rx, '<mark>$1</mark>') : (r.post.excerpt || '');
      let snippet = '';
      if (r.matches.includes('content') && r.post.content) {
        const text = r.post.content.replace(/<[^>]*>/g, '');
        const idx = text.toLowerCase().indexOf(query.toLowerCase());
        if (idx >= 0) {
          const s = text.substring(Math.max(0, idx - 60), Math.min(text.length, idx + query.length + 60));
          snippet = '<div class="search-content-snippet"><span class="snippet-label">In article:</span><p class="snippet-text">' + s.replace(rx, '<mark>$1</mark>') + '</p></div>';
        }
      }
      return '<div class="search-result-item" onclick="App.closeSearch();App.go(\'/post/' + r.post.id + '\')"><div class="search-result-header"><div class="search-result-category">' + (cat?.title || r.post.category) + '</div><div class="search-match-indicators">' + badges + '</div></div><h3 class="search-result-title">' + title + '</h3><p class="search-result-excerpt">' + excerpt + '</p>' + snippet + '</div>';
    }).join('');
  },
  
  pageSearch(query) {
    const c = document.getElementById('page-results');
    if (!c) return;
    if (!query || query.length < 2) { c.innerHTML = '<p style="text-align:center;color:var(--text-secondary)">Type to search.</p>'; return; }
    const results = Content.search(query);
    c.innerHTML = results.length ? results.map(r => this.card(r.post)).join('') : '<p style="text-align:center;color:var(--text-secondary)">No results.</p>';
  },
  
  filterHome(cat, btn) {
    document.querySelectorAll('.category-filter-btn').forEach(b => b.classList.remove('active'));
    btn?.classList.add('active');
    const specialTypes = ['downloads', 'glossary', 'faqs', 'about'];
    let posts;
    if (cat === 'all') {
      posts = Content.getRecentPosts(50).filter(p => {
        const c = Content.getCategory(p.category);
        return c && !specialTypes.includes(c.type);
      }).slice(0, 9);
    } else {
      posts = Content.getPostsByCategory(cat);
    }
    const g = document.getElementById('home-posts');
    if (g) g.innerHTML = posts.length ? posts.map(p => this.card(p)).join('') : '<p style="text-align:center;color:var(--text-secondary);padding:48px 0;grid-column:1/-1">No articles.</p>';
  },
  filterCat(catId, subId, btn) { document.querySelectorAll('.category-filter-btn').forEach(b => b.classList.remove('active')); btn?.classList.add('active'); const posts = subId === 'all' ? Content.getPostsByCategory(catId) : Content.getPostsBySubtopic(subId); const g = document.getElementById('cat-posts'); if (g) g.innerHTML = posts.length ? posts.map(p => this.card(p)).join('') : '<p style="text-align:center;color:var(--text-secondary);padding:48px 0;grid-column:1/-1">No articles.</p>'; },
  searchTag(tag) { this.openSearch(); const s = document.getElementById('search-input'); if (s) { s.value = tag; this.doSearch(tag); } },
  filterGlossary(q) {
    const terms = q ? Content.glossary.filter(t => t.word.toLowerCase().includes(q.toLowerCase())) : Content.glossary;
    const c = document.getElementById('glossary-content');
    if (!c) return;
    if (!terms.length) { c.innerHTML = '<p style="text-align:center;color:var(--text-secondary);padding:48px">No terms found.</p>'; return; }
    const grouped = {};
    terms.forEach(t => { const l = t.word[0].toUpperCase(); if (!grouped[l]) grouped[l] = []; grouped[l].push(t); });
    c.innerHTML = Object.keys(grouped).sort().map(letter => '<div class="glossary-group" id="gl-' + letter + '"><h2 class="glossary-group-title">' + letter + '</h2>' + grouped[letter].map(t => '<div class="glossary-item"><h3 class="glossary-item-term">' + t.word + '</h3><p class="glossary-item-definition">' + t.definition + '</p></div>').join('') + '</div>').join('');
  },
  
  scrollToLetter(letter) {
    const el = document.getElementById('gl-' + letter);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  },
  
  async sendContact(form) {
    const name = form.querySelector('[name="name"]')?.value.trim();
    const email = form.querySelector('[name="email"]')?.value.trim();
    const message = form.querySelector('[name="message"]')?.value.trim();
    if (!name || !email || !message) { this.toast('Fill all fields', 'error'); return; }
    if (DB.ready) await DB.upsert('contact_messages', { name, email, message });
    const key = Content.getWeb3Key();
    if (key && key !== 'YOUR_KEY_HERE') {
      try { await fetch('https://api.web3forms.com/submit', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ access_key: key, name, email, message, subject: 'Contact from ' + name }) }); } catch (e) {}
    }
    this.toast('Message sent!');
    form.reset(); this.closeContact();
  },
  
  async sendNewsletter(e) {
    e.preventDefault();
    const form = e.target;
    const name = form.querySelector('[name="name"]')?.value.trim();
    const email = form.querySelector('[name="email"]')?.value.trim();
    if (!name || !email) { this.toast('Fill all fields', 'error'); return; }
    if (DB.ready) {
      const { error } = await DB.upsert('newsletter_subscribers', { name, email });
      if (error?.code === '23505') { this.toast('Already subscribed!', 'warning'); return; }
    }
    const key = Content.getWeb3Key();
    if (key && key !== 'YOUR_KEY_HERE') {
      try { await fetch('https://api.web3forms.com/submit', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ access_key: key, name, email, message: 'Newsletter subscription from ' + name + ' (' + email + ')', subject: 'New Subscriber: ' + name }) }); } catch (e) {}
    }
    this.toast('Subscribed!');
    form.reset();
  },
  
  share(platform) {
    const url = encodeURIComponent(window.location.href);
    const text = encodeURIComponent(document.title);
    const urls = { twitter: 'https://twitter.com/intent/tweet?text=' + text + '&url=' + url, facebook: 'https://www.facebook.com/sharer/sharer.php?u=' + url, linkedin: 'https://www.linkedin.com/shareArticle?mini=true&url=' + url };
    if (urls[platform]) window.open(urls[platform], '_blank');
  },
  copyLink() { navigator.clipboard?.writeText(window.location.href).then(() => this.toast('Copied!')); },
  
  toast(msg, type) { const t = document.getElementById('toast'); if (!t) return; t.textContent = msg; t.className = 'toast toast-' + (type || 'info') + ' visible'; setTimeout(() => t.classList.remove('visible'), 3500); },
  hideLoader() { const l = document.getElementById('loading-screen'); if (l) { l.style.opacity = '0'; setTimeout(() => l.style.display = 'none', 300); } },
  
  icon(name) {
    const i = {
      'menu': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>',
      'close': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
      'search': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
      'sun': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/></svg>',
      'moon': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
      'edit': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>',
      'download': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
      'book': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>',
      'help': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
      'info': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
      'briefcase': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>',
      'bank': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 22 7 12 2"/><line x1="2" y1="17" x2="22" y2="17"/><line x1="2" y1="7" x2="2" y2="17"/><line x1="22" y1="7" x2="22" y2="17"/><line x1="7" y1="7" x2="7" y2="17"/><line x1="12" y1="7" x2="12" y2="17"/><line x1="17" y1="7" x2="17" y2="17"/></svg>',
      'balance': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v18"/><path d="M5 8l7-5 7 5"/><path d="M5 8v8a3 3 0 0 0 3 3h1"/><path d="M19 8v8a3 3 0 0 1-3 3h-1"/></svg>',
      'chevron-down': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>',
      'twitter': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z"/></svg>',
      'facebook': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>',
      'linkedin': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg>',
      'link': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
      'mail': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;vertical-align:middle"><rect x="2" y="4" width="20" height="16" rx="2"/><polyline points="22,4 12,13 2,4"/></svg>',
      'instagram': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/></svg>',
      'youtube': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>',
      'message': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
      'arrow-up': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>',
      'file': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/></svg>'
    };
    return i[name] || i['file'];
  }
};

document.addEventListener('DOMContentLoaded', () => App.init());