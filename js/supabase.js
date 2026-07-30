// Blog Template - Supabase Client
const DB = {
  client: null,
  ready: false,
  
  init() {
    if (!ENV?.SUPABASE_URL || ENV.SUPABASE_URL.includes('YOUR_PROJECT_ID')) {
      console.log('[DB] No credentials'); return false;
    }
    const s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js';
    s.onload = () => {
      this.client = window.supabase.createClient(ENV.SUPABASE_URL, ENV.SUPABASE_ANON_KEY);
      this.ready = true;
      console.log('[DB] Connected');
      window.dispatchEvent(new Event('db-ready'));
    };
    s.onerror = () => console.warn('[DB] SDK load failed');
    document.head.appendChild(s);
    return true;
  },
  
  async all(table, col, asc) {
    if (!this.ready) return [];
    try {
      let q = this.client.from(table).select('*');
      if (col) q = q.order(col, { ascending: asc !== false });
      const { data, error } = await q;
      if (error) throw error;
      return data || [];
    } catch (e) { console.warn('[DB] all(' + table + '):', e); return []; }
  },
  
  async get(table, id) {
    if (!this.ready) return null;
    try {
      const { data, error } = await this.client.from(table).select('*').eq('id', id).single();
      if (error) throw error;
      return data;
    } catch (e) { return null; }
  },
  
  async rpc(fn, args) {
    if (!this.ready) return null;
    try {
      const { data, error } = await this.client.rpc(fn, args || {});
      if (error) throw error;
      return data;
    } catch (e) { console.warn('[DB] rpc(' + fn + '):', e); return null; }
  },

  async upsert(table, row) {
    if (!this.ready) return { error: { message: 'Not connected' } };
    return await this.client.from(table).upsert(row);
  },
  
  async del(table, id, col) {
    if (!this.ready) return { error: { message: 'Not connected' } };
    let q = this.client.from(table).delete();
    return col ? await q.eq(col, id) : await q.eq('id', id);
  },
  
  async upload(bucket, file, folder) {
    if (!this.ready) return null;
    try {
      const ext = file.name.split('.').pop().toLowerCase();
      const base = file.name.replace(/\.[^/.]+$/, '').replace(/[^a-zA-Z0-9-_]/g, '-').toLowerCase();
      const uid = Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
      const path = (folder ? folder + '/' : '') + base + '-' + uid + '.' + ext;
      const { error } = await this.client.storage.from(bucket).upload(path, file, { upsert: false });
      if (error) throw error;
      const { data } = this.client.storage.from(bucket).getPublicUrl(path);
      return data.publicUrl;
    } catch (e) { console.warn('[DB] Upload:', e); return null; }
  },
  
  url(bucket, path) {
    if (!this.ready) return null;
    const { data } = this.client.storage.from(bucket).getPublicUrl(path);
    return data?.publicUrl;
  }
};