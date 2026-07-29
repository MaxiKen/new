// Blog Template - Local Storage with TTL
const Store = {
  P: 'fil_',
  
  set(key, val, hours) {
    try {
      const ttl = hours ? Date.now() + hours * 3600000 : null;
      localStorage.setItem(this.P + key, JSON.stringify({ v: val, t: ttl }));
    } catch (e) {}
  },
  
  get(key) {
    try {
      const raw = localStorage.getItem(this.P + key);
      if (!raw) return null;
      const { v, t } = JSON.parse(raw);
      if (t && Date.now() > t) { localStorage.removeItem(this.P + key); return null; }
      return v;
    } catch (e) { return null; }
  },
  
  del(key) { try { localStorage.removeItem(this.P + key); } catch (e) {} },
  
  clear() {
    try {
      const keys = [];
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k.startsWith(this.P)) keys.push(k);
      }
      keys.forEach(k => localStorage.removeItem(k));
    } catch (e) {}
  },
  
  // Cache settings for 30 days
  cacheSettings(data) { this.set('settings', data, 720); },
  getSettings() { return this.get('settings'); },
  
  // Cache data with 24h TTL
  cache(key, data) { this.set(key, data, 24); },
  getCached(key) { return this.get(key); },
  
  // Theme preference (no expiry)
  setTheme(t) { this.set('theme', t); },
  getTheme() { return this.get('theme'); },
  
  // Scroll positions
  setScroll(page, pos) { this.set('scroll_' + page, pos); },
  getScroll(page) { return this.get('scroll_' + page) || 0; },
  
  // Read posts
  markRead(id) {
    const r = this.get('read') || [];
    if (!r.includes(id)) { r.push(id); this.set('read', r); }
  },
  isRead(id) { return (this.get('read') || []).includes(id); }
};