# Local Development Setup

## Quick Start

### Option 1: Using Scripts (Recommended)

**Windows:**
```bash
start-local.bat
```

**Linux/Mac:**
```bash
chmod +x start-local.sh
./start-local.sh
```

### Option 2: Manual Setup

#### 1. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env and add your GEMINI_API_KEY

# Start backend server
python main.py
```

#### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## URLs

- **Backend API**: http://localhost:5000
- **Frontend App**: http://localhost:5173
- **Backend Health Check**: http://localhost:5000/api/health

## Environment Variables

Create a `.env` file in the `backend` directory:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

Get your API key from: https://makersuite.google.com/app/apikey

## Development Workflow

1. **Make changes** to backend code in `backend/` directory
2. **Backend auto-reloads** when you save changes (Flask debug mode)
3. **Make changes** to frontend code in `frontend/src/` directory
4. **Frontend auto-reloads** when you save changes (Vite dev mode)

## API Endpoints

All API calls from frontend are automatically proxied to `http://localhost:5000` via Vite proxy configuration.

## Troubleshooting

### Backend Issues
- Check if Python dependencies are installed: `pip install -r requirements.txt`
- Verify GEMINI_API_KEY is set in `.env` file
- Check backend logs in the terminal

### Frontend Issues
- Check if Node.js dependencies are installed: `npm install`
- Clear browser cache and reload
- Check browser console for errors

### Port Conflicts
- Backend uses port 5000
- Frontend uses port 5173
- If ports are in use, change them in the respective config files

## Switching Back to Production

To switch back to the deployed backend:

1. **Frontend**: Change `BACKEND_BASE_URL` in `frontend/src/pages/shopping.tsx` back to:
   ```typescript
   const BACKEND_BASE_URL = "https://eventually-yours-shopping-app.onrender.com";
   ```

2. **Vite Config**: Change proxy target in `frontend/vite.config.ts` back to:
   ```typescript
 