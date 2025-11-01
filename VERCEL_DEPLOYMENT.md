# Deploying to Vercel

This guide will help you deploy your Home Management System application to Vercel.

## Prerequisites

1. A [Vercel account](https://vercel.com/signup)
2. [Vercel CLI](https://vercel.com/cli) installed (optional but recommended)
3. A PostgreSQL database (e.g., from [Supabase](https://supabase.com/), [Neon](https://neon.tech/), or [Railway](https://railway.app/))
4. Your code pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Step 1: Set Up PostgreSQL Database

Before deploying, you need a PostgreSQL database. Here are some free options:

### Option A: Supabase (Recommended)
1. Go to [supabase.com](https://supabase.com/)
2. Create a new project
3. Get your connection string from Settings → Database
4. The connection string format: `postgresql://postgres:[YOUR-PASSWORD]@[HOST]:[PORT]/postgres`

### Option B: Neon
1. Go to [neon.tech](https://neon.tech/)
2. Create a new project
3. Copy the connection string

### Option C: Railway
1. Go to [railway.app](https://railway.app/)
2. Create a new PostgreSQL database
3. Copy the connection string from the Connect tab

## Step 2: Prepare Your Repository

Make sure your code is pushed to GitHub, GitLab, or Bitbucket. The following files have been created for you:

- `vercel.json` - Vercel configuration
- `api/index.py` - Vercel serverless function entry point
- `.vercelignore` - Files to exclude from deployment

## Step 3: Deploy to Vercel

### Method 1: Using Vercel Dashboard (Easiest)

1. Go to [vercel.com](https://vercel.com/) and log in
2. Click "Add New" → "Project"
3. Import your Git repository
4. Configure your project:
   - **Framework Preset**: Other
   - **Root Directory**: ./
   - **Build Command**: Leave empty (Vercel will auto-detect)
   - **Output Directory**: Leave empty

5. **Add Environment Variables** (CRITICAL):
   Click on "Environment Variables" and add:
   
   ```
   POSTGRES_URL = postgresql://user:password@host:port/database
   SECRET_KEY = your-secret-key-here
   ```
   
   - For `POSTGRES_URL`: Use your PostgreSQL connection string from Step 1
   - For `SECRET_KEY`: Generate a secure random string (e.g., use `openssl rand -hex 32`)

6. Click "Deploy"

### Method 2: Using Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from your project directory**:
   ```bash
   vercel
   ```

4. **Add environment variables**:
   ```bash
   vercel env add POSTGRES_URL
   ```
   Paste your PostgreSQL URL when prompted.
   
   ```bash
   vercel env add SECRET_KEY
   ```
   Paste your secret key when prompted.

5. **Deploy to production**:
   ```bash
   vercel --prod
   ```

## Step 4: Verify Deployment

1. After deployment, Vercel will provide you with a URL (e.g., `https://your-app.vercel.app`)
2. Visit the URL to check if your application is working
3. Try logging in or registering a new user
4. Check the Vercel dashboard logs if you encounter any issues

## Troubleshooting

### Database Connection Issues

If you see database connection errors:

1. **Check your POSTGRES_URL**:
   - Make sure it's correctly formatted
   - Verify it includes the correct username, password, host, port, and database name
   - Test the connection locally first

2. **SSL Requirements**:
   If your database requires SSL, update your connection string:
   ```
   postgresql://user:password@host:port/database?sslmode=require
   ```

3. **Check Database Logs**:
   - Go to your database provider's dashboard
   - Check connection logs for any issues

### Application Errors

1. **Check Vercel Logs**:
   - Go to your project in Vercel dashboard
   - Click on "Deployments"
   - Click on the latest deployment
   - Check "Functions" logs for errors

2. **Static Files Not Loading**:
   - Make sure your `static` folder is in the root directory
   - Check that paths in your templates are correct

### Environment Variables Not Working

1. Make sure you added them in the Vercel dashboard under Settings → Environment Variables
2. Redeploy after adding environment variables
3. Environment variables are case-sensitive

## Important Notes

1. **Cold Starts**: Serverless functions on Vercel may have cold starts (1-3 seconds delay on first request)
2. **Function Timeout**: Free tier has a 10-second execution limit for serverless functions
3. **Database Connections**: Use connection pooling to avoid exhausting database connections
4. **Static Files**: Make sure your `static` folder is properly configured in `vercel.json`

## Updating Your Deployment

To update your deployment:

1. Push changes to your Git repository
2. Vercel will automatically deploy the changes
3. Or manually trigger a deployment from the Vercel dashboard

## Getting Help

- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI on Vercel Guide](https://vercel.com/guides/deploying-fastapi-with-vercel)
- Check deployment logs in Vercel dashboard

## Next Steps

After successful deployment:

1. Set up a custom domain (optional)
2. Configure production database backups
3. Monitor application performance in Vercel dashboard
4. Set up error tracking (e.g., Sentry)
