# Quick Start Guide

## 5-Minute Setup

### Step 1: Get Supabase Credentials
1. Go to [supabase.com](https://supabase.com) and create an account
2. Create a new project
3. Go to Settings → API
4. Copy your **Project URL** and **anon public key**

### Step 2: Configure Environment
Edit `env.js`:
```javascript
const ENV = {
  SUPABASE_URL: 'https://your-project.supabase.co',
  SUPABASE_ANON_KEY: 'your-anon-key-here'
};
```

### Step 3: Setup Database
1. In Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy the entire contents of `supabase-schema.sql`
4. Click **Run**

### Step 4: Create Storage Buckets
In Supabase → Storage, create these buckets (all public):
- `site-assets`
- `post-images`
- `author-avatars`
- `download-files`

### Step 5: Start Using
1. Open `admin.html` to configure your site
2. Go to Settings → Set your site name, colors, etc.
3. Create authors, categories, and posts
4. Open `index.html` to see your blog

## Adding Content

### Create a Post
1. Admin → Posts → + New Post
2. Fill in required fields (ID, Title, Category, Subtopic, Author, Content)
3. Use the rich text editor for content
4. Click Save

### Add Categories
1. Admin → Categories → + New Category
2. Set ID, title, icon
3. Add subtopics to organize content

### Upload Files
1. Admin → Downloads → + New Download
2. Upload file or enter URL
3. Set name, description, format

## Going Live

1. Upload all files to your web hosting
2. Ensure HTTPS is enabled (required for PWA)
3. Update `env.js` with production Supabase credentials
4. Test all features

## Need Help?

Check `README.md` for detailed documentation.