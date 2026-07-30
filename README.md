# Blog Template

A professional, responsive blog platform built with vanilla HTML, CSS, and JavaScript. Uses Supabase as backend with offline support via PWA.

## Features

- **Responsive Design** — Works on all devices
- **PWA Support** — Installable, works offline
- **2 Themes** — Light and Dark, fully customizable via admin
- **Rich Text Editor** — Quill.js WYSIWYG for blog posts
- **Dynamic Content** — All content from Supabase database
- **File Uploads** — Images, documents via Supabase Storage
- **Admin Panel** — Full CRUD for all content (hidden, direct URL only)
- **Search** — Full-text search across all posts
- **Contact Form** — Messages saved to database
- **Newsletter** — Subscribers managed in admin
- **Categories & Subtopics** — Organize content hierarchically
- **Featured Posts** — Highlight important content
- **Pull to Refresh** — Mobile gesture support
- **Offline Mode** — Cached content available offline

## Quick Start

1. Copy `env.example.js` to `env.js`
2. Add your Supabase URL and anon key
3. Run `supabase-schema.sql` in Supabase SQL Editor
4. Create storage buckets (see SUPABASE-SETUP.md)
5. Open `index.html` in browser
6. Access admin at `admin.html`

## File Structure

```
├── index.html          # Main site
├── admin.html          # Admin panel (hidden)
├── env.js              # Supabase credentials
├── manifest.json       # PWA manifest
├── sw.js               # Service worker
├── supabase-schema.sql # Database setup
├── css/
│   └── styles.css      # All styles
├── js/
│   ├── app.js          # Main application
│   ├── content.js      # Content manager
│   ├── router.js       # SPA router
│   ├── storage.js      # Local storage
│   └── supabase.js     # Database client
├── icons/              # App icons
└── images/             # Static images
```

## Admin Studio

Access at `yourdomain.com/admin.html` (the `#/admin` route on the public site redirects there too). Every visit starts at a **sign-in screen**.

### Accounts & sign-in
- Two account types: **admin** and **author**.
- The admin account is fixed to the username `admin` and starts **without a password** — sign in with `admin` and an empty password the first time; the studio immediately prompts you to set one.
- Authors are created by the admin and start **without a password**. The admin can set/clear a password for anyone; every user can also set, change, or remove their own. A blank password means passwordless sign-in.
- Sessions are token-based (SHA-256 hashed server-side) with "remember me", per-device session management, lockout after repeated failures, and a full audit log.

### What authors can do
- Write and manage **their own posts** (any category/subtopic), always published under their own byline.
- Edit **their own profile** (bio, photo, cover, expertise, social links, password).

### What the admin can do (everything, plus)
- Post **as any author** (choose the byline in the editor).
- Edit any author's profile on their behalf, create/deactivate/unlock accounts, manage usernames and passwords, revoke sessions.
- Review workflow (approve/send back), scheduling, featured posts, revisions, editorial & sign-in policies.

### Studio pages
- **Dashboard** — Role-aware stats, review queue, top posts, activity
- **Posts** — Filters, bulk actions, Quill writing desk with autosave, SEO, scheduling, revisions, duplicate
- **Authors** — Profiles + accounts, password/lock/session controls (admin)
- **Media** — Image library
- **Settings** — Site name, colors, hero, social links, SEO
- **Categories** — Create, edit, hide, reorder; add/remove subtopics
- **Downloads / Glossary / FAQs / About** — Library content
- **Messages / Subscribers** — Contact inbox and newsletter list
- **Security** — Own password & devices; admin: all accounts, policies, audit log

## Customization

### Change Site Name
Admin → Settings → Site Information → Site Name

### Change Colors
Admin → Settings → Theme Colors → Pick colors for light/dark themes

### Add Hero Image
Admin → Settings → Upload Hero Background Image

### Add Social Links
Admin → Settings → Contact & Social → Enter URLs

## Requirements

- Modern browser
- Supabase account (free tier works)
- Web server for hosting (HTTPS required for PWA)

## License

Free to use and modify.