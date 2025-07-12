# Deployment Guide - Eventually Yours Shopping App

## Prerequisites

1. **GitHub Account** - To host your code
2. **Render Account** - For hosting backend and frontend
3. **Google Gemini API Key** - For AI recommendations

## Step 1: Prepare Your Code

### 1.1 Create Environment File
Create a `.env` file in the `backend/` directory:

```bash
# Copy the example file
cp backend/env.example backend/.env
```

Edit `backend/.env` and add your actual API key:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 1.2 Test Locally
```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

## Step 2: Deploy to GitHub

1. **Initialize Git** (if not already done):
```bash
git init
git add .
git commit -m "Initial commit"
```

2. **Create GitHub Repository**:
   - Go to GitHub.com
   - Create a new repository
   - Don't initialize with README (you already have one)

3. **Push to GitHub**:
```bash
git remote add origin https://github.com/yourusername/eventually-yours-shopping-app.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy Backend to Render

1. **Create Web Service**:
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Backend Service**:
   - **Name**: `eventually-yours-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

3. **Environment Variables**:
   - Go to "Environment" tab
   - Add the following variables:
     - `GEMINI_API_KEY`: Your actual Gemini API key
     - `FLASK_ENV`: `production`
     - `FLASK_DEBUG`: `False`

4. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Note the URL (e.g., `https://eventually-yours-backend.onrender.com`)

## Step 4: Deploy Frontend to Render

1. **Create Static Site**:
   - Go to Render Dashboard
   - Click "New +" → "Static Site"
   - Connect your GitHub repository

2. **Configure Frontend Service**:
   - **Name**: `eventually-yours-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

3. **Environment Variables** (if needed):
   - Add any frontend environment variables

4. **Deploy**:
   - Click "Create Static Site"
   - Wait for deployment to complete
   - Note the URL (e.g., `https://eventually-yours-frontend.onrender.com`)

## Step 5: Update Frontend API URL

1. **Update API Configuration**:
   Edit `frontend/src/lib/apiClient.ts`:
   ```typescript
   const API_BASE_URL = process.env.NODE_ENV === 'production' 
     ? 'https://eventually-yours-shopping-app-project-production.up.railway.app'
: 'https://eventually-yours-shopping-app-project-production.up.railway.app';
   ```

2. **Redeploy Frontend**:
   - Push changes to GitHub
   - Render will automatically redeploy

## Step 6: Configure Custom Domain (Optional)

1. **Add Custom Domain**:
   - Go to your Render service
   - Click "Settings" → "Custom Domains"
   - Add your domain
   - Configure DNS as instructed

## Security Notes

✅ **API Keys Secured**: All API keys are now in environment variables
✅ **GitIgnore Updated**: Sensitive files are excluded from version control
✅ **Production Ready**: Environment-specific configurations

## Troubleshooting

### Common Issues:

1. **API Key Not Found**:
   - Check environment variables in Render
   - Ensure `.env` file exists locally

2. **CORS Errors**:
   - Verify backend URL in frontend configuration
   - Check CORS settings in backend

3. **Build Failures**:
   - Check build logs in Render
   - Verify all dependencies are in requirements.txt/package.json

### Support:
- Check Render documentation: https://render.com/docs
- Check Flask documentation: https://flask.palletsprojects.com/
- Check Vite documentation: https://vitejs.dev/ 