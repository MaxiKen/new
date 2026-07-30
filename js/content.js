// Blog Template - Content Manager (DB-first with local cache)
const Content = {
  settings: null,
  authors: [],
  categories: [],
  subtopics: [],
  posts: [],
  downloads: [],
  glossary: [],
  faqs: [],
  about: null,
  source: 'db',
  
  async init() {
    if (DB.ready) {
      try {
        const [settings, authors, categories, subtopics, posts, downloads, glossary, faqs, about] = await Promise.all([
          DB.get('site_settings', 1),
          DB.all('authors', 'name'),
          DB.all('categories', 'sort_order'),
          DB.all('subtopics', 'sort_order'),
          DB.all('posts', 'published_date', false),
          DB.all('downloads', 'sort_order'),
          DB.all('glossary', 'word'),
          DB.all('faqs', 'sort_order'),
          DB.get('about', 1)
        ]);
        
        if (settings) {
          this.settings = settings;
          Store.cacheSettings(settings);
        }
        this.authors = authors || [];
        this.categories = categories || [];
        this.subtopics = subtopics || [];
        this.posts = posts || [];
        this.downloads = downloads || [];
        this.glossary = glossary || [];
          this.faqs = faqs || [];
        this.about = about;
        
        // Cache individual data
        Store.cache('authors', this.authors);
        Store.cache('categories', this.categories);
        Store.cache('subtopics', this.subtopics);
        Store.cache('posts', this.posts);
        Store.cache('downloads', this.downloads);
        Store.cache('glossary', this.glossary);
        Store.cache('faqs', this.faqs);
        Store.cache('about', this.about);
        
        this.source = 'db';
        return true;
      } catch (e) { console.warn('[Content] DB load error:', e); }
    }
    
    // Fallback to cache
    this.settings = Store.getSettings();
    this.authors = Store.getCached('authors') || [];
    this.categories = Store.getCached('categories') || [];
    this.subtopics = Store.getCached('subtopics') || [];
    this.posts = Store.getCached('posts') || [];
    this.downloads = Store.getCached('downloads') || [];
    this.glossary = Store.getCached('glossary') || [];
    this.faqs = Store.getCached('faqs') || [];
    this.about = Store.getCached('about');
    this.source = 'cache';
    return !!this.settings;
  },
  
  // Settings helpers
  getSite() { return this.settings?.site || {}; },
  getThemes() { return this.settings?.themes || {}; },
  getSEO() { return this.settings?.seo || {}; },
  getSocial() { return this.settings?.social || {}; },
  getFooter() { return this.settings?.footer || {}; },
  getContact() { return this.settings?.contact || {}; },
  getSiteName() { return this.getSite().name || 'Blog'; },
  getWeb3Key() { return this.getContact().web3forms_key || ''; },
  getEmail() { return this.getContact().email || ''; },
  getSocial() { return this.settings?.social || {}; },
  getContact() { return this.settings?.contact || {}; },
  
  // Categories
  getVisibleCategories() {
    return this.categories.filter(c => !c.hidden);
  },
  getCategory(id) { return this.categories.find(c => c.id === id); },
  getVisibleSubtopics(catId) {
    return this.subtopics.filter(s => s.category_id === catId && !s.hidden);
  },
  getSubtopic(id) { return this.subtopics.find(s => s.id === id); },
  
  // Authors
  getAuthor(id) { return this.authors.find(a => a.id === id); },
  
  // Posts
  isLive(p) {
    if (p.status) {
      if (p.status === 'published') return true;
      if (p.status === 'scheduled') return p.scheduled_for && new Date(p.scheduled_for) <= new Date();
      return false;
    }
    return p.is_published !== false;
  },

  getPublishedPosts() {
    return this.posts
      .filter(p => this.isLive(p))
      .sort((a, b) => {
        // Sort by created_at timestamp (most accurate), fall back to published_date
        const da = a.created_at || a.published_date || '';
        const db = b.created_at || b.published_date || '';
        return da < db ? 1 : da > db ? -1 : 0;
      });
  },
  getPost(id) { return this.posts.find(p => p.id === id); },
  getPostsByCategory(cat) {
    return this.getPublishedPosts().filter(p => p.category === cat);
  },
  getPostsBySubtopic(sub) {
    return this.getPublishedPosts().filter(p => p.subtopic === sub);
  },
  getPostsByAuthor(authorId) {
    return this.getPublishedPosts().filter(p => p.author === authorId);
  },
  getFeaturedPosts() { return this.getPublishedPosts().filter(p => p.is_featured); },
  getRecentPosts(limit) {
    return this.getPublishedPosts().slice(0, limit || 9);
  },
  getRelatedPosts(postId, limit) {
    const post = this.getPost(postId);
    if (!post) return [];
    return this.getPublishedPosts()
      .filter(p => p.id !== postId && (p.category === post.category || p.subtopic === post.subtopic))
      .slice(0, limit || 3);
  },
  calcReadTime(post) {
    if (!post?.content) return '1 min';
    const text = post.content.replace(/<[^>]*>/g, '');
    const words = text.split(/\s+/).filter(Boolean).length;
    return Math.max(1, Math.ceil(words / 200)) + ' min read';
  },
  
  // Search
  search(query) {
    if (!query || query.length < 2) return [];
    const q = query.toLowerCase();
    const results = [];
    this.getPublishedPosts().forEach(post => {
      const matches = [];
      if (post.title?.toLowerCase().includes(q)) matches.push('title');
      if (post.excerpt?.toLowerCase().includes(q)) matches.push('excerpt');
      if (post.content?.toLowerCase().includes(q)) matches.push('content');
      if (post.tags?.some(t => t.toLowerCase().includes(q))) matches.push('tags');
      if (matches.length > 0) results.push({ post, matches });
    });
    return results.sort((a, b) => {
      const pa = a.matches.includes('title') ? 0 : 1;
      const pb = b.matches.includes('title') ? 0 : 1;
      return pa - pb;
    });
  },
  
  // Downloads
  getPublishedDownloads() { return this.downloads.filter(d => d.is_published); },
  
  // Glossary
  getGlossaryByLetter() {
    const grouped = {};
    this.glossary.forEach(t => {
      const letter = (t.word || '?')[0].toUpperCase();
      if (!grouped[letter]) grouped[letter] = [];
      grouped[letter].push(t);
    });
    const sorted = {};
    Object.keys(grouped).sort().forEach(k => { sorted[k] = grouped[k].sort((a, b) => (a.word || '').localeCompare(b.word || '')); });
    return sorted;
  },
  
  // About
  getAbout() { return this.about || {}; },
  
  // Format
  fmtDate(d) {
    if (!d) return '';
    try { return new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }); } catch (e) { return d; }
  },
  initials(name) {
    if (!name) return '?';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
  }
};