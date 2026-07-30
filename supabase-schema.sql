-- =====================================================================
--  BLOG PLATFORM — COMPLETE SUPABASE / POSTGRES SCHEMA  (v2.0)
-- =====================================================================
--  What this file does
--  -------------------
--  * Content tables (settings, authors, categories, subtopics, posts,
--    downloads, glossary, faqs, about, messages, subscribers)
--  * Account system:
--      - ONE admin account, username "admin" (immutable), no default
--        password (must be set later from the panel)
--      - AUTHOR accounts, created by the admin, initially WITHOUT a
--        password. Admin or the author can set / change / remove it
--        at any time. Blank password = passwordless sign-in.
--  * Server-side sessions (hashed tokens), lockout after failed
--    attempts, audit log, editorial workflow, revisions, media library,
--    scheduled publishing and view analytics.
--  * Every privileged operation goes through SECURITY DEFINER `api_*`
--    functions that validate a session token, so the public anon key
--    can NOT write to protected tables directly.
--
--  How to run
--  ----------
--  Supabase Dashboard -> SQL Editor -> New query -> paste ALL of this
--  -> Run.  The script is idempotent: safe on a fresh project and safe
--  to re-run over the previous version of this schema (no data loss).
-- =====================================================================

-- ---------------------------------------------------------------------
-- 0. EXTENSIONS
-- ---------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS extensions;
CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA extensions;

-- =====================================================================
-- 1. CONTENT TABLES
-- =====================================================================

