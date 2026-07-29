-- Blog Template - Supabase Schema
-- Run ENTIRE file in SQL Editor at once

-- =============================================
-- SITE SETTINGS (single row, all config)
-- =============================================
CREATE TABLE IF NOT EXISTS site_settings (
  id INTEGER PRIMARY KEY DEFAULT 1,
  site JSONB DEFAULT '{}',
  themes JSONB DEFAULT '{}',
  seo JSONB DEFAULT '{}',
  social JSONB DEFAULT '{}',
  footer JSONB DEFAULT '{}',
  contact JSONB DEFAULT '{}',
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- AUTHORS
-- =============================================
CREATE TABLE IF NOT EXISTS authors (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  avatar TEXT,
  bio TEXT,
  role TEXT,
  specialization TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- CATEGORIES
-- =============================================
CREATE TABLE IF NOT EXISTS categories (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  icon TEXT,
  description TEXT,
  type TEXT DEFAULT 'blog',
  sort_order INTEGER DEFAULT 0,
  hidden BOOLEAN DEFAULT FALSE,
  system_locked BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- SUBTOPICS
-- =============================================
CREATE TABLE IF NOT EXISTS subtopics (
  id TEXT PRIMARY KEY,
  category_id TEXT REFERENCES categories(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  type TEXT DEFAULT 'blog',
  page TEXT,
  sort_order INTEGER DEFAULT 0,
  hidden BOOLEAN DEFAULT FALSE,
  system_locked BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- POSTS
-- =============================================
CREATE TABLE IF NOT EXISTS posts (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  excerpt TEXT,
  content TEXT DEFAULT '',
  category TEXT NOT NULL,
  subtopic TEXT,
  author TEXT REFERENCES authors(id) ON DELETE SET NULL,
  published_date DATE DEFAULT CURRENT_DATE,
  tags TEXT[] DEFAULT '{}',
  featured_image TEXT,
  featured_image_alt TEXT,
  is_featured BOOLEAN DEFAULT FALSE,
  is_published BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- DOWNLOADS
-- =============================================
CREATE TABLE IF NOT EXISTS downloads (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  file_url TEXT,
  file_format TEXT,
  file_size TEXT,
  thumbnail TEXT,
  tags TEXT[] DEFAULT '{}',
  sort_order INTEGER DEFAULT 0,
  is_published BOOLEAN DEFAULT TRUE,
  system_locked BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- GLOSSARY
-- =============================================
CREATE TABLE IF NOT EXISTS glossary (
  id SERIAL PRIMARY KEY,
  word TEXT NOT NULL,
  definition TEXT NOT NULL,
  sort_order INTEGER DEFAULT 0,
  system_locked BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- FAQs
-- =============================================
CREATE TABLE IF NOT EXISTS faqs (
  id SERIAL PRIMARY KEY,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  sort_order INTEGER DEFAULT 0,
  system_locked BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- ABOUT
-- =============================================
CREATE TABLE IF NOT EXISTS about (
  id INTEGER PRIMARY KEY DEFAULT 1,
  title TEXT,
  subtitle TEXT,
  body TEXT DEFAULT '',
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- CONTACT MESSAGES
-- =============================================
CREATE TABLE IF NOT EXISTS contact_messages (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  message TEXT NOT NULL,
  is_read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- NEWSLETTER SUBSCRIBERS
-- =============================================
CREATE TABLE IF NOT EXISTS newsletter_subscribers (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- ROW LEVEL SECURITY
-- =============================================
ALTER TABLE site_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE authors ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE subtopics ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE downloads ENABLE ROW LEVEL SECURITY;
ALTER TABLE glossary ENABLE ROW LEVEL SECURITY;
ALTER TABLE faqs ENABLE ROW LEVEL SECURITY;
ALTER TABLE about ENABLE ROW LEVEL SECURITY;
ALTER TABLE contact_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_subscribers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read" ON site_settings FOR SELECT USING (true);
CREATE POLICY "Public read" ON authors FOR SELECT USING (true);
CREATE POLICY "Public read" ON categories FOR SELECT USING (true);
CREATE POLICY "Public read" ON subtopics FOR SELECT USING (true);
CREATE POLICY "Public read" ON posts FOR SELECT USING (true);
CREATE POLICY "Public read" ON downloads FOR SELECT USING (true);
CREATE POLICY "Public read" ON glossary FOR SELECT USING (true);
CREATE POLICY "Public read" ON faqs FOR SELECT USING (true);
CREATE POLICY "Public read" ON about FOR SELECT USING (true);
CREATE POLICY "Public read" ON contact_messages FOR SELECT USING (true);
CREATE POLICY "Public read" ON newsletter_subscribers FOR SELECT USING (true);

CREATE POLICY "Public write" ON site_settings FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Public write" ON authors FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Public write" ON categories FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Public write" ON subtopics FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Public write" ON posts FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Public write" ON downloads FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Public write" ON glossary FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Public write" ON faqs FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Public write" ON about FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Public write" ON contact_messages FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Public write" ON newsletter_subscribers FOR ALL USING (true) WITH CHECK (true);

-- =============================================
-- STORAGE BUCKETS
-- =============================================
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types) VALUES
('site-assets', 'site-assets', true, 10485760, ARRAY['image/jpeg','image/png','image/webp','image/gif','image/svg+xml']),
('post-images', 'post-images', true, 5242880, ARRAY['image/jpeg','image/png','image/webp','image/gif','image/svg+xml']),
('author-avatars', 'author-avatars', true, 2097152, ARRAY['image/jpeg','image/png','image/webp']),
('download-files', 'download-files', true, 104857600, ARRAY['application/pdf','application/vnd.openxmlformats-officedocument.wordprocessingml.document','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','application/vnd.openxmlformats-officedocument.presentationml.presentation','image/jpeg','image/png','image/webp','image/gif','image/svg+xml','audio/mpeg','audio/wav','video/mp4','video/webm','application/zip','text/csv'])
ON CONFLICT (id) DO UPDATE SET file_size_limit = EXCLUDED.file_size_limit, allowed_mime_types = EXCLUDED.allowed_mime_types;

CREATE POLICY "Public read storage" ON storage.objects FOR SELECT USING (true);
CREATE POLICY "Public upload storage" ON storage.objects FOR INSERT WITH CHECK (true);
CREATE POLICY "Public delete storage" ON storage.objects FOR DELETE USING (true);
CREATE POLICY "Public update storage" ON storage.objects FOR UPDATE USING (true);

-- =============================================
-- INDEXES
-- =============================================
CREATE INDEX IF NOT EXISTS idx_posts_cat ON posts(category);
CREATE INDEX IF NOT EXISTS idx_posts_sub ON posts(subtopic);
CREATE INDEX IF NOT EXISTS idx_posts_featured ON posts(is_featured) WHERE is_featured = true;
CREATE INDEX IF NOT EXISTS idx_posts_published ON posts(is_published, published_date DESC);
CREATE INDEX IF NOT EXISTS idx_subtopics_cat ON subtopics(category_id);
CREATE INDEX IF NOT EXISTS idx_categories_sort ON categories(sort_order);
CREATE INDEX IF NOT EXISTS idx_subtopics_sort ON subtopics(sort_order);
CREATE INDEX IF NOT EXISTS idx_downloads_sort ON downloads(sort_order);
CREATE INDEX IF NOT EXISTS idx_glossary_word ON glossary(word);
CREATE INDEX IF NOT EXISTS idx_contact_read ON contact_messages(is_read);
CREATE INDEX IF NOT EXISTS idx_contact_date ON contact_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_newsletter_email ON newsletter_subscribers(email);

-- =============================================
-- SEED: SITE SETTINGS
-- =============================================
INSERT INTO site_settings (id, site, themes, seo, social, footer, contact) VALUES (1,
'{"name":"My Blog","tagline":"Your blog tagline here","description":"A blog platform for your content.","logo":"","favicon":"","hero_image":"","hero_title":"Welcome","hero_subtitle":"Start writing and sharing your ideas."}',
'{"light":{"primary":"#3b82f6","secondary":"#60a5fa","accent":"#f59e0b","background":"#ffffff","surface":"#f8fafc","text":"#1e293b","text_secondary":"#64748b","border":"#e2e8f0"},"dark":{"primary":"#60a5fa","secondary":"#93c5fd","accent":"#fbbf24","background":"#0f172a","surface":"#1e293b","text":"#f1f5f9","text_secondary":"#94a3b8","border":"#334155"}}',
'{"title":"My Blog","description":"A blog platform","keywords":"blog, writing, content"}',
'{"twitter":"","facebook":"","linkedin":"","instagram":"","youtube":""}',
'{"copyright":"© 2026 My Blog. All rights reserved.","links":[]}',
'{"email":"admin@example.com","web3forms_key":"YOUR_KEY_HERE"}'
) ON CONFLICT (id) DO NOTHING;

-- =============================================
-- SEED: CATEGORIES
-- =============================================
INSERT INTO categories (id, title, icon, description, type, sort_order, hidden, system_locked) VALUES
('default', 'Blog', 'edit', 'Default blog category', 'blog', 1, false, false),
('downloads', 'Downloads', 'download', 'Downloadable resources', 'downloads', 2, false, true),
('glossary', 'Glossary', 'book', 'Terms and definitions', 'glossary', 3, false, true),
('faqs', 'FAQs', 'help', 'Frequently asked questions', 'faqs', 4, false, true),
('about', 'About', 'info', 'About us', 'about', 5, false, true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO subtopics (id, category_id, title, description, type, sort_order, hidden, system_locked) VALUES
('default-contents', 'default', 'Default Contents', 'General blog posts', 'blog', 1, false, false)
ON CONFLICT (id) DO NOTHING;

INSERT INTO about (id, title, subtitle, body) VALUES (1, 'About', 'Learn more about us', '') ON CONFLICT (id) DO NOTHING;