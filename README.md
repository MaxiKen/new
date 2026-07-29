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

## Admin Panel

Access at `yourdomain.com/admin.html`

### Features:
- **Dashboard** — Stats overview
- **Settings** — Site name, colors, hero, social links, SEO
- **Posts** — Create/edit with Quill editor, featured toggle, publish/hide
- **Authors** — Manage author profiles
- **Categories** — Create, edit, hide, reorder; add/remove subtopics
- **Downloads** — Upload files, manage resources
- **Glossary** — Word + definition entries
- **FAQs** — Questions and answers
- **About** — Edit about page with rich text
- **Messages** — View contact form submissions
- **Subscribers** — Manage newsletter subscribers

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