-- Public site configuration (readable by everyone) -------------------
CREATE TABLE IF NOT EXISTS site_settings (
  id          INTEGER PRIMARY KEY DEFAULT 1,
  site        JSONB DEFAULT '{}',
  themes      JSONB DEFAULT '{}',
  seo         JSONB DEFAULT '{}',
  social      JSONB DEFAULT '{}',
  footer      JSONB DEFAULT '{}',
  contact     JSONB DEFAULT '{}',
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Private configuration (never exposed to the public anon key) --------
CREATE TABLE IF NOT EXISTS app_config (
  id          INTEGER PRIMARY KEY DEFAULT 1,
  editorial   JSONB DEFAULT '{}',   -- workflow rules
  security    JSONB DEFAULT '{}',   -- session / lockout rules
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Authors (public profiles) -------------------------------------------
CREATE TABLE IF NOT EXISTS authors (
  id              TEXT PRIMARY KEY,
  name            TEXT NOT NULL,
  avatar          TEXT,
  bio             TEXT,
  role            TEXT,
  specialization  TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE authors ADD COLUMN IF NOT EXISTS email        TEXT;
ALTER TABLE authors ADD COLUMN IF NOT EXISTS phone        TEXT;
ALTER TABLE authors ADD COLUMN IF NOT EXISTS website      TEXT;
ALTER TABLE authors ADD COLUMN IF NOT EXISTS location     TEXT;
ALTER TABLE authors ADD COLUMN IF NOT EXISTS tagline      TEXT;
ALTER TABLE authors ADD COLUMN IF NOT EXISTS cover_image  TEXT;
ALTER TABLE authors ADD COLUMN IF NOT EXISTS expertise    TEXT[] DEFAULT '{}';
ALTER TABLE authors ADD COLUMN IF NOT EXISTS socials      JSONB  DEFAULT '{}';
ALTER TABLE authors ADD COLUMN IF NOT EXISTS is_visible   BOOLEAN DEFAULT TRUE;
ALTER TABLE authors ADD COLUMN IF NOT EXISTS sort_order   INTEGER DEFAULT 0;
ALTER TABLE authors ADD COLUMN IF NOT EXISTS updated_at   TIMESTAMPTZ DEFAULT NOW();

-- Categories -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
  id            TEXT PRIMARY KEY,
  title         TEXT NOT NULL,
  icon          TEXT,
  description   TEXT,
  type          TEXT DEFAULT 'blog',
  sort_order    INTEGER DEFAULT 0,
  hidden        BOOLEAN DEFAULT FALSE,
  system_locked BOOLEAN DEFAULT FALSE,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Subtopics ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS subtopics (
  id            TEXT PRIMARY KEY,
  category_id   TEXT REFERENCES categories(id) ON DELETE CASCADE,
  title         TEXT NOT NULL,
  description   TEXT,
  type          TEXT DEFAULT 'blog',
  page          TEXT,
  sort_order    INTEGER DEFAULT 0,
  hidden        BOOLEAN DEFAULT FALSE,
  system_locked BOOLEAN DEFAULT FALSE,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Posts ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS posts (
  id                 TEXT PRIMARY KEY,
  title              TEXT NOT NULL,
  excerpt            TEXT,
  content            TEXT DEFAULT '',
  category           TEXT NOT NULL,
  subtopic           TEXT,
  author             TEXT REFERENCES authors(id) ON DELETE SET NULL,
  published_date     DATE DEFAULT CURRENT_DATE,
  tags               TEXT[] DEFAULT '{}',
  featured_image     TEXT,
  featured_image_alt TEXT,
  is_featured        BOOLEAN DEFAULT FALSE,
  is_published       BOOLEAN DEFAULT TRUE,
  created_at         TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE posts ADD COLUMN IF NOT EXISTS status           TEXT DEFAULT 'published';
ALTER TABLE posts ADD COLUMN IF NOT EXISTS scheduled_for    TIMESTAMPTZ;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS seo              JSONB DEFAULT '{}';
ALTER TABLE posts ADD COLUMN IF NOT EXISTS views            INTEGER DEFAULT 0;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS word_count       INTEGER DEFAULT 0;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS reading_minutes  INTEGER DEFAULT 1;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS updated_at       TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE posts ADD COLUMN IF NOT EXISTS created_by       UUID;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS updated_by       UUID;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS submitted_at     TIMESTAMPTZ;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS reviewed_at      TIMESTAMPTZ;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS review_note      TEXT;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS published_at     TIMESTAMPTZ;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'posts_status_check') THEN
    ALTER TABLE posts ADD CONSTRAINT posts_status_check
      CHECK (status IN ('draft','review','scheduled','published','archived'));
  END IF;
END $$;

-- Downloads ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS downloads (
  id            TEXT PRIMARY KEY,
  name          TEXT NOT NULL,
  description   TEXT,
  file_url      TEXT,
  file_format   TEXT,
  file_size     TEXT,
  thumbnail     TEXT,
  tags          TEXT[] DEFAULT '{}',
  sort_order    INTEGER DEFAULT 0,
  is_published  BOOLEAN DEFAULT TRUE,
  system_locked BOOLEAN DEFAULT FALSE,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE downloads ADD COLUMN IF NOT EXISTS downloads_count INTEGER DEFAULT 0;

-- Glossary -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS glossary (
  id            SERIAL PRIMARY KEY,
  word          TEXT NOT NULL,
  definition    TEXT NOT NULL,
  sort_order    INTEGER DEFAULT 0,
  system_locked BOOLEAN DEFAULT FALSE,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- FAQs -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS faqs (
  id            SERIAL PRIMARY KEY,
  question      TEXT NOT NULL,
  answer        TEXT NOT NULL,
  sort_order    INTEGER DEFAULT 0,
  system_locked BOOLEAN DEFAULT FALSE,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- About page -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS about (
  id         INTEGER PRIMARY KEY DEFAULT 1,
  title      TEXT,
  subtitle   TEXT,
  body       TEXT DEFAULT '',
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contact messages -----------------------------------------------------
CREATE TABLE IF NOT EXISTS contact_messages (
  id         SERIAL PRIMARY KEY,
  name       TEXT NOT NULL,
  email      TEXT NOT NULL,
  message    TEXT NOT NULL,
  is_read    BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE contact_messages ADD COLUMN IF NOT EXISTS is_archived BOOLEAN DEFAULT FALSE;
ALTER TABLE contact_messages ADD COLUMN IF NOT EXISTS subject     TEXT;

-- Newsletter -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS newsletter_subscribers (
  id         SERIAL PRIMARY KEY,
  name       TEXT NOT NULL,
  email      TEXT NOT NULL UNIQUE,
  is_active  BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================================
-- 2. ACCOUNTS, SESSIONS, AUDIT
-- =====================================================================

CREATE TABLE IF NOT EXISTS accounts (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username        TEXT NOT NULL UNIQUE,
  role            TEXT NOT NULL CHECK (role IN ('admin','author')),
  author_id       TEXT REFERENCES authors(id) ON DELETE CASCADE,
  password_hash   TEXT,                       -- NULL = no password (passwordless sign-in)
  password_set_at TIMESTAMPTZ,
  is_active       BOOLEAN DEFAULT TRUE,
  failed_attempts INTEGER DEFAULT 0,
  locked_until    TIMESTAMPTZ,
  last_login_at   TIMESTAMPTZ,
  last_login_ip   TEXT,
  login_count     INTEGER DEFAULT 0,
  notes           TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Only one admin account may ever exist
CREATE UNIQUE INDEX IF NOT EXISTS accounts_single_admin ON accounts ((role)) WHERE role = 'admin';
-- One login per author
CREATE UNIQUE INDEX IF NOT EXISTS accounts_author_unique ON accounts (author_id) WHERE author_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS sessions (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id    UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  token_hash    TEXT NOT NULL UNIQUE,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  last_seen_at  TIMESTAMPTZ DEFAULT NOW(),
  expires_at    TIMESTAMPTZ NOT NULL,
  remember      BOOLEAN DEFAULT FALSE,
  user_agent    TEXT,
  ip            TEXT,
  revoked_at    TIMESTAMPTZ,
  revoke_reason TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
  id         BIGSERIAL PRIMARY KEY,
  account_id UUID REFERENCES accounts(id) ON DELETE SET NULL,
  actor      TEXT,
  actor_role TEXT,
  action     TEXT NOT NULL,
  entity     TEXT,
  entity_id  TEXT,
  detail     JSONB DEFAULT '{}',
  ip         TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Post revision history -------------------------------------------------
CREATE TABLE IF NOT EXISTS post_revisions (
  id         BIGSERIAL PRIMARY KEY,
  post_id    TEXT NOT NULL,
  title      TEXT,
  excerpt    TEXT,
  content    TEXT,
  snapshot   JSONB DEFAULT '{}',
  saved_by   UUID,
  saved_by_name TEXT,
  note       TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Media library ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS media (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  url          TEXT NOT NULL,
  bucket       TEXT,
  path         TEXT,
  filename     TEXT,
  mime         TEXT,
  size_bytes   BIGINT,
  alt          TEXT,
  uploaded_by  UUID REFERENCES accounts(id) ON DELETE SET NULL,
  uploader     TEXT,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Per-day view analytics --------------------------------------------------
CREATE TABLE IF NOT EXISTS post_daily_views (
  post_id TEXT NOT NULL,
  day     DATE NOT NULL DEFAULT CURRENT_DATE,
  views   INTEGER DEFAULT 0,
  PRIMARY KEY (post_id, day)
);

-- =====================================================================
-- 3. INDEXES
-- =====================================================================
CREATE INDEX IF NOT EXISTS idx_posts_cat        ON posts(category);
CREATE INDEX IF NOT EXISTS idx_posts_sub        ON posts(subtopic);
CREATE INDEX IF NOT EXISTS idx_posts_author     ON posts(author);
CREATE INDEX IF NOT EXISTS idx_posts_status     ON posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_featured   ON posts(is_featured) WHERE is_featured = TRUE;
CREATE INDEX IF NOT EXISTS idx_posts_published  ON posts(is_published, published_date DESC);
CREATE INDEX IF NOT EXISTS idx_posts_sched      ON posts(scheduled_for) WHERE status = 'scheduled';
CREATE INDEX IF NOT EXISTS idx_subtopics_cat    ON subtopics(category_id);
CREATE INDEX IF NOT EXISTS idx_categories_sort  ON categories(sort_order);
CREATE INDEX IF NOT EXISTS idx_subtopics_sort   ON subtopics(sort_order);
CREATE INDEX IF NOT EXISTS idx_downloads_sort   ON downloads(sort_order);
CREATE INDEX IF NOT EXISTS idx_glossary_word    ON glossary(word);
CREATE INDEX IF NOT EXISTS idx_contact_read     ON contact_messages(is_read);
CREATE INDEX IF NOT EXISTS idx_contact_date     ON contact_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_newsletter_email ON newsletter_subscribers(email);
CREATE INDEX IF NOT EXISTS idx_sessions_account ON sessions(account_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_audit_created    ON audit_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_account    ON audit_log(account_id);
CREATE INDEX IF NOT EXISTS idx_revisions_post   ON post_revisions(post_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_media_uploader   ON media(uploaded_by, created_at DESC);

-- =====================================================================
-- 4. TRIGGERS
-- =====================================================================

-- generic updated_at ----------------------------------------------------
CREATE OR REPLACE FUNCTION app_touch_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at := NOW();
  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_authors_touch ON authors;
CREATE TRIGGER trg_authors_touch BEFORE UPDATE ON authors
  FOR EACH ROW EXECUTE FUNCTION app_touch_updated_at();

DROP TRIGGER IF EXISTS trg_accounts_touch ON accounts;
CREATE TRIGGER trg_accounts_touch BEFORE UPDATE ON accounts
  FOR EACH ROW EXECUTE FUNCTION app_touch_updated_at();

DROP TRIGGER IF EXISTS trg_settings_touch ON site_settings;
CREATE TRIGGER trg_settings_touch BEFORE UPDATE ON site_settings
  FOR EACH ROW EXECUTE FUNCTION app_touch_updated_at();

DROP TRIGGER IF EXISTS trg_about_touch ON about;
CREATE TRIGGER trg_about_touch BEFORE UPDATE ON about
  FOR EACH ROW EXECUTE FUNCTION app_touch_updated_at();

-- posts: derived fields + status sync ------------------------------------
CREATE OR REPLACE FUNCTION app_posts_before_write()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
  v_words INTEGER;
BEGIN
  NEW.status := COALESCE(NEW.status, 'draft');
  v_words := COALESCE(array_length(
                regexp_split_to_array(
                  btrim(regexp_replace(COALESCE(NEW.content,''), '<[^>]*>', ' ', 'g')),
                  '\s+'), 1), 0);
  NEW.word_count      := v_words;
  NEW.reading_minutes := GREATEST(1, CEIL(v_words / 200.0))::INTEGER;
  NEW.is_published    := (NEW.status = 'published');
  NEW.updated_at      := NOW();

  IF NEW.status = 'published' THEN
    IF NEW.published_at IS NULL THEN NEW.published_at := NOW(); END IF;
    IF NEW.published_date IS NULL THEN NEW.published_date := CURRENT_DATE; END IF;
    NEW.scheduled_for := NULL;
  END IF;

  IF NEW.status = 'archived' THEN
    NEW.is_featured := FALSE;
  END IF;

  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_posts_before ON posts;
CREATE TRIGGER trg_posts_before BEFORE INSERT OR UPDATE ON posts
  FOR EACH ROW EXECUTE FUNCTION app_posts_before_write();

-- posts: keep a revision of the previous content --------------------------
CREATE OR REPLACE FUNCTION app_posts_revision()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  IF (OLD.content IS DISTINCT FROM NEW.content)
     OR (OLD.title IS DISTINCT FROM NEW.title)
     OR (OLD.excerpt IS DISTINCT FROM NEW.excerpt) THEN
    INSERT INTO post_revisions (post_id, title, excerpt, content, snapshot, saved_by)
    VALUES (OLD.id, OLD.title, OLD.excerpt, OLD.content,
            jsonb_build_object('status', OLD.status, 'category', OLD.category,
                               'subtopic', OLD.subtopic, 'tags', OLD.tags,
                               'featured_image', OLD.featured_image),
            NEW.updated_by);
    -- keep only the 25 newest revisions per post
    DELETE FROM post_revisions r
     WHERE r.post_id = OLD.id
       AND r.id NOT IN (SELECT id FROM post_revisions WHERE post_id = OLD.id
                        ORDER BY created_at DESC LIMIT 25);
  END IF;
  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_posts_revision ON posts;
CREATE TRIGGER trg_posts_revision AFTER UPDATE ON posts
  FOR EACH ROW EXECUTE FUNCTION app_posts_revision();

-- accounts: protect the built-in admin -------------------------------------
CREATE OR REPLACE FUNCTION app_protect_admin()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    IF OLD.role = 'admin' THEN
      RAISE EXCEPTION 'The admin account cannot be deleted';
    END IF;
    RETURN OLD;
  END IF;

  IF TG_OP = 'UPDATE' AND OLD.role = 'admin' THEN
    IF NEW.username <> OLD.username THEN
      RAISE EXCEPTION 'The admin username cannot be changed';
    END IF;
    IF NEW.role <> 'admin' THEN
      RAISE EXCEPTION 'The admin role cannot be changed';
    END IF;
    NEW.is_active := TRUE;           -- the admin can never lock itself out
  END IF;

  IF TG_OP = 'INSERT' AND NEW.role = 'admin' AND lower(NEW.username) <> 'admin' THEN
    RAISE EXCEPTION 'The admin account must use the username "admin"';
  END IF;

  NEW.username := lower(btrim(NEW.username));
  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_accounts_protect ON accounts;
CREATE TRIGGER trg_accounts_protect BEFORE INSERT OR UPDATE OR DELETE ON accounts
  FOR EACH ROW EXECUTE FUNCTION app_protect_admin();

-- =====================================================================
-- 5. INTERNAL HELPERS  (not callable by the public key)
-- =====================================================================

CREATE OR REPLACE FUNCTION app_client_ip() RETURNS TEXT
LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE h TEXT;
BEGIN
  BEGIN
    h := current_setting('request.headers', true)::json ->> 'x-forwarded-for';
  EXCEPTION WHEN OTHERS THEN
    h := NULL;
  END;
  RETURN NULLIF(split_part(COALESCE(h, ''), ',', 1), '');
END $fn$;

CREATE OR REPLACE FUNCTION app_hash_token(p_token TEXT) RETURNS TEXT
LANGUAGE sql IMMUTABLE SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
  SELECT encode(digest(COALESCE(p_token, ''), 'sha256'), 'hex');
$fn$;

-- configuration with sane defaults
CREATE OR REPLACE FUNCTION app_cfg(p_group TEXT) RETURNS JSONB
LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE v JSONB; d JSONB;
BEGIN
  SELECT CASE p_group WHEN 'editorial' THEN editorial WHEN 'security' THEN security ELSE '{}'::JSONB END
    INTO v FROM app_config WHERE id = 1;
  d := CASE p_group
        WHEN 'editorial' THEN '{"require_approval":false,"authors_can_publish":true,"authors_can_delete":true,"authors_can_upload":true,"authors_can_schedule":true,"default_status":"draft"}'::JSONB
        WHEN 'security'  THEN '{"session_hours":12,"remember_days":30,"max_attempts":8,"lockout_minutes":15,"min_password_length":6,"allow_passwordless":true}'::JSONB
        ELSE '{}'::JSONB END;
  RETURN d || COALESCE(v, '{}'::JSONB);
END $fn$;

-- validate a session token, returns the account row (or an empty row)
CREATE OR REPLACE FUNCTION app_auth(p_token TEXT) RETURNS accounts
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE
  s sessions%ROWTYPE;
  a accounts%ROWTYPE;
  v_days INTEGER;
  v_hours INTEGER;
BEGIN
  IF p_token IS NULL OR length(p_token) < 20 THEN RETURN a; END IF;

  SELECT * INTO s FROM sessions
   WHERE token_hash = app_hash_token(p_token) AND revoked_at IS NULL;
  IF NOT FOUND THEN RETURN a; END IF;

  IF s.expires_at <= NOW() THEN
    UPDATE sessions SET revoked_at = NOW(), revoke_reason = 'expired' WHERE id = s.id;
    RETURN a;
  END IF;

  SELECT * INTO a FROM accounts WHERE id = s.account_id;
  IF NOT FOUND OR NOT a.is_active THEN
    a := NULL;
    RETURN a;
  END IF;

  v_days  := COALESCE((app_cfg('security') ->> 'remember_days')::INTEGER, 30);
  v_hours := COALESCE((app_cfg('security') ->> 'session_hours')::INTEGER, 12);

  -- sliding expiry: every request keeps an active session alive
  UPDATE sessions
     SET last_seen_at = NOW(),
         expires_at = CASE WHEN remember
                           THEN NOW() + make_interval(days => v_days)
                           ELSE GREATEST(expires_at, NOW() + make_interval(hours => v_hours)) END
   WHERE id = s.id;

  RETURN a;
END $fn$;

-- validate + enforce role, raises on failure
CREATE OR REPLACE FUNCTION app_require(p_token TEXT, p_role TEXT DEFAULT NULL) RETURNS accounts
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE a accounts%ROWTYPE;
BEGIN
  a := app_auth(p_token);
  IF a.id IS NULL THEN
    RAISE EXCEPTION 'AUTH_REQUIRED' USING ERRCODE = '28000';
  END IF;
  IF p_role = 'admin' AND a.role <> 'admin' THEN
    RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501';
  END IF;
  RETURN a;
END $fn$;

CREATE OR REPLACE FUNCTION app_log(p_acc accounts, p_action TEXT, p_entity TEXT DEFAULT NULL,
                                   p_entity_id TEXT DEFAULT NULL, p_detail JSONB DEFAULT '{}')
RETURNS VOID
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
BEGIN
  INSERT INTO audit_log (account_id, actor, actor_role, action, entity, entity_id, detail, ip)
  VALUES (p_acc.id, p_acc.username, p_acc.role, p_action, p_entity, p_entity_id,
          COALESCE(p_detail, '{}'::JSONB), app_client_ip());
END $fn$;

-- the "who am I" payload used everywhere in the panel
CREATE OR REPLACE FUNCTION app_account_json(p_id UUID) RETURNS JSONB
LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE a accounts%ROWTYPE; au authors%ROWTYPE;
BEGIN
  SELECT * INTO a FROM accounts WHERE id = p_id;
  IF NOT FOUND THEN RETURN NULL; END IF;
  IF a.author_id IS NOT NULL THEN SELECT * INTO au FROM authors WHERE id = a.author_id; END IF;
  RETURN jsonb_build_object(
    'id',            a.id,
    'username',      a.username,
    'role',          a.role,
    'author_id',     a.author_id,
    'has_password',  a.password_hash IS NOT NULL,
    'password_set_at', a.password_set_at,
    'is_active',     a.is_active,
    'last_login_at', a.last_login_at,
    'login_count',   a.login_count,
    'created_at',    a.created_at,
    'display_name',  COALESCE(au.name, initcap(a.username)),
    'avatar',        au.avatar,
    'profile',       CASE WHEN au.id IS NOT NULL THEN to_jsonb(au) ELSE NULL END
  );
END $fn$;

-- flip scheduled posts that are due
CREATE OR REPLACE FUNCTION app_publish_due() RETURNS INTEGER
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE n INTEGER;
BEGIN
  WITH due AS (
    UPDATE posts
       SET status = 'published',
           published_at = COALESCE(published_at, scheduled_for, NOW()),
           published_date = COALESCE(published_date, (COALESCE(scheduled_for, NOW()))::DATE)
     WHERE status = 'scheduled' AND scheduled_for IS NOT NULL AND scheduled_for <= NOW()
     RETURNING 1
  ) SELECT count(*) INTO n FROM due;
  RETURN COALESCE(n, 0);
END $fn$;

CREATE OR REPLACE FUNCTION app_slug(p_text TEXT) RETURNS TEXT
LANGUAGE sql IMMUTABLE SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
  SELECT btrim(regexp_replace(regexp_replace(lower(COALESCE(p_text, '')), '[^a-z0-9]+', '-', 'g'), '(^-+|-+$)', '', 'g'), '-');
$fn$;

CREATE OR REPLACE FUNCTION app_tags(p_data JSONB) RETURNS TEXT[]
LANGUAGE sql IMMUTABLE SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
  SELECT COALESCE((SELECT array_agg(btrim(t)) FROM jsonb_array_elements_text(
                     CASE WHEN jsonb_typeof(p_data) = 'array' THEN p_data ELSE '[]'::JSONB END) AS t
                   WHERE btrim(t) <> ''), '{}'::TEXT[]);
$fn$;

-- =====================================================================
-- 6. AUTHENTICATION API
-- =====================================================================

-- Is the very first admin sign-in still pending? (drives the login hint)
CREATE OR REPLACE FUNCTION api_admin_status() RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE a accounts%ROWTYPE;
BEGIN
  SELECT * INTO a FROM accounts WHERE role = 'admin';
  IF NOT FOUND THEN RETURN jsonb_build_object('installed', FALSE, 'needs_setup', TRUE); END IF;
  RETURN jsonb_build_object(
    'installed',   TRUE,
    'needs_setup', (a.password_hash IS NULL AND COALESCE(a.login_count, 0) = 0)
  );
END $fn$;

CREATE OR REPLACE FUNCTION api_login(p_username TEXT, p_password TEXT DEFAULT NULL,
                                     p_remember BOOLEAN DEFAULT FALSE, p_agent TEXT DEFAULT NULL)
RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE
  a       accounts%ROWTYPE;
  sec     JSONB := app_cfg('security');
  v_token TEXT;
  v_exp   TIMESTAMPTZ;
  v_left  INTEGER;
BEGIN
  SELECT * INTO a FROM accounts WHERE username = lower(btrim(COALESCE(p_username, '')));

  IF NOT FOUND THEN
    RETURN jsonb_build_object('ok', FALSE, 'error', 'INVALID_CREDENTIALS',
                              'message', 'We could not find that username, or the password is wrong.');
  END IF;

  IF NOT a.is_active THEN
    RETURN jsonb_build_object('ok', FALSE, 'error', 'ACCOUNT_DISABLED',
                              'message', 'This account has been disabled. Ask the admin to re-enable it.');
  END IF;

  IF a.locked_until IS NOT NULL AND a.locked_until > NOW() THEN
    RETURN jsonb_build_object('ok', FALSE, 'error', 'LOCKED',
      'message', 'Too many failed attempts. Try again in ' ||
                 GREATEST(1, CEIL(EXTRACT(EPOCH FROM (a.locked_until - NOW())) / 60))::INTEGER || ' minute(s).');
  END IF;

  IF a.password_hash IS NOT NULL THEN
    IF COALESCE(p_password, '') = '' OR crypt(p_password, a.password_hash) <> a.password_hash THEN
      UPDATE accounts
         SET failed_attempts = failed_attempts + 1,
             locked_until = CASE WHEN failed_attempts + 1 >= COALESCE((sec ->> 'max_attempts')::INTEGER, 8)
                                 THEN NOW() + make_interval(mins => COALESCE((sec ->> 'lockout_minutes')::INTEGER, 15))
                                 ELSE NULL END
       WHERE id = a.id
      RETURNING COALESCE((sec ->> 'max_attempts')::INTEGER, 8) - failed_attempts INTO v_left;

      INSERT INTO audit_log (account_id, actor, actor_role, action, entity, entity_id, detail, ip)
      VALUES (a.id, a.username, a.role, 'login_failed', 'account', a.username,
              jsonb_build_object('attempts_left', GREATEST(v_left, 0)), app_client_ip());

      RETURN jsonb_build_object('ok', FALSE, 'error', 'INVALID_CREDENTIALS',
        'password_required', TRUE,
        'message', CASE WHEN COALESCE(p_password, '') = ''
                        THEN 'This account is protected by a password.'
                        ELSE 'Wrong password. ' || GREATEST(v_left, 0)::TEXT || ' attempt(s) left before a temporary lock.' END);
    END IF;
  ELSIF COALESCE(p_password, '') <> '' THEN
    -- account has no password yet: a typed password is simply ignored
    NULL;
  END IF;

  v_token := encode(gen_random_bytes(32), 'hex');
  v_exp   := CASE WHEN COALESCE(p_remember, FALSE)
                  THEN NOW() + make_interval(days => COALESCE((sec ->> 'remember_days')::INTEGER, 30))
                  ELSE NOW() + make_interval(hours => COALESCE((sec ->> 'session_hours')::INTEGER, 12)) END;

  INSERT INTO sessions (account_id, token_hash, expires_at, remember, user_agent, ip)
  VALUES (a.id, app_hash_token(v_token), v_exp, COALESCE(p_remember, FALSE),
          left(COALESCE(p_agent, ''), 400), app_client_ip());

  UPDATE accounts
     SET failed_attempts = 0, locked_until = NULL, last_login_at = NOW(),
         last_login_ip = app_client_ip(), login_count = COALESCE(login_count, 0) + 1
   WHERE id = a.id;

  PERFORM app_log(a, 'login', 'account', a.username, jsonb_build_object('remember', COALESCE(p_remember, FALSE)));

  RETURN jsonb_build_object(
    'ok', TRUE,
    'token', v_token,
    'expires_at', v_exp,
    'account', app_account_json(a.id),
    'must_set_password', (a.password_hash IS NULL AND a.role = 'admin'),
    'no_password', (a.password_hash IS NULL)
  );
END $fn$;

CREATE OR REPLACE FUNCTION api_session(p_token TEXT) RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE a accounts%ROWTYPE;
BEGIN
  a := app_auth(p_token);
  IF a.id IS NULL THEN RETURN jsonb_build_object('ok', FALSE, 'error', 'AUTH_REQUIRED'); END IF;
  RETURN jsonb_build_object(
    'ok', TRUE,
    'account', app_account_json(a.id),
    'editorial', app_cfg('editorial'),
    'must_set_password', (a.password_hash IS NULL AND a.role = 'admin')
  );
END $fn$;

CREATE OR REPLACE FUNCTION api_logout(p_token TEXT) RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE a accounts%ROWTYPE;
BEGIN
  a := app_auth(p_token);
  UPDATE sessions SET revoked_at = NOW(), revoke_reason = 'logout'
   WHERE token_hash = app_hash_token(p_token) AND revoked_at IS NULL;
  IF a.id IS NOT NULL THEN PERFORM app_log(a, 'logout', 'account', a.username); END IF;
  RETURN jsonb_build_object('ok', TRUE);
END $fn$;

-- Set / change / REMOVE your own password.
-- p_new = NULL or '' removes the password (passwordless sign-in).
CREATE OR REPLACE FUNCTION api_set_password(p_token TEXT, p_current TEXT DEFAULT NULL,
                                            p_new TEXT DEFAULT NULL, p_revoke_others BOOLEAN DEFAULT TRUE)
RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE
  a    accounts%ROWTYPE;
  sec  JSONB := app_cfg('security');
  v_min INTEGER;
BEGIN
  a := app_require(p_token);
  v_min := COALESCE((sec ->> 'min_password_length')::INTEGER, 6);

  IF a.password_hash IS NOT NULL THEN
    IF COALESCE(p_current, '') = '' OR crypt(p_current, a.password_hash) <> a.password_hash THEN
      RETURN jsonb_build_object('ok', FALSE, 'error', 'BAD_CURRENT', 'message', 'Your current password is not correct.');
    END IF;
  END IF;

  IF COALESCE(p_new, '') = '' THEN
    IF NOT COALESCE((sec ->> 'allow_passwordless')::BOOLEAN, TRUE) THEN
      RETURN jsonb_build_object('ok', FALSE, 'error', 'PASSWORD_REQUIRED',
                                'message', 'Passwordless sign-in is turned off for this site.');
    END IF;
    UPDATE accounts SET password_hash = NULL, password_set_at = NULL WHERE id = a.id;
    PERFORM app_log(a, 'password_removed', 'account', a.username);
  ELSE
    IF length(p_new) < v_min THEN
      RETURN jsonb_build_object('ok', FALSE, 'error', 'TOO_SHORT',
                                'message', 'Use at least ' || v_min || ' characters.');
    END IF;
    UPDATE accounts SET password_hash = crypt(p_new, gen_salt('bf', 10)), password_set_at = NOW() WHERE id = a.id;
    PERFORM app_log(a, 'password_set', 'account', a.username);
  END IF;

  IF COALESCE(p_revoke_others, TRUE) THEN
    UPDATE sessions SET revoked_at = NOW(), revoke_reason = 'password_change'
     WHERE account_id = a.id AND revoked_at IS NULL AND token_hash <> app_hash_token(p_token);
  END IF;

  RETURN jsonb_build_object('ok', TRUE, 'account', app_account_json(a.id),
                            'message', CASE WHEN COALESCE(p_new, '') = ''
                                            THEN 'Password removed. You can now sign in without one.'
                                            ELSE 'Password updated.' END);
END $fn$;

-- Admin sets / removes the password of any account (its own included).
CREATE OR REPLACE FUNCTION api_admin_set_password(p_token TEXT, p_account_id UUID,
                                                  p_new TEXT DEFAULT NULL, p_revoke BOOLEAN DEFAULT TRUE)
RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE
  a     accounts%ROWTYPE;
  t     accounts%ROWTYPE;
  sec   JSONB := app_cfg('security');
  v_min INTEGER;
BEGIN
  a := app_require(p_token, 'admin');
  SELECT * INTO t FROM accounts WHERE id = p_account_id;
  IF NOT FOUND THEN RETURN jsonb_build_object('ok', FALSE, 'error', 'NOT_FOUND', 'message', 'Account not found.'); END IF;

  v_min := COALESCE((sec ->> 'min_password_length')::INTEGER, 6);

  IF COALESCE(p_new, '') = '' THEN
    UPDATE accounts SET password_hash = NULL, password_set_at = NULL WHERE id = t.id;
    PERFORM app_log(a, 'password_removed', 'account', t.username, jsonb_build_object('by_admin', TRUE));
  ELSE
    IF length(p_new) < v_min THEN
      RETURN jsonb_build_object('ok', FALSE, 'error', 'TOO_SHORT', 'message', 'Use at least ' || v_min || ' characters.');
    END IF;
    UPDATE accounts SET password_hash = crypt(p_new, gen_salt('bf', 10)), password_set_at = NOW() WHERE id = t.id;
    PERFORM app_log(a, 'password_set', 'account', t.username, jsonb_build_object('by_admin', TRUE));
  END IF;

  IF COALESCE(p_revoke, TRUE) THEN
    UPDATE sessions SET revoked_at = NOW(), revoke_reason = 'admin_password_change'
     WHERE account_id = t.id AND revoked_at IS NULL AND token_hash <> app_hash_token(p_token);
  END IF;

  RETURN jsonb_build_object('ok', TRUE, 'account', app_account_json(t.id),
                            'message', CASE WHEN COALESCE(p_new, '') = ''
                                            THEN t.username || ' can now sign in without a password.'
                                            ELSE 'Password saved for ' || t.username || '.' END);
END $fn$;

CREATE OR REPLACE FUNCTION api_revoke_session(p_token TEXT, p_session_id UUID) RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE a accounts%ROWTYPE; n INTEGER;
BEGIN
  a := app_require(p_token);
  UPDATE sessions SET revoked_at = NOW(), revoke_reason = 'revoked'
   WHERE id = p_session_id AND revoked_at IS NULL
     AND (a.role = 'admin' OR account_id = a.id);
  GET DIAGNOSTICS n = ROW_COUNT;
  PERFORM app_log(a, 'session_revoked', 'session', p_session_id::TEXT);
  RETURN jsonb_build_object('ok', n > 0);
END $fn$;

CREATE OR REPLACE FUNCTION api_revoke_all_sessions(p_token TEXT, p_account_id UUID DEFAULT NULL) RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE a accounts%ROWTYPE; v_target UUID; n INTEGER;
BEGIN
  a := app_require(p_token);
  v_target := COALESCE(p_account_id, a.id);
  IF a.role <> 'admin' AND v_target <> a.id THEN RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501'; END IF;
  UPDATE sessions SET revoked_at = NOW(), revoke_reason = 'revoke_all'
   WHERE account_id = v_target AND revoked_at IS NULL AND token_hash <> app_hash_token(p_token);
  GET DIAGNOSTICS n = ROW_COUNT;
  PERFORM app_log(a, 'sessions_revoked', 'account', v_target::TEXT, jsonb_build_object('count', n));
  RETURN jsonb_build_object('ok', TRUE, 'count', n);
END $fn$;

-- =====================================================================
-- 7. READ API  (role aware)
-- =====================================================================

CREATE OR REPLACE FUNCTION api_list(p_token TEXT, p_entity TEXT, p_options JSONB DEFAULT '{}')
RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE
  a       accounts%ROWTYPE;
  v       JSONB := '[]'::JSONB;
  v_admin BOOLEAN;
  v_target UUID;
  v_post  TEXT;
BEGIN
  a := app_require(p_token);
  v_admin := (a.role = 'admin');

  IF p_entity = 'posts' THEN
    PERFORM app_publish_due();
    SELECT COALESCE(jsonb_agg(x ORDER BY (x ->> 'sort_ts') DESC), '[]'::JSONB) INTO v
      FROM (
        SELECT (to_jsonb(p) - 'content') || jsonb_build_object(
                 'author_name',    COALESCE(au.name, 'Unassigned'),
                 'category_title', COALESCE(c.title, p.category),
                 'subtopic_title', COALESCE(s.title, p.subtopic),
                 'sort_ts',        COALESCE(p.updated_at, p.created_at)) AS x
          FROM posts p
          LEFT JOIN authors au    ON au.id = p.author
          LEFT JOIN categories c  ON c.id = p.category
          LEFT JOIN subtopics s   ON s.id = p.subtopic
         WHERE v_admin OR p.author = a.author_id
      ) q;

  ELSIF p_entity = 'authors' THEN
    SELECT COALESCE(jsonb_agg(x ORDER BY (x #>> '{author,name}')), '[]'::JSONB) INTO v
      FROM (
        SELECT jsonb_build_object(
                 'author',  to_jsonb(au),
                 'account', CASE WHEN ac.id IS NULL THEN NULL ELSE jsonb_build_object(
                              'id', ac.id, 'username', ac.username,
                              'has_password', ac.password_hash IS NOT NULL,
                              'password_set_at', ac.password_set_at,
                              'is_active', ac.is_active, 'locked_until', ac.locked_until,
                              'last_login_at', ac.last_login_at, 'login_count', ac.login_count) END,
                 'stats',   jsonb_build_object('total', st.total, 'published', st.published,
                                               'pending', st.pending, 'views', st.views)) AS x
          FROM authors au
          LEFT JOIN accounts ac ON ac.author_id = au.id
          LEFT JOIN LATERAL (
                SELECT count(*) AS total,
                       count(*) FILTER (WHERE status = 'published') AS published,
                       count(*) FILTER (WHERE status IN ('draft','review','scheduled')) AS pending,
                       COALESCE(sum(views), 0) AS views
                  FROM posts WHERE author = au.id) st ON TRUE
         WHERE v_admin OR au.id = a.author_id
      ) q;

  ELSIF p_entity = 'categories' THEN
    SELECT COALESCE(jsonb_agg(to_jsonb(c) ORDER BY c.sort_order, c.title), '[]'::JSONB) INTO v FROM categories c;

  ELSIF p_entity = 'subtopics' THEN
    SELECT COALESCE(jsonb_agg(to_jsonb(s) ORDER BY s.sort_order, s.title), '[]'::JSONB) INTO v FROM subtopics s;

  ELSIF p_entity = 'downloads' THEN
    IF NOT v_admin THEN RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501'; END IF;
    SELECT COALESCE(jsonb_agg(to_jsonb(d) ORDER BY d.sort_order, d.name), '[]'::JSONB) INTO v FROM downloads d;

  ELSIF p_entity = 'glossary' THEN
    IF NOT v_admin THEN RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501'; END IF;
    SELECT COALESCE(jsonb_agg(to_jsonb(g) ORDER BY g.word), '[]'::JSONB) INTO v FROM glossary g;

  ELSIF p_entity = 'faqs' THEN
    IF NOT v_admin THEN RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501'; END IF;
    SELECT COALESCE(jsonb_agg(to_jsonb(f) ORDER BY f.sort_order, f.id), '[]'::JSONB) INTO v FROM faqs f;

  ELSIF p_entity = 'messages' THEN
    IF NOT v_admin THEN RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501'; END IF;
    SELECT COALESCE(jsonb_agg(to_jsonb(m) ORDER BY m.created_at DESC), '[]'::JSONB) INTO v FROM contact_messages m;

  ELSIF p_entity = 'subscribers' THEN
    IF NOT v_admin THEN RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501'; END IF;
    SELECT COALESCE(jsonb_agg(to_jsonb(s) ORDER BY s.created_at DESC), '[]'::JSONB) INTO v FROM newsletter_subscribers s;

  ELSIF p_entity = 'accounts' THEN
    IF NOT v_admin THEN RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501'; END IF;
    SELECT COALESCE(jsonb_agg(jsonb_build_object(
             'id', ac.id, 'username', ac.username, 'role', ac.role, 'author_id', ac.author_id,
             'display_name', COALESCE(au.name, initcap(ac.username)),
             'has_password', ac.password_hash IS NOT NULL, 'password_set_at', ac.password_set_at,
             'is_active', ac.is_active, 'locked_until', ac.locked_until,
             'last_login_at', ac.last_login_at, 'login_count', ac.login_count,
             'created_at', ac.created_at,
             'active_sessions', (SELECT count(*) FROM sessions s
                                  WHERE s.account_id = ac.id AND s.revoked_at IS NULL AND s.expires_at > NOW())
           ) ORDER BY ac.role, ac.username), '[]'::JSONB) INTO v
      FROM accounts ac LEFT JOIN authors au ON au.id = ac.author_id;

  ELSIF p_entity = 'audit' THEN
    IF NOT v_admin THEN
      SELECT COALESCE(jsonb_agg(to_jsonb(l) ORDER BY l.created_at DESC), '[]'::JSONB) INTO v
        FROM (SELECT * FROM audit_log WHERE account_id = a.id ORDER BY created_at DESC LIMIT 100) l;
    ELSE
      SELECT COALESCE(jsonb_agg(to_jsonb(l) ORDER BY l.created_at DESC), '[]'::JSONB) INTO v
        FROM (SELECT * FROM audit_log ORDER BY created_at DESC
               LIMIT COALESCE((p_options ->> 'limit')::INTEGER, 300)) l;
    END IF;

  ELSIF p_entity = 'sessions' THEN
    v_target := COALESCE((p_options ->> 'account_id')::UUID, a.id);
    IF NOT v_admin AND v_target <> a.id THEN RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501'; END IF;
    SELECT COALESCE(jsonb_agg(jsonb_build_object(
             'id', s.id, 'created_at', s.created_at, 'last_seen_at', s.last_seen_at,
             'expires_at', s.expires_at, 'remember', s.remember, 'user_agent', s.user_agent,
             'ip', s.ip, 'revoked_at', s.revoked_at,
             'current', s.token_hash = app_hash_token(p_token)
           ) ORDER BY s.last_seen_at DESC), '[]'::JSONB) INTO v
      FROM sessions s
     WHERE s.account_id = v_target AND s.revoked_at IS NULL AND s.expires_at > NOW();

  ELSIF p_entity = 'revisions' THEN
    v_post := p_options ->> 'post_id';
    IF NOT v_admin AND NOT EXISTS (SELECT 1 FROM posts WHERE id = v_post AND author = a.author_id) THEN
      RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501';
    END IF;
    SELECT COALESCE(jsonb_agg(jsonb_build_object(
             'id', r.id, 'created_at', r.created_at, 'title', r.title,
             'excerpt', r.excerpt, 'snapshot', r.snapshot,
             'chars', length(COALESCE(r.content, '')),
             'saved_by_name', COALESCE(r.saved_by_name, ac.username, 'system')
           ) ORDER BY r.created_at DESC), '[]'::JSONB) INTO v
      FROM post_revisions r LEFT JOIN accounts ac ON ac.id = r.saved_by
     WHERE r.post_id = v_post;

  ELSIF p_entity = 'media' THEN
    SELECT COALESCE(jsonb_agg(to_jsonb(m) ORDER BY m.created_at DESC), '[]'::JSONB) INTO v
      FROM media m WHERE v_admin OR m.uploaded_by = a.id;

  ELSE
    RAISE EXCEPTION 'UNKNOWN_ENTITY: %', p_entity USING ERRCODE = '22023';
  END IF;

  RETURN v;
END $fn$;

CREATE OR REPLACE FUNCTION api_get(p_token TEXT, p_entity TEXT, p_id TEXT DEFAULT NULL)
RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE
  a       accounts%ROWTYPE;
  v       JSONB;
  v_admin BOOLEAN;
BEGIN
  a := app_require(p_token);
  v_admin := (a.role = 'admin');

  IF p_entity = 'post' THEN
    SELECT to_jsonb(p) INTO v FROM posts p WHERE p.id = p_id;
    IF v IS NULL THEN RETURN NULL; END IF;
    IF NOT v_admin AND (v ->> 'author') IS DISTINCT FROM a.author_id THEN
      RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501';
    END IF;

  ELSIF p_entity = 'author' THEN
    IF NOT v_admin AND p_id IS DISTINCT FROM a.author_id THEN
      RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501';
    END IF;
    SELECT to_jsonb(au) INTO v FROM authors au WHERE au.id = p_id;

  ELSIF p_entity = 'settings' THEN
    IF NOT v_admin THEN RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501'; END IF;
    SELECT to_jsonb(s) INTO v FROM site_settings s WHERE s.id = 1;
    v := COALESCE(v, '{}'::JSONB) || jsonb_build_object('editorial', app_cfg('editorial'),
                                                        'security',  app_cfg('security'));

  ELSIF p_entity = 'about' THEN
    IF NOT v_admin THEN RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501'; END IF;
    SELECT to_jsonb(ab) INTO v FROM about ab WHERE ab.id = 1;

  ELSIF p_entity = 'download' THEN
    IF NOT v_admin THEN RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501'; END IF;
    SELECT to_jsonb(d) INTO v FROM downloads d WHERE d.id = p_id;

  ELSIF p_entity = 'glossary' THEN
    IF NOT v_admin THEN RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501'; END IF;
    SELECT to_jsonb(g) INTO v FROM glossary g WHERE g.id = p_id::INTEGER;

  ELSIF p_entity = 'faq' THEN
    IF NOT v_admin THEN RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501'; END IF;
    SELECT to_jsonb(f) INTO v FROM faqs f WHERE f.id = p_id::INTEGER;

  ELSIF p_entity = 'revision' THEN
    SELECT to_jsonb(r) INTO v FROM post_revisions r WHERE r.id = p_id::BIGINT;
    IF v IS NOT NULL AND NOT v_admin
       AND NOT EXISTS (SELECT 1 FROM posts WHERE id = v ->> 'post_id' AND author = a.author_id) THEN
      RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501';
    END IF;

  ELSE
    RAISE EXCEPTION 'UNKNOWN_ENTITY: %', p_entity USING ERRCODE = '22023';
  END IF;

  RETURN v;
END $fn$;

-- Dashboard numbers, role aware -----------------------------------------
CREATE OR REPLACE FUNCTION api_stats(p_token TEXT) RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE a accounts%ROWTYPE; v JSONB; v_admin BOOLEAN; v_mine TEXT;
BEGIN
  a := app_require(p_token);
  v_admin := (a.role = 'admin');
  v_mine  := a.author_id;
  PERFORM app_publish_due();

  SELECT jsonb_build_object(
    'posts_total',     count(*),
    'posts_published', count(*) FILTER (WHERE status = 'published'),
    'posts_draft',     count(*) FILTER (WHERE status = 'draft'),
    'posts_review',    count(*) FILTER (WHERE status = 'review'),
    'posts_scheduled', count(*) FILTER (WHERE status = 'scheduled'),
    'posts_archived',  count(*) FILTER (WHERE status = 'archived'),
    'posts_featured',  count(*) FILTER (WHERE is_featured),
    'views_total',     COALESCE(sum(views), 0),
    'words_total',     COALESCE(sum(word_count), 0)
  ) INTO v FROM posts WHERE v_admin OR author = v_mine;

  v := v || jsonb_build_object(
    'authors',      (SELECT count(*) FROM authors),
    'categories',   (SELECT count(*) FROM categories),
    'subtopics',    (SELECT count(*) FROM subtopics),
    'views_7d',     (SELECT COALESCE(sum(dv.views), 0) FROM post_daily_views dv
                       JOIN posts p ON p.id = dv.post_id
                      WHERE dv.day > CURRENT_DATE - 7 AND (v_admin OR p.author = v_mine)),
    'recent_posts', (SELECT COALESCE(jsonb_agg(x ORDER BY (x ->> 'ts') DESC), '[]'::JSONB) FROM (
                       SELECT jsonb_build_object('id', p.id, 'title', p.title, 'status', p.status,
                                                 'author_name', COALESCE(au.name, 'Unassigned'),
                                                 'views', p.views,
                                                 'ts', COALESCE(p.updated_at, p.created_at)) AS x
                         FROM posts p LEFT JOIN authors au ON au.id = p.author
                        WHERE v_admin OR p.author = v_mine
                        ORDER BY COALESCE(p.updated_at, p.created_at) DESC LIMIT 8) t),
    'top_posts',    (SELECT COALESCE(jsonb_agg(x ORDER BY (x ->> 'views')::INTEGER DESC), '[]'::JSONB) FROM (
                       SELECT jsonb_build_object('id', p.id, 'title', p.title, 'views', COALESCE(p.views, 0)) AS x
                         FROM posts p
                        WHERE (v_admin OR p.author = v_mine) AND p.status = 'published'
                        ORDER BY COALESCE(p.views, 0) DESC LIMIT 5) t)
  );

  IF v_admin THEN
    v := v || jsonb_build_object(
      'messages_unread', (SELECT count(*) FROM contact_messages WHERE NOT is_read),
      'messages_total',  (SELECT count(*) FROM contact_messages),
      'subscribers',     (SELECT count(*) FROM newsletter_subscribers WHERE is_active),
      'downloads',       (SELECT count(*) FROM downloads),
      'glossary',        (SELECT count(*) FROM glossary),
      'faqs',            (SELECT count(*) FROM faqs),
      'accounts',        (SELECT count(*) FROM accounts),
      'accounts_nopass', (SELECT count(*) FROM accounts WHERE password_hash IS NULL),
      'active_sessions', (SELECT count(*) FROM sessions WHERE revoked_at IS NULL AND expires_at > NOW()),
      'pending_review',  (SELECT COALESCE(jsonb_agg(jsonb_build_object(
                              'id', p.id, 'title', p.title, 'author_name', COALESCE(au.name, '—'),
                              'submitted_at', p.submitted_at)), '[]'::JSONB)
                            FROM posts p LEFT JOIN authors au ON au.id = p.author
                           WHERE p.status = 'review'),
      'activity',        (SELECT COALESCE(jsonb_agg(jsonb_build_object(
                              'actor', l.actor, 'action', l.action, 'entity', l.entity,
                              'entity_id', l.entity_id, 'created_at', l.created_at)), '[]'::JSONB)
                            FROM (SELECT * FROM audit_log ORDER BY created_at DESC LIMIT 10) l)
    );
  END IF;

  RETURN v || jsonb_build_object('role', a.role, 'generated_at', NOW());
END $fn$;

-- =====================================================================
-- 8. WRITE API — POSTS
-- =====================================================================

CREATE OR REPLACE FUNCTION api_save_post(p_token TEXT, p_data JSONB) RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE
  a        accounts%ROWTYPE;
  old      posts%ROWTYPE;
  ed       JSONB := app_cfg('editorial');
  v_id     TEXT;
  v_new    BOOLEAN;
  v_author TEXT;
  v_status TEXT;
  v_sched  TIMESTAMPTZ;
  v_note   TEXT := NULL;
  v_admin  BOOLEAN;
  v_row    JSONB;
BEGIN
  a := app_require(p_token);
  v_admin := (a.role = 'admin');

  v_id := app_slug(COALESCE(NULLIF(btrim(p_data ->> 'id'), ''), p_data ->> 'title'));
  IF v_id = '' OR v_id IS NULL THEN
    RETURN jsonb_build_object('ok', FALSE, 'error', 'MISSING_ID', 'message', 'A URL slug is required.');
  END IF;
  IF COALESCE(btrim(p_data ->> 'title'), '') = '' THEN
    RETURN jsonb_build_object('ok', FALSE, 'error', 'MISSING_TITLE', 'message', 'A title is required.');
  END IF;
  IF COALESCE(btrim(p_data ->> 'category'), '') = '' THEN
    RETURN jsonb_build_object('ok', FALSE, 'error', 'MISSING_CATEGORY', 'message', 'Choose a category.');
  END IF;

  SELECT * INTO old FROM posts WHERE id = v_id;
  v_new := NOT FOUND;

  -- the slug of an existing post was edited
  IF COALESCE(p_data ->> 'was_id', '') <> '' AND (p_data ->> 'was_id') <> v_id THEN
    IF NOT v_new THEN
      RETURN jsonb_build_object('ok', FALSE, 'error', 'SLUG_TAKEN',
                                'message', 'Another post already uses the slug "' || v_id || '".');
    END IF;
    SELECT * INTO old FROM posts WHERE id = p_data ->> 'was_id';
    IF FOUND THEN
      IF NOT v_admin AND old.author IS DISTINCT FROM a.author_id THEN
        RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501';
      END IF;
      UPDATE posts          SET id      = v_id WHERE id      = p_data ->> 'was_id';
      UPDATE post_revisions SET post_id = v_id WHERE post_id = p_data ->> 'was_id';
      SELECT * INTO old FROM posts WHERE id = v_id;
      v_new := FALSE;
    END IF;
  END IF;

  -- who owns the post
  IF v_admin THEN
    v_author := NULLIF(btrim(COALESCE(p_data ->> 'author', '')), '');
    IF v_author IS NULL THEN
      RETURN jsonb_build_object('ok', FALSE, 'error', 'MISSING_AUTHOR', 'message', 'Choose the author to publish as.');
    END IF;
  ELSE
    v_author := a.author_id;
    IF NOT v_new AND old.author IS DISTINCT FROM a.author_id THEN
      RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501';
    END IF;
  END IF;

  -- workflow rules
  v_status := COALESCE(NULLIF(p_data ->> 'status', ''), 'draft');
  IF v_status NOT IN ('draft','review','scheduled','published','archived') THEN v_status := 'draft'; END IF;
  v_sched := NULLIF(p_data ->> 'scheduled_for', '')::TIMESTAMPTZ;

  IF NOT v_admin THEN
    IF v_status = 'published' AND (COALESCE((ed ->> 'require_approval')::BOOLEAN, FALSE)
                                   OR NOT COALESCE((ed ->> 'authors_can_publish')::BOOLEAN, TRUE)) THEN
      v_status := 'review';
      v_note := 'Your post was sent to the admin for review.';
    END IF;
    IF v_status = 'scheduled' AND NOT COALESCE((ed ->> 'authors_can_schedule')::BOOLEAN, TRUE) THEN
      v_status := 'draft';
      v_note := 'Scheduling is reserved for the admin — saved as a draft.';
    END IF;
  END IF;

  IF v_status = 'scheduled' THEN
    IF v_sched IS NULL THEN
      RETURN jsonb_build_object('ok', FALSE, 'error', 'MISSING_SCHEDULE', 'message', 'Pick the date and time to publish.');
    END IF;
    IF v_sched <= NOW() THEN v_status := 'published'; v_sched := NULL; END IF;
  ELSE
    v_sched := NULL;
  END IF;

  INSERT INTO posts (id, title, excerpt, content, category, subtopic, author, published_date,
                     tags, featured_image, featured_image_alt, is_featured, status, scheduled_for,
                     seo, created_by, updated_by, submitted_at)
  VALUES (v_id,
          btrim(p_data ->> 'title'),
          NULLIF(p_data ->> 'excerpt', ''),
          COALESCE(p_data ->> 'content', ''),
          p_data ->> 'category',
          NULLIF(p_data ->> 'subtopic', ''),
          v_author,
          COALESCE(NULLIF(p_data ->> 'published_date', '')::DATE, CURRENT_DATE),
          app_tags(p_data -> 'tags'),
          NULLIF(p_data ->> 'featured_image', ''),
          NULLIF(p_data ->> 'featured_image_alt', ''),
          COALESCE((p_data ->> 'is_featured')::BOOLEAN, FALSE) AND v_admin,
          v_status, v_sched,
          COALESCE(p_data -> 'seo', '{}'::JSONB),
          a.id, a.id,
          CASE WHEN v_status = 'review' THEN NOW() END)
  ON CONFLICT (id) DO UPDATE SET
      title              = EXCLUDED.title,
      excerpt            = EXCLUDED.excerpt,
      content            = EXCLUDED.content,
      category           = EXCLUDED.category,
      subtopic           = EXCLUDED.subtopic,
      author             = EXCLUDED.author,
      published_date     = EXCLUDED.published_date,
      tags               = EXCLUDED.tags,
      featured_image     = EXCLUDED.featured_image,
      featured_image_alt = EXCLUDED.featured_image_alt,
      is_featured        = CASE WHEN v_admin THEN EXCLUDED.is_featured ELSE posts.is_featured END,
      status             = EXCLUDED.status,
      scheduled_for      = EXCLUDED.scheduled_for,
      seo                = EXCLUDED.seo,
      updated_by         = EXCLUDED.updated_by,
      submitted_at       = CASE WHEN EXCLUDED.status = 'review' AND posts.status <> 'review'
                                THEN NOW() ELSE posts.submitted_at END;

  PERFORM app_log(a, CASE WHEN v_new THEN 'post_created' ELSE 'post_updated' END, 'post', v_id,
                  jsonb_build_object('status', v_status, 'author', v_author));

  SELECT to_jsonb(p) INTO v_row FROM posts p WHERE p.id = v_id;
  RETURN jsonb_build_object('ok', TRUE, 'id', v_id, 'post', v_row, 'status', v_status,
                            'message', COALESCE(v_note, CASE WHEN v_new THEN 'Post created.' ELSE 'Post saved.' END));
END $fn$;

CREATE OR REPLACE FUNCTION api_post_action(p_token TEXT, p_id TEXT, p_action TEXT, p_value JSONB DEFAULT '{}')
RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE
  a       accounts%ROWTYPE;
  p       posts%ROWTYPE;
  ed      JSONB := app_cfg('editorial');
  v_admin BOOLEAN;
  v_new   TEXT;
  r       post_revisions%ROWTYPE;
  v_msg   TEXT;
BEGIN
  a := app_require(p_token);
  v_admin := (a.role = 'admin');

  SELECT * INTO p FROM posts WHERE id = p_id;
  IF NOT FOUND THEN RETURN jsonb_build_object('ok', FALSE, 'error', 'NOT_FOUND', 'message', 'Post not found.'); END IF;
  IF NOT v_admin AND p.author IS DISTINCT FROM a.author_id THEN
    RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501';
  END IF;
  IF NOT v_admin AND p_action IN ('approve','reject','feature','unfeature') THEN
    RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501';
  END IF;

  CASE p_action
    WHEN 'publish' THEN
      IF NOT v_admin AND (COALESCE((ed ->> 'require_approval')::BOOLEAN, FALSE)
                          OR NOT COALESCE((ed ->> 'authors_can_publish')::BOOLEAN, TRUE)) THEN
        UPDATE posts SET status = 'review', submitted_at = NOW(), updated_by = a.id WHERE id = p_id;
        v_msg := 'Sent to the admin for review.';
      ELSE
        UPDATE posts SET status = 'published', updated_by = a.id, review_note = NULL WHERE id = p_id;
        v_msg := 'Post published.';
      END IF;

    WHEN 'unpublish' THEN
      UPDATE posts SET status = 'draft', updated_by = a.id WHERE id = p_id;
      v_msg := 'Moved back to drafts.';

    WHEN 'submit' THEN
      UPDATE posts SET status = 'review', submitted_at = NOW(), updated_by = a.id WHERE id = p_id;
      v_msg := 'Submitted for review.';

    WHEN 'approve' THEN
      UPDATE posts SET status = 'published', reviewed_at = NOW(), review_note = NULL, updated_by = a.id WHERE id = p_id;
      v_msg := 'Approved and published.';

    WHEN 'reject' THEN
      UPDATE posts SET status = 'draft', reviewed_at = NOW(),
                       review_note = NULLIF(p_value ->> 'note', ''), updated_by = a.id WHERE id = p_id;
      v_msg := 'Sent back to the author.';

    WHEN 'archive' THEN
      UPDATE posts SET status = 'archived', updated_by = a.id WHERE id = p_id;
      v_msg := 'Post archived.';

    WHEN 'restore' THEN
      UPDATE posts SET status = 'draft', updated_by = a.id WHERE id = p_id;
      v_msg := 'Post restored as a draft.';

    WHEN 'feature' THEN
      UPDATE posts SET is_featured = TRUE, updated_by = a.id WHERE id = p_id;
      v_msg := 'Added to featured.';

    WHEN 'unfeature' THEN
      UPDATE posts SET is_featured = FALSE, updated_by = a.id WHERE id = p_id;
      v_msg := 'Removed from featured.';

    WHEN 'schedule' THEN
      UPDATE posts SET status = 'scheduled', scheduled_for = (p_value ->> 'at')::TIMESTAMPTZ, updated_by = a.id
       WHERE id = p_id;
      v_msg := 'Scheduled.';

    WHEN 'delete' THEN
      IF NOT v_admin AND NOT COALESCE((ed ->> 'authors_can_delete')::BOOLEAN, TRUE) THEN
        RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501';
      END IF;
      DELETE FROM posts WHERE id = p_id;
      DELETE FROM post_revisions WHERE post_id = p_id;
      v_msg := 'Post deleted.';

    WHEN 'duplicate' THEN
      v_new := app_slug(p_id || '-copy');
      WHILE EXISTS (SELECT 1 FROM posts WHERE id = v_new) LOOP
        v_new := v_new || '-' || floor(random() * 90 + 10)::TEXT;
      END LOOP;
      INSERT INTO posts (id, title, excerpt, content, category, subtopic, author, published_date, tags,
                         featured_image, featured_image_alt, is_featured, status, seo, created_by, updated_by)
      VALUES (v_new, p.title || ' (copy)', p.excerpt, p.content, p.category, p.subtopic,
              CASE WHEN v_admin THEN p.author ELSE a.author_id END, CURRENT_DATE, p.tags,
              p.featured_image, p.featured_image_alt, FALSE, 'draft', p.seo, a.id, a.id);
      v_msg := 'Duplicated as a draft.';

    WHEN 'restore_revision' THEN
      SELECT * INTO r FROM post_revisions WHERE id = (p_value ->> 'revision_id')::BIGINT AND post_id = p_id;
      IF NOT FOUND THEN RETURN jsonb_build_object('ok', FALSE, 'error', 'NOT_FOUND', 'message', 'Revision not found.'); END IF;
      UPDATE posts SET title = r.title, excerpt = r.excerpt, content = r.content, updated_by = a.id WHERE id = p_id;
      v_msg := 'Revision restored.';

    ELSE
      RETURN jsonb_build_object('ok', FALSE, 'error', 'UNKNOWN_ACTION', 'message', 'Unknown action.');
  END CASE;

  PERFORM app_log(a, 'post_' || p_action, 'post', p_id, p_value);
  RETURN jsonb_build_object('ok', TRUE, 'message', v_msg, 'new_id', v_new);
END $fn$;

-- =====================================================================
-- 9. WRITE API — AUTHORS & ACCOUNTS
-- =====================================================================

-- Admin: create or edit any author (optionally with a login).
-- Author: edit only their own public profile.
CREATE OR REPLACE FUNCTION api_save_author(p_token TEXT, p_data JSONB) RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE
  a        accounts%ROWTYPE;
  v_admin  BOOLEAN;
  v_id     TEXT;
  v_new    BOOLEAN;
  v_user   TEXT;
  v_acc_id UUID;
  v_row    JSONB;
BEGIN
  a := app_require(p_token);
  v_admin := (a.role = 'admin');

  IF v_admin THEN
    v_id := app_slug(COALESCE(NULLIF(btrim(p_data ->> 'id'), ''), p_data ->> 'name'));
  ELSE
    v_id := a.author_id;
  END IF;

  IF COALESCE(v_id, '') = '' THEN
    RETURN jsonb_build_object('ok', FALSE, 'error', 'MISSING_ID', 'message', 'An author ID is required.');
  END IF;
  IF COALESCE(btrim(p_data ->> 'name'), '') = '' THEN
    RETURN jsonb_build_object('ok', FALSE, 'error', 'MISSING_NAME', 'message', 'A display name is required.');
  END IF;

  v_new := NOT EXISTS (SELECT 1 FROM authors WHERE id = v_id);
  IF v_new AND NOT v_admin THEN RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501'; END IF;

  INSERT INTO authors (id, name, avatar, bio, role, specialization, email, phone, website,
                       location, tagline, cover_image, expertise, socials, is_visible, sort_order)
  VALUES (v_id,
          btrim(p_data ->> 'name'),
          NULLIF(p_data ->> 'avatar', ''),
          NULLIF(p_data ->> 'bio', ''),
          NULLIF(p_data ->> 'role', ''),
          NULLIF(p_data ->> 'specialization', ''),
          NULLIF(p_data ->> 'email', ''),
          NULLIF(p_data ->> 'phone', ''),
          NULLIF(p_data ->> 'website', ''),
          NULLIF(p_data ->> 'location', ''),
          NULLIF(p_data ->> 'tagline', ''),
          NULLIF(p_data ->> 'cover_image', ''),
          app_tags(p_data -> 'expertise'),
          COALESCE(p_data -> 'socials', '{}'::JSONB),
          COALESCE((p_data ->> 'is_visible')::BOOLEAN, TRUE),
          COALESCE((p_data ->> 'sort_order')::INTEGER, 0))
  ON CONFLICT (id) DO UPDATE SET
      name           = EXCLUDED.name,
      avatar         = EXCLUDED.avatar,
      bio            = EXCLUDED.bio,
      role           = EXCLUDED.role,
      specialization = EXCLUDED.specialization,
      email          = EXCLUDED.email,
      phone          = EXCLUDED.phone,
      website        = EXCLUDED.website,
      location       = EXCLUDED.location,
      tagline        = EXCLUDED.tagline,
      cover_image    = EXCLUDED.cover_image,
      expertise      = EXCLUDED.expertise,
      socials        = EXCLUDED.socials,
      is_visible     = CASE WHEN v_admin THEN EXCLUDED.is_visible ELSE authors.is_visible END,
      sort_order     = CASE WHEN v_admin THEN EXCLUDED.sort_order ELSE authors.sort_order END;

  -- give brand new authors a passwordless login
  IF v_new AND v_admin AND COALESCE((p_data ->> 'create_account')::BOOLEAN, TRUE) THEN
    v_user := lower(btrim(COALESCE(NULLIF(p_data ->> 'username', ''), v_id)));
    IF v_user = 'admin' THEN
      v_user := v_id;
    END IF;
    IF EXISTS (SELECT 1 FROM accounts WHERE username = v_user) THEN
      v_user := v_user || '-' || floor(random() * 900 + 100)::TEXT;
    END IF;
    INSERT INTO accounts (username, role, author_id, password_hash)
    VALUES (v_user, 'author', v_id, NULL)
    RETURNING id INTO v_acc_id;
  END IF;

  PERFORM app_log(a, CASE WHEN v_new THEN 'author_created' ELSE 'author_updated' END, 'author', v_id, '{}'::JSONB);

  SELECT to_jsonb(au) INTO v_row FROM authors au WHERE au.id = v_id;
  RETURN jsonb_build_object('ok', TRUE, 'id', v_id, 'author', v_row, 'username', v_user,
                            'account_id', v_acc_id,
                            'message', CASE WHEN v_new
                                            THEN 'Author created' || COALESCE(' — username "' || v_user || '", no password yet.', '.')
                                            ELSE 'Profile saved.' END);
END $fn$;

CREATE OR REPLACE FUNCTION api_author_action(p_token TEXT, p_id TEXT, p_action TEXT, p_value JSONB DEFAULT '{}')
RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE
  a      accounts%ROWTYPE;
  t      accounts%ROWTYPE;
  v_user TEXT;
  v_msg  TEXT;
  v_to   TEXT;
BEGIN
  a := app_require(p_token, 'admin');
  IF NOT EXISTS (SELECT 1 FROM authors WHERE id = p_id) THEN
    RETURN jsonb_build_object('ok', FALSE, 'error', 'NOT_FOUND', 'message', 'Author not found.');
  END IF;
  SELECT * INTO t FROM accounts WHERE author_id = p_id;

  CASE p_action
    WHEN 'set_active' THEN
      IF t.id IS NULL THEN RETURN jsonb_build_object('ok', FALSE, 'error', 'NO_ACCOUNT', 'message', 'This author has no login yet.'); END IF;
      UPDATE accounts SET is_active = COALESCE((p_value ->> 'active')::BOOLEAN, TRUE) WHERE id = t.id;
      IF NOT COALESCE((p_value ->> 'active')::BOOLEAN, TRUE) THEN
        UPDATE sessions SET revoked_at = NOW(), revoke_reason = 'account_disabled'
         WHERE account_id = t.id AND revoked_at IS NULL;
      END IF;
      v_msg := CASE WHEN COALESCE((p_value ->> 'active')::BOOLEAN, TRUE) THEN 'Login enabled.' ELSE 'Login disabled.' END;

    WHEN 'unlock' THEN
      UPDATE accounts SET failed_attempts = 0, locked_until = NULL WHERE id = t.id;
      v_msg := 'Account unlocked.';

    WHEN 'set_username' THEN
      v_user := lower(btrim(COALESCE(p_value ->> 'username', '')));
      IF v_user = '' OR v_user = 'admin' THEN
        RETURN jsonb_build_object('ok', FALSE, 'error', 'BAD_USERNAME', 'message', 'Pick a different username.');
      END IF;
      IF EXISTS (SELECT 1 FROM accounts WHERE username = v_user AND author_id IS DISTINCT FROM p_id) THEN
        RETURN jsonb_build_object('ok', FALSE, 'error', 'TAKEN', 'message', 'That username is already used.');
      END IF;
      IF t.id IS NULL THEN
        INSERT INTO accounts (username, role, author_id) VALUES (v_user, 'author', p_id);
        v_msg := 'Login created (no password yet).';
      ELSE
        UPDATE accounts SET username = v_user WHERE id = t.id;
        v_msg := 'Username updated.';
      END IF;

    WHEN 'create_account' THEN
      IF t.id IS NOT NULL THEN
        RETURN jsonb_build_object('ok', FALSE, 'error', 'EXISTS', 'message', 'This author already has a login.');
      END IF;
      v_user := lower(btrim(COALESCE(NULLIF(p_value ->> 'username', ''), p_id)));
      IF EXISTS (SELECT 1 FROM accounts WHERE username = v_user) THEN
        v_user := v_user || '-' || floor(random() * 900 + 100)::TEXT;
      END IF;
      INSERT INTO accounts (username, role, author_id) VALUES (v_user, 'author', p_id);
      v_msg := 'Login created: ' || v_user || ' (no password yet).';

    WHEN 'delete' THEN
      v_to := NULLIF(p_value ->> 'reassign_to', '');
      IF v_to IS NOT NULL THEN
        UPDATE posts SET author = v_to WHERE author = p_id;
      ELSIF COALESCE((p_value ->> 'delete_posts')::BOOLEAN, FALSE) THEN
        DELETE FROM posts WHERE author = p_id;
      END IF;
      DELETE FROM authors WHERE id = p_id;   -- cascades to the account
      v_msg := 'Author removed.';

    ELSE
      RETURN jsonb_build_object('ok', FALSE, 'error', 'UNKNOWN_ACTION', 'message', 'Unknown action.');
  END CASE;

  PERFORM app_log(a, 'author_' || p_action, 'author', p_id, p_value);
  RETURN jsonb_build_object('ok', TRUE, 'message', v_msg);
END $fn$;

-- =====================================================================
-- 10. WRITE API — SETTINGS, TAXONOMY, SIMPLE ENTRIES
-- =====================================================================

CREATE OR REPLACE FUNCTION api_save_settings(p_token TEXT, p_data JSONB) RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE a accounts%ROWTYPE;
BEGIN
  a := app_require(p_token, 'admin');

  INSERT INTO site_settings (id) VALUES (1) ON CONFLICT (id) DO NOTHING;
  UPDATE site_settings SET
      site    = COALESCE(p_data -> 'site',    site),
      themes  = COALESCE(p_data -> 'themes',  themes),
      seo     = COALESCE(p_data -> 'seo',     seo),
      social  = COALESCE(p_data -> 'social',  social),
      footer  = COALESCE(p_data -> 'footer',  footer),
      contact = COALESCE(p_data -> 'contact', contact)
   WHERE id = 1;

  IF p_data ? 'editorial' OR p_data ? 'security' THEN
    INSERT INTO app_config (id) VALUES (1) ON CONFLICT (id) DO NOTHING;
    UPDATE app_config SET
        editorial  = COALESCE(app_config.editorial, '{}'::JSONB) || COALESCE(p_data -> 'editorial', '{}'::JSONB),
        security   = COALESCE(app_config.security,  '{}'::JSONB) || COALESCE(p_data -> 'security',  '{}'::JSONB),
        updated_at = NOW()
     WHERE id = 1;
  END IF;

  PERFORM app_log(a, 'settings_saved', 'settings', '1', jsonb_build_object('keys', (SELECT jsonb_agg(k) FROM jsonb_object_keys(p_data) k)));
  RETURN jsonb_build_object('ok', TRUE, 'message', 'Settings saved.');
END $fn$;

CREATE OR REPLACE FUNCTION api_save_taxonomy(p_token TEXT, p_kind TEXT, p_data JSONB) RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE
  a     accounts%ROWTYPE;
  v_id  TEXT;
  v_new BOOLEAN;
  v_ord INTEGER;
BEGIN
  a := app_require(p_token, 'admin');
  v_id := app_slug(COALESCE(NULLIF(btrim(p_data ->> 'id'), ''), p_data ->> 'title'));
  IF COALESCE(v_id, '') = '' OR COALESCE(btrim(p_data ->> 'title'), '') = '' THEN
    RETURN jsonb_build_object('ok', FALSE, 'error', 'MISSING_FIELDS', 'message', 'An ID and a title are required.');
  END IF;

  IF p_kind = 'category' THEN
    v_new := NOT EXISTS (SELECT 1 FROM categories WHERE id = v_id);
    SELECT COALESCE(max(sort_order), 0) + 1 INTO v_ord FROM categories;
    INSERT INTO categories (id, title, icon, description, type, sort_order, hidden)
    VALUES (v_id, btrim(p_data ->> 'title'), COALESCE(NULLIF(p_data ->> 'icon', ''), 'edit'),
            NULLIF(p_data ->> 'description', ''), 'blog', v_ord,
            COALESCE((p_data ->> 'hidden')::BOOLEAN, FALSE))
    ON CONFLICT (id) DO UPDATE SET
        title = EXCLUDED.title, icon = EXCLUDED.icon, description = EXCLUDED.description;

  ELSIF p_kind = 'subtopic' THEN
    IF COALESCE(p_data ->> 'category_id', '') = '' THEN
      RETURN jsonb_build_object('ok', FALSE, 'error', 'MISSING_CATEGORY', 'message', 'Parent category missing.');
    END IF;
    v_new := NOT EXISTS (SELECT 1 FROM subtopics WHERE id = v_id);
    SELECT COALESCE(max(sort_order), 0) + 1 INTO v_ord FROM subtopics WHERE category_id = p_data ->> 'category_id';
    INSERT INTO subtopics (id, category_id, title, description, type, sort_order, hidden)
    VALUES (v_id, p_data ->> 'category_id', btrim(p_data ->> 'title'),
            NULLIF(p_data ->> 'description', ''), 'blog', v_ord,
            COALESCE((p_data ->> 'hidden')::BOOLEAN, FALSE))
    ON CONFLICT (id) DO UPDATE SET
        title = EXCLUDED.title, description = EXCLUDED.description;
  ELSE
    RETURN jsonb_build_object('ok', FALSE, 'error', 'UNKNOWN_KIND', 'message', 'Unknown taxonomy kind.');
  END IF;

  PERFORM app_log(a, p_kind || (CASE WHEN v_new THEN '_created' ELSE '_updated' END), p_kind, v_id, '{}'::JSONB);
  RETURN jsonb_build_object('ok', TRUE, 'id', v_id, 'message', CASE WHEN v_new THEN 'Created.' ELSE 'Saved.' END);
END $fn$;

CREATE OR REPLACE FUNCTION api_taxonomy_action(p_token TEXT, p_kind TEXT, p_id TEXT,
                                               p_action TEXT, p_value JSONB DEFAULT '{}')
RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE
  a      accounts%ROWTYPE;
  v_msg  TEXT;
  v_dir  INTEGER;
  v_cur  INTEGER;
  v_oid  TEXT;
  v_oord INTEGER;
  v_cat  TEXT;
  v_lock BOOLEAN;
BEGIN
  a := app_require(p_token, 'admin');
  v_dir := COALESCE((p_value ->> 'dir')::INTEGER, -1);

  IF p_kind = 'category' THEN
    SELECT system_locked, sort_order INTO v_lock, v_cur FROM categories WHERE id = p_id;
    IF v_lock IS NULL THEN RETURN jsonb_build_object('ok', FALSE, 'error', 'NOT_FOUND'); END IF;

    IF p_action = 'hide' THEN
      UPDATE categories SET hidden = COALESCE((p_value ->> 'hidden')::BOOLEAN, TRUE) WHERE id = p_id;
      v_msg := 'Visibility updated.';
    ELSIF p_action = 'delete' THEN
      IF v_lock THEN RETURN jsonb_build_object('ok', FALSE, 'error', 'LOCKED', 'message', 'This category is part of the site structure.'); END IF;
      DELETE FROM categories WHERE id = p_id;
      v_msg := 'Category deleted.';
    ELSIF p_action = 'move' THEN
      SELECT id, sort_order INTO v_oid, v_oord FROM categories
       WHERE CASE WHEN v_dir < 0 THEN sort_order < v_cur ELSE sort_order > v_cur END
       ORDER BY CASE WHEN v_dir < 0 THEN -sort_order ELSE sort_order END LIMIT 1;
      IF v_oid IS NOT NULL THEN
        UPDATE categories SET sort_order = v_cur  WHERE id = v_oid;
        UPDATE categories SET sort_order = v_oord WHERE id = p_id;
      END IF;
      v_msg := 'Reordered.';
    ELSE
      RETURN jsonb_build_object('ok', FALSE, 'error', 'UNKNOWN_ACTION');
    END IF;

  ELSIF p_kind = 'subtopic' THEN
    SELECT system_locked, sort_order, category_id INTO v_lock, v_cur, v_cat FROM subtopics WHERE id = p_id;
    IF v_lock IS NULL THEN RETURN jsonb_build_object('ok', FALSE, 'error', 'NOT_FOUND'); END IF;

    IF p_action = 'hide' THEN
      UPDATE subtopics SET hidden = COALESCE((p_value ->> 'hidden')::BOOLEAN, TRUE) WHERE id = p_id;
      v_msg := 'Visibility updated.';
    ELSIF p_action = 'delete' THEN
      IF v_lock THEN RETURN jsonb_build_object('ok', FALSE, 'error', 'LOCKED', 'message', 'This subtopic is part of the site structure.'); END IF;
      DELETE FROM subtopics WHERE id = p_id;
      v_msg := 'Subtopic deleted.';
    ELSIF p_action = 'move' THEN
      SELECT id, sort_order INTO v_oid, v_oord FROM subtopics
       WHERE category_id = v_cat
         AND CASE WHEN v_dir < 0 THEN sort_order < v_cur ELSE sort_order > v_cur END
       ORDER BY CASE WHEN v_dir < 0 THEN -sort_order ELSE sort_order END LIMIT 1;
      IF v_oid IS NOT NULL THEN
        UPDATE subtopics SET sort_order = v_cur  WHERE id = v_oid;
        UPDATE subtopics SET sort_order = v_oord WHERE id = p_id;
      END IF;
      v_msg := 'Reordered.';
    ELSE
      RETURN jsonb_build_object('ok', FALSE, 'error', 'UNKNOWN_ACTION');
    END IF;
  ELSE
    RETURN jsonb_build_object('ok', FALSE, 'error', 'UNKNOWN_KIND');
  END IF;

  PERFORM app_log(a, p_kind || '_' || p_action, p_kind, p_id, p_value);
  RETURN jsonb_build_object('ok', TRUE, 'message', v_msg);
END $fn$;

-- downloads / glossary / faqs / about / media -----------------------------
CREATE OR REPLACE FUNCTION api_save_entry(p_token TEXT, p_entity TEXT, p_data JSONB) RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE
  a     accounts%ROWTYPE;
  v_id  TEXT;
  v_int INTEGER;
  v_ord INTEGER;
BEGIN
  a := app_require(p_token);

  IF p_entity = 'media' THEN
    IF a.role <> 'admin' AND NOT COALESCE((app_cfg('editorial') ->> 'authors_can_upload')::BOOLEAN, TRUE) THEN
      RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501';
    END IF;
    INSERT INTO media (url, bucket, path, filename, mime, size_bytes, alt, uploaded_by, uploader)
    VALUES (p_data ->> 'url', p_data ->> 'bucket', p_data ->> 'path', p_data ->> 'filename',
            p_data ->> 'mime', NULLIF(p_data ->> 'size_bytes', '')::BIGINT, NULLIF(p_data ->> 'alt', ''),
            a.id, a.username);
    RETURN jsonb_build_object('ok', TRUE, 'message', 'Uploaded.');
  END IF;

  IF a.role <> 'admin' THEN RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501'; END IF;

  IF p_entity = 'download' THEN
    v_id := app_slug(COALESCE(NULLIF(btrim(p_data ->> 'id'), ''), p_data ->> 'name'));
    IF COALESCE(v_id, '') = '' OR COALESCE(btrim(p_data ->> 'name'), '') = '' THEN
      RETURN jsonb_build_object('ok', FALSE, 'error', 'MISSING_FIELDS', 'message', 'ID and name are required.');
    END IF;
    SELECT COALESCE(max(sort_order), 0) + 1 INTO v_ord FROM downloads;
    INSERT INTO downloads (id, name, description, file_url, file_format, file_size, thumbnail, tags, sort_order, is_published)
    VALUES (v_id, btrim(p_data ->> 'name'), NULLIF(p_data ->> 'description', ''), NULLIF(p_data ->> 'file_url', ''),
            NULLIF(p_data ->> 'file_format', ''), NULLIF(p_data ->> 'file_size', ''), NULLIF(p_data ->> 'thumbnail', ''),
            app_tags(p_data -> 'tags'), v_ord, COALESCE((p_data ->> 'is_published')::BOOLEAN, TRUE))
    ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name, description = EXCLUDED.description, file_url = EXCLUDED.file_url,
        file_format = EXCLUDED.file_format, file_size = EXCLUDED.file_size,
        thumbnail = EXCLUDED.thumbnail, tags = EXCLUDED.tags, is_published = EXCLUDED.is_published;

  ELSIF p_entity = 'glossary' THEN
    IF COALESCE(btrim(p_data ->> 'word'), '') = '' OR COALESCE(btrim(p_data ->> 'definition'), '') = '' THEN
      RETURN jsonb_build_object('ok', FALSE, 'error', 'MISSING_FIELDS', 'message', 'Word and definition are required.');
    END IF;
    v_int := NULLIF(p_data ->> 'id', '')::INTEGER;
    IF v_int IS NULL THEN
      INSERT INTO glossary (word, definition) VALUES (btrim(p_data ->> 'word'), btrim(p_data ->> 'definition'))
      RETURNING id INTO v_int;
    ELSE
      UPDATE glossary SET word = btrim(p_data ->> 'word'), definition = btrim(p_data ->> 'definition') WHERE id = v_int;
    END IF;
    v_id := v_int::TEXT;

  ELSIF p_entity = 'faq' THEN
    IF COALESCE(btrim(p_data ->> 'question'), '') = '' OR COALESCE(btrim(p_data ->> 'answer'), '') = '' THEN
      RETURN jsonb_build_object('ok', FALSE, 'error', 'MISSING_FIELDS', 'message', 'Question and answer are required.');
    END IF;
    v_int := NULLIF(p_data ->> 'id', '')::INTEGER;
    IF v_int IS NULL THEN
      SELECT COALESCE(max(sort_order), 0) + 1 INTO v_ord FROM faqs;
      INSERT INTO faqs (question, answer, sort_order)
      VALUES (btrim(p_data ->> 'question'), btrim(p_data ->> 'answer'), v_ord) RETURNING id INTO v_int;
    ELSE
      UPDATE faqs SET question = btrim(p_data ->> 'question'), answer = btrim(p_data ->> 'answer') WHERE id = v_int;
    END IF;
    v_id := v_int::TEXT;

  ELSIF p_entity = 'about' THEN
    INSERT INTO about (id, title, subtitle, body)
    VALUES (1, p_data ->> 'title', p_data ->> 'subtitle', COALESCE(p_data ->> 'body', ''))
    ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title, subtitle = EXCLUDED.subtitle, body = EXCLUDED.body;
    v_id := '1';

  ELSE
    RETURN jsonb_build_object('ok', FALSE, 'error', 'UNKNOWN_ENTITY', 'message', 'Unknown entity.');
  END IF;

  PERFORM app_log(a, p_entity || '_saved', p_entity, v_id, '{}'::JSONB);
  RETURN jsonb_build_object('ok', TRUE, 'id', v_id, 'message', 'Saved.');
END $fn$;

CREATE OR REPLACE FUNCTION api_delete_entry(p_token TEXT, p_entity TEXT, p_id TEXT) RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE a accounts%ROWTYPE; v_locked BOOLEAN;
BEGIN
  a := app_require(p_token);

  IF p_entity = 'media' THEN
    DELETE FROM media WHERE id = p_id::UUID AND (a.role = 'admin' OR uploaded_by = a.id);
    RETURN jsonb_build_object('ok', TRUE, 'message', 'Removed from the library.');
  END IF;

  IF a.role <> 'admin' THEN RAISE EXCEPTION 'FORBIDDEN' USING ERRCODE = '42501'; END IF;

  IF p_entity = 'download' THEN
    SELECT system_locked INTO v_locked FROM downloads WHERE id = p_id;
    IF v_locked THEN RETURN jsonb_build_object('ok', FALSE, 'error', 'LOCKED', 'message', 'This item is locked.'); END IF;
    DELETE FROM downloads WHERE id = p_id;
  ELSIF p_entity = 'glossary' THEN
    DELETE FROM glossary WHERE id = p_id::INTEGER AND NOT COALESCE(system_locked, FALSE);
  ELSIF p_entity = 'faq' THEN
    DELETE FROM faqs WHERE id = p_id::INTEGER AND NOT COALESCE(system_locked, FALSE);
  ELSIF p_entity = 'message' THEN
    DELETE FROM contact_messages WHERE id = p_id::INTEGER;
  ELSIF p_entity = 'subscriber' THEN
    DELETE FROM newsletter_subscribers WHERE id = p_id::INTEGER;
  ELSE
    RETURN jsonb_build_object('ok', FALSE, 'error', 'UNKNOWN_ENTITY');
  END IF;

  PERFORM app_log(a, p_entity || '_deleted', p_entity, p_id, '{}'::JSONB);
  RETURN jsonb_build_object('ok', TRUE, 'message', 'Deleted.');
END $fn$;

CREATE OR REPLACE FUNCTION api_entry_action(p_token TEXT, p_entity TEXT, p_id TEXT,
                                            p_action TEXT, p_value JSONB DEFAULT '{}')
RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE a accounts%ROWTYPE; v_msg TEXT := 'Updated.';
BEGIN
  a := app_require(p_token, 'admin');

  IF p_entity = 'download' AND p_action = 'publish' THEN
    UPDATE downloads SET is_published = COALESCE((p_value ->> 'value')::BOOLEAN, TRUE) WHERE id = p_id;
  ELSIF p_entity = 'message' AND p_action = 'read' THEN
    UPDATE contact_messages SET is_read = COALESCE((p_value ->> 'value')::BOOLEAN, TRUE) WHERE id = p_id::INTEGER;
  ELSIF p_entity = 'message' AND p_action = 'read_all' THEN
    UPDATE contact_messages SET is_read = TRUE WHERE NOT is_read;
    v_msg := 'All messages marked as read.';
  ELSIF p_entity = 'subscriber' AND p_action = 'active' THEN
    UPDATE newsletter_subscribers SET is_active = COALESCE((p_value ->> 'value')::BOOLEAN, TRUE) WHERE id = p_id::INTEGER;
  ELSE
    RETURN jsonb_build_object('ok', FALSE, 'error', 'UNKNOWN_ACTION');
  END IF;

  PERFORM app_log(a, p_entity || '_' || p_action, p_entity, p_id, p_value);
  RETURN jsonb_build_object('ok', TRUE, 'message', v_msg);
END $fn$;

-- =====================================================================
-- 11. PUBLIC (UNAUTHENTICATED) API
-- =====================================================================

CREATE OR REPLACE FUNCTION api_track_view(p_post_id TEXT) RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
BEGIN
  UPDATE posts SET views = COALESCE(views, 0) + 1 WHERE id = p_post_id AND status = 'published';
  IF FOUND THEN
    INSERT INTO post_daily_views (post_id, day, views) VALUES (p_post_id, CURRENT_DATE, 1)
    ON CONFLICT (post_id, day) DO UPDATE SET views = post_daily_views.views + 1;
  END IF;
  RETURN jsonb_build_object('ok', TRUE);
END $fn$;

CREATE OR REPLACE FUNCTION api_contact(p_name TEXT, p_email TEXT, p_message TEXT, p_subject TEXT DEFAULT NULL)
RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
DECLARE v_ip TEXT; v_recent INTEGER;
BEGIN
  IF COALESCE(btrim(p_name), '') = '' OR COALESCE(btrim(p_email), '') = '' OR COALESCE(btrim(p_message), '') = '' THEN
    RETURN jsonb_build_object('ok', FALSE, 'message', 'Please fill in every field.');
  END IF;
  IF p_email !~ '^[^@\s]+@[^@\s]+\.[^@\s]+$' THEN
    RETURN jsonb_build_object('ok', FALSE, 'message', 'That email address looks wrong.');
  END IF;

  v_ip := app_client_ip();
  SELECT count(*) INTO v_recent FROM contact_messages
   WHERE created_at > NOW() - INTERVAL '10 minutes' AND email = lower(btrim(p_email));
  IF v_recent >= 5 THEN
    RETURN jsonb_build_object('ok', FALSE, 'message', 'You have sent several messages already. Please wait a little.');
  END IF;

  INSERT INTO contact_messages (name, email, message, subject)
  VALUES (left(btrim(p_name), 120), lower(btrim(p_email)), left(btrim(p_message), 5000), NULLIF(btrim(COALESCE(p_subject, '')), ''));
  RETURN jsonb_build_object('ok', TRUE, 'message', 'Message sent. Thank you!');
END $fn$;

CREATE OR REPLACE FUNCTION api_subscribe(p_name TEXT, p_email TEXT) RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, extensions, pg_temp AS $fn$
BEGIN
  IF COALESCE(btrim(p_email), '') = '' OR p_email !~ '^[^@\s]+@[^@\s]+\.[^@\s]+$' THEN
    RETURN jsonb_build_object('ok', FALSE, 'message', 'Please enter a valid email address.');
  END IF;
  INSERT INTO newsletter_subscribers (name, email)
  VALUES (COALESCE(NULLIF(left(btrim(p_name), 120), ''), 'Subscriber'), lower(btrim(p_email)))
  ON CONFLICT (email) DO UPDATE SET is_active = TRUE, name = EXCLUDED.name;
  RETURN jsonb_build_object('ok', TRUE, 'message', 'You are subscribed. Welcome aboard!');
END $fn$;

-- =====================================================================
-- 12. ROW LEVEL SECURITY
--     The public anon key may only READ published content.
--     Every write happens through the api_* functions above.
-- =====================================================================

ALTER TABLE site_settings          ENABLE ROW LEVEL SECURITY;
ALTER TABLE app_config             ENABLE ROW LEVEL SECURITY;
ALTER TABLE authors                ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories             ENABLE ROW LEVEL SECURITY;
ALTER TABLE subtopics              ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts                  ENABLE ROW LEVEL SECURITY;
ALTER TABLE downloads              ENABLE ROW LEVEL SECURITY;
ALTER TABLE glossary               ENABLE ROW LEVEL SECURITY;
ALTER TABLE faqs                   ENABLE ROW LEVEL SECURITY;
ALTER TABLE about                  ENABLE ROW LEVEL SECURITY;
ALTER TABLE contact_messages       ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts               ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions               ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log              ENABLE ROW LEVEL SECURITY;
ALTER TABLE post_revisions         ENABLE ROW LEVEL SECURITY;
ALTER TABLE media                  ENABLE ROW LEVEL SECURITY;
ALTER TABLE post_daily_views       ENABLE ROW LEVEL SECURITY;

-- remove the wide-open policies shipped with v1 ------------------------
DO $$
DECLARE r RECORD;
BEGIN
  FOR r IN
    SELECT schemaname, tablename, policyname
      FROM pg_policies
     WHERE schemaname = 'public'
       AND policyname IN ('Public read', 'Public write', 'public read', 'public write')
  LOOP
    EXECUTE format('DROP POLICY IF EXISTS %I ON %I.%I', r.policyname, r.schemaname, r.tablename);
  END LOOP;
END $$;

DROP POLICY IF EXISTS "read_settings"   ON site_settings;
DROP POLICY IF EXISTS "read_authors"    ON authors;
DROP POLICY IF EXISTS "read_categories" ON categories;
DROP POLICY IF EXISTS "read_subtopics"  ON subtopics;
DROP POLICY IF EXISTS "read_posts"      ON posts;
DROP POLICY IF EXISTS "read_downloads"  ON downloads;
DROP POLICY IF EXISTS "read_glossary"   ON glossary;
DROP POLICY IF EXISTS "read_faqs"       ON faqs;
DROP POLICY IF EXISTS "read_about"      ON about;

CREATE POLICY "read_settings"   ON site_settings FOR SELECT USING (TRUE);
CREATE POLICY "read_authors"    ON authors       FOR SELECT USING (TRUE);
CREATE POLICY "read_categories" ON categories    FOR SELECT USING (COALESCE(hidden, FALSE) = FALSE);
CREATE POLICY "read_subtopics"  ON subtopics     FOR SELECT USING (COALESCE(hidden, FALSE) = FALSE);
CREATE POLICY "read_posts"      ON posts         FOR SELECT
  USING (status = 'published'
         OR (status = 'scheduled' AND scheduled_for IS NOT NULL AND scheduled_for <= NOW()));
CREATE POLICY "read_downloads"  ON downloads     FOR SELECT USING (COALESCE(is_published, TRUE));
CREATE POLICY "read_glossary"   ON glossary      FOR SELECT USING (TRUE);
CREATE POLICY "read_faqs"       ON faqs          FOR SELECT USING (TRUE);
CREATE POLICY "read_about"      ON about         FOR SELECT USING (TRUE);

-- app_config, accounts, sessions, audit_log, post_revisions, media,
-- post_daily_views, contact_messages and newsletter_subscribers get NO
-- policies at all -> unreachable with the anon key, reachable only
-- through the SECURITY DEFINER api_* functions.

-- =====================================================================
-- 13. GRANTS
-- =====================================================================

GRANT USAGE ON SCHEMA public TO anon, authenticated;

-- read-only for the public key
GRANT SELECT ON site_settings, authors, categories, subtopics, posts,
                downloads, glossary, faqs, about TO anon, authenticated;

-- no direct writes anywhere
DO $$
DECLARE t RECORD;
BEGIN
  FOR t IN SELECT tablename FROM pg_tables WHERE schemaname = 'public'
  LOOP
    BEGIN
      EXECUTE format('REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON public.%I FROM anon, authenticated', t.tablename);
    EXCEPTION WHEN OTHERS THEN NULL;   -- table owned by someone else: skip
    END;
  END LOOP;
END $$;

REVOKE SELECT ON contact_messages, newsletter_subscribers FROM anon, authenticated;

-- functions: api_* are public entry points, app_* are internal only
DO $$
DECLARE f RECORD;
BEGIN
  FOR f IN
    SELECT p.oid::regprocedure AS sig, p.proname
      FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
     WHERE n.nspname = 'public' AND (p.proname LIKE 'api\_%' OR p.proname LIKE 'app\_%')
  LOOP
    EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC', f.sig);
    BEGIN
      EXECUTE format('REVOKE ALL ON FUNCTION %s FROM anon, authenticated', f.sig);
    EXCEPTION WHEN OTHERS THEN NULL;
    END;
    IF f.proname LIKE 'api\_%' THEN
      EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO anon, authenticated', f.sig);
    END IF;
  END LOOP;
END $$;

-- =====================================================================
-- 14. STORAGE BUCKETS
-- =====================================================================
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types) VALUES
('site-assets',    'site-assets',    TRUE, 10485760,  ARRAY['image/jpeg','image/png','image/webp','image/gif','image/svg+xml']),
('post-images',    'post-images',    TRUE, 10485760,  ARRAY['image/jpeg','image/png','image/webp','image/gif','image/svg+xml']),
('author-avatars', 'author-avatars', TRUE, 5242880,   ARRAY['image/jpeg','image/png','image/webp','image/gif']),
('download-files', 'download-files', TRUE, 104857600, ARRAY['application/pdf','application/msword','application/vnd.openxmlformats-officedocument.wordprocessingml.document','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','application/vnd.openxmlformats-officedocument.presentationml.presentation','image/jpeg','image/png','image/webp','image/gif','image/svg+xml','audio/mpeg','audio/wav','video/mp4','video/webm','application/zip','text/csv','text/plain'])
ON CONFLICT (id) DO UPDATE SET public = EXCLUDED.public,
                               file_size_limit = EXCLUDED.file_size_limit,
                               allowed_mime_types = EXCLUDED.allowed_mime_types;

DO $$
DECLARE r RECORD;
BEGIN
  FOR r IN SELECT policyname FROM pg_policies WHERE schemaname = 'storage' AND tablename = 'objects'
             AND policyname IN ('Public read storage','Public upload storage','Public delete storage',
                                'Public update storage','blog_read_storage','blog_write_storage',
                                'blog_update_storage','blog_delete_storage')
  LOOP
    EXECUTE format('DROP POLICY IF EXISTS %I ON storage.objects', r.policyname);
  END LOOP;
END $$;

CREATE POLICY "blog_read_storage"   ON storage.objects FOR SELECT
  USING (bucket_id IN ('site-assets','post-images','author-avatars','download-files'));
CREATE POLICY "blog_write_storage"  ON storage.objects FOR INSERT
  WITH CHECK (bucket_id IN ('site-assets','post-images','author-avatars','download-files'));
CREATE POLICY "blog_update_storage" ON storage.objects FOR UPDATE
  USING (bucket_id IN ('site-assets','post-images','author-avatars','download-files'));
CREATE POLICY "blog_delete_storage" ON storage.objects FOR DELETE
  USING (bucket_id IN ('site-assets','post-images','author-avatars','download-files'));

-- =====================================================================
-- 15. SEED DATA
-- =====================================================================

INSERT INTO site_settings (id, site, themes, seo, social, footer, contact) VALUES (1,
'{"name":"My Blog","tagline":"Your blog tagline here","description":"A blog platform for your content.","logo":"","favicon":"","hero_image":"","hero_title":"Welcome","hero_subtitle":"Start writing and sharing your ideas."}',
'{"light":{"primary":"#3b82f6","secondary":"#60a5fa","accent":"#f59e0b","background":"#ffffff","surface":"#f8fafc","text":"#1e293b","text_secondary":"#64748b","border":"#e2e8f0"},"dark":{"primary":"#60a5fa","secondary":"#93c5fd","accent":"#fbbf24","background":"#0f172a","surface":"#1e293b","text":"#f1f5f9","text_secondary":"#94a3b8","border":"#334155"}}',
'{"title":"My Blog","description":"A blog platform","keywords":"blog, writing, content"}',
'{"twitter":"","facebook":"","linkedin":"","instagram":"","youtube":""}',
'{"copyright":"© 2026 My Blog. All rights reserved.","links":[]}',
'{"email":"admin@example.com","web3forms_key":""}'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO app_config (id, editorial, security) VALUES (1,
'{"require_approval":false,"authors_can_publish":true,"authors_can_delete":true,"authors_can_upload":true,"authors_can_schedule":true,"default_status":"draft"}',
'{"session_hours":12,"remember_days":30,"max_attempts":8,"lockout_minutes":15,"min_password_length":6,"allow_passwordless":true}'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO categories (id, title, icon, description, type, sort_order, hidden, system_locked) VALUES
('default',   'Blog',      'edit',     'Default blog category',  'blog',      1, FALSE, FALSE),
('downloads', 'Downloads', 'download', 'Downloadable resources', 'downloads', 2, FALSE, TRUE),
('glossary',  'Glossary',  'book',     'Terms and definitions',  'glossary',  3, FALSE, TRUE),
('faqs',      'FAQs',      'help',     'Frequently asked questions', 'faqs',  4, FALSE, TRUE),
('about',     'About',     'info',     'About us',               'about',     5, FALSE, TRUE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO subtopics (id, category_id, title, description, type, sort_order, hidden, system_locked) VALUES
('default-contents', 'default', 'Default Contents', 'General blog posts', 'blog', 1, FALSE, FALSE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO about (id, title, subtitle, body) VALUES (1, 'About', 'Learn more about us', '')
ON CONFLICT (id) DO NOTHING;

-- THE ADMIN ACCOUNT: username "admin", no password until one is set ------
INSERT INTO accounts (username, role, author_id, password_hash)
VALUES ('admin', 'admin', NULL, NULL)
ON CONFLICT (username) DO NOTHING;

-- Every existing author gets a passwordless login (username = author id) --
INSERT INTO accounts (username, role, author_id)
SELECT lower(au.id), 'author', au.id
  FROM authors au
 WHERE lower(au.id) <> 'admin'
   AND NOT EXISTS (SELECT 1 FROM accounts ac WHERE ac.author_id = au.id)
   AND NOT EXISTS (SELECT 1 FROM accounts ac2 WHERE ac2.username = lower(au.id));

-- =====================================================================
-- 16. MIGRATION / CONSISTENCY FIX-UPS  (safe to re-run)
-- =====================================================================

-- posts created before the workflow existed
UPDATE posts SET status = 'draft'
 WHERE COALESCE(is_published, TRUE) = FALSE AND COALESCE(status, 'published') = 'published';
UPDATE posts SET status = 'published' WHERE status IS NULL;
UPDATE posts SET published_at = COALESCE(published_at, created_at, NOW()) WHERE status = 'published';
UPDATE posts SET seo = COALESCE(seo, '{}'::JSONB), views = COALESCE(views, 0);

-- recompute word counts / reading time / is_published through the trigger
UPDATE posts SET updated_at = COALESCE(updated_at, NOW());

UPDATE authors SET is_visible = COALESCE(is_visible, TRUE),
                   socials    = COALESCE(socials, '{}'::JSONB),
                   expertise  = COALESCE(expertise, '{}'::TEXT[]);

-- housekeeping: drop sessions that expired long ago
DELETE FROM sessions WHERE expires_at < NOW() - INTERVAL '30 days';

-- =====================================================================
-- 17. DONE — quick check
-- =====================================================================
-- SELECT username, role, (password_hash IS NULL) AS passwordless FROM accounts ORDER BY role;
