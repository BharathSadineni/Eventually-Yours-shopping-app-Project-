# Eventually Yours Shopping App

A modern AI-powered shopping assistant that provides personalized product recommendations based on user preferences and shopping context.

## 🏗️ Architecture

```
eventually-yours-shopping-app/
├── frontend/                    # React + Vite frontend
│   ├── src/                    # Source code
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/             # Page components
│   │   ├── context/           # React context providers
│   │   ├── hooks/             # Custom React hooks
│   │   ├── lib/               # Utility libraries
│   │   ├── shared/            # Shared schemas and types
│   │   └── types/             # TypeScript type definitions
│   ├── public/                # Static assets
│   ├── package.json           # Frontend dependencies
│   ├── vite.config.ts         # Vite configuration
│   ├── tailwind.config.ts     # Tailwind CSS configuration
│   └── tsconfig.json          # TypeScript configuration
├── backend/                    # Python Flask backend
│   ├── api/                   # API endpoints
│   │   └── backend_api.py     # Main Flask application
│   ├── services/              # Business logic services
│   │   ├── amazon_scraper.py  # Amazon product scraping
│   │   ├── prompt_builder.py  # AI prompt construction
│   │   ├── sorting_algorithm.py # Product sorting logic
│   │   └── improved_categories.py # Category management
│   ├── utils/                 # Utility functions
│   │   └── domain_gen.py      # Amazon domain mapping
│   ├── requirements.txt       # Python dependencies
│   ├── main.py               # Backend entry point
│   └── run.py                # Alternative entry point
├── docs/                      # Documentation
│   └── PERFORMANCE_OPTIMIZATIONS.md
└── README.md                  # This file
```

## 🚀 Quick Start

### Frontend Setup

```bash
cd frontend
npm install
npm run build
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

The backend API will be available at `https://eventually-yours-shopping-app.onrender.com`

## 🛠️ Features

- **Personalized Recommendations**: AI-powered product suggestions based on user preferences
- **Multi-Category Support**: Recommendations across various product categories
- **Real-time Scraping**: Live product data from Amazon
- **User Profile Management**: Save and manage user preferences
- **Export/Import**: Backup and restore user data
- **Responsive Design**: Modern UI that works on all devices

## 🧩 Tech Stack

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **React Hook Form** - Form management
- **Zod** - Schema validation
- **Lucide React** - Icons
- **Radix UI** - Accessible components

### Backend
- **Flask** - Web framework
- **Python 3.8+** - Runtime
- **Beautiful Soup** - Web scraping
- **Google Gemini API** - AI recommendations
- **Threading** - Concurrent processing

## 📁 Key Components

### Frontend Structure
- `src/pages/` - Main application pages
- `src/components/ui/` - Reusable UI components
- `src/context/` - React context for state management
- `src/hooks/` - Custom React hooks
- `src/lib/` - Utility functions and API clients

### Backend Structure
- `api/` - REST API endpoints
- `services/` - Business logic and external integrations
- `utils/` - Helper functions and utilities

## 🔧 Development

### Adding New Features
1. Frontend: Add components in `frontend/src/components/`
2. Backend: Add services in `backend/services/`
3. API: Add endpoints in `backend/api/backend_api.py`

### Code Style
- Frontend: ESLint + Prettier
- Backend: PEP 8
- TypeScript strict mode enabled

## 📚 Documentation

See the `docs/` folder for detailed documentation including:
- Performance optimizations
- API documentation
- Deployment guides

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🔑 Environment Setup

Before running the application, you need to set up your API keys:

### Option 1: Automatic Setup (Recommended)
```bash
cd backend
python setup-env.py
```
This will guide you through creating your `.env` file with your Gemini API key.

### Option 2: Manual Setup
1. Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a `.env` file in the `backend/` directory:
```bash
cd backend
cp env.example .env
```
3. Edit `.env` and replace `your_gemini_api_key_here` with your actual API key:
```
GEMINI_API_KEY=your_actual_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

⚠️ **Security Note**: The `.env` file is automatically ignored by git to protect your API keys.