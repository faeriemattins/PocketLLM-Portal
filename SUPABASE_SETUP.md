# Supabase Setup Instructions

## Step 1: Create Account
1. Go to https://supabase.com
2. Click "Start your project"
3. Sign up with GitHub, Google, or email

## Step 2: Create Project
1. Click "New Project"
2. **Project name**: `PocketLLM-Portal`
3. **Database Password**: Choose a strong password (save it!)
4. **Region**: Choose closest to you
5. Click "Create new project" (takes ~2 minutes)

## Step 3: Get Connection String
1. Once created, click on your project
2. Go to **Settings** (gear icon) → **Database**
3. Scroll to **Connection string**
4. Select **URI** tab
5. Copy the connection string (looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres`)
6. Replace `[YOUR-PASSWORD]` with your actual password

## Step 4: Provide to Me
Paste the connection string here, and I'll configure your app to use it!

---

**Alternative: Neon (even simpler)**
1. Go to https://neon.tech
2. Sign up → Create project
3. Copy the connection string immediately shown
