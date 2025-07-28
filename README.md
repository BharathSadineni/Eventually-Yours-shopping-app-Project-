# Eventually Yours Shopping App

**Eventually Yours** is a modern, AI-powered shopping assistant that provides personalized product recommendations based on your preferences and shopping context. The app uses advanced AI and live Amazon data scraping for the best experience.

[Hosted Version](https://eventuallyyours.netlify.app/)

---

## Demo Video of Eventually Yours Shopping App

<p align="center">
  <a href="https://bharathsadineniportfolio.netlify.app/static/media/EventuallyYoursShoppingAppDemo.1a1d0e806cf0a3d3af8f.mp4" target="_blank">
    <img src="https://github.com/BharathSadineni/Eventually-Yours-shopping-app-Project-/blob/main/Eventually%20Yours%20Demo%20Image.png?raw=true" alt="Eventually Yours Demo Image" width="600"/>
  </a>
</p>
<p align="center"><i>Click the image above to watch the demo video.</i></p>

---

## 📝 Project Description

Eventually Yours Shopping App is designed to revolutionize the online shopping experience. By combining real-time data scraping from Amazon with the power of AI (powered by Google Gemini), the app delivers highly relevant, context-aware product recommendations tailored to your needs.

**Key Benefits:**
- Save time searching for products—get instant, relevant suggestions.
- Find products for any occasion, from birthdays to everyday needs.
- Get recommendations in your preferred language.
- Enjoy a seamless, responsive interface on any device.

---

## 🌟 What It Does / Features

- **AI-Powered Recommendations:** Get product suggestions that fit your preferences, shopping habits, and the occasion.
- **Real-Time Amazon Scraping:** The app fetches up-to-date product info, prices, and details from Amazon for accurate recommendations.
- **Multi-Category & Occasion Support:** Shop for electronics, fashion, home goods, and more. Filter or describe the occasion for context-aware results.
- **User Profile Management:** Create a profile, select your favorite categories, and set shopping preferences for even better recommendations.
- **Personalized Experience:** Complete your profile and get recommendations tailored just for you.
- **Export/Import Data:** Easily backup or restore your profile and preferences.
- **Responsive Design:** Enjoy a beautiful, mobile-friendly UI.
- **Secure:** User data and API keys are protected and never exposed.

---

## 🏗️ Architecture Overview
```
eventually-yours-shopping-app/
├── frontend/                    # React + Vite frontend
│   ├── src/                    # Source code
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Main application pages
│   │   ├── context/            # React context providers
│   │   ├── hooks/              # Custom hooks
│   │   ├── lib/                # Utility libraries
│   │   ├── shared/             # Shared schemas and types
│   │   └── types/              # TypeScript type definitions
│   ├── public/                 # Static assets
│   ├── package.json            # Frontend dependencies
│   ├── vite.config.ts          # Vite configuration
│   ├── tailwind.config.ts      # Tailwind CSS configuration
│   └── tsconfig.json           # TypeScript configuration
├── backend/                    # Python Flask backend
│   ├── api/                    # API endpoints
│   │   └── backend_api.py      # Main Flask application
│   ├── services/               # Business logic and external integrations
│   │   ├── amazon_scraper.py   # Amazon product scraping
│   │   ├── prompt_builder.py   # AI prompt construction
│   │   ├── sorting_algorithm.py # Product sorting logic
│   │   └── improved_categories.py # Category management
│   ├── utils/                  # Helper functions
│   │   └── domain_gen.py       # Amazon domain mapping
│   ├── requirements.txt        # Python dependencies
│   ├── main.py                 # Backend entry point
│   └── run.py                  # Alternative entry point
├── docs/                       # Documentation
│   └── PERFORMANCE_OPTIMIZATIONS.md
└── README.md                   # This file
```

---

## 🚀 Quick Start

### Frontend Setup

```bash
cd frontend
npm install
npm run build
npm run dev
```
Frontend will be available at [http://localhost:5173](http://localhost:5173)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```
Backend API runs at `https://eventually-yours-shopping-app-project-production.up.railway.app`

---

## 🛠️ Feature List

- **AI Recommendations:** Personalized, context-aware product suggestions.
- **Live Amazon Data:** Always up-to-date products, prices, and details.
- **Profile & Preferences:** Manage your favorite categories and shopping habits.
- **Occasion-Based Shopping:** Get ideas for birthdays, holidays, and more.
- **Data Import/Export:** Easy backup and restore.
- **Modern UI:** Fast, accessible, and responsive for all devices.
- **Secure:** Environment variables and keys are never exposed.

---

## 🧩 Tech Stack

**Frontend:**
- React 18
- TypeScript
- Vite
- Tailwind CSS
- React Hook Form
- Zod
- Lucide React
- Radix UI

**Backend:**
- Flask (Python 3.8+)
- Beautiful Soup (Web scraping)
- Google Gemini API (AI recommendations)
- Threading (Concurrent processing)

---

## 📁 Key Components

### Frontend Structure
- `src/pages/` – Main application pages
- `src/components/ui/` – Reusable UI components
- `src/context/` – State management via React context
- `src/hooks/` – Custom React hooks
- `src/lib/` – Utility functions and API clients

### Backend Structure
- `api/` – REST API endpoints
- `services/` – Business logic and integrations
- `utils/` – Helper functions and utilities

---

## 🔧 Development

### Adding New Features
1. **Frontend:** Add components to `frontend/src/components/`
2. **Backend:** Add services to `backend/services/`
3. **API:** Add endpoints in `backend/api/backend_api.py`

### Code Style
- Frontend: ESLint + Prettier
- Backend: PEP 8
- TypeScript strict mode enabled

---

## 📚 Documentation

See the `docs/` folder for:
- Performance optimizations
- API documentation
- Deployment guides

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 🔑 Environment Setup

Before running the application, set up your API keys:

#### Option 1: Automatic Setup (Recommended)
```bash
cd backend
python setup-env.py
```
This script helps you create your `.env` file with your Gemini API key.

#### Option 2: Manual Setup
1. Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a `.env` file in the `backend/` directory:
   ```bash
   cd backend
   cp env.example .env
   ```
3. Edit `.env` and set your actual API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

⚠️ **Security Note:** `.env` is git-ignored to keep your API keys secure.

---

## 💡 Using the App

1. **Complete your profile** with categories and preferences for the best experience.
2. **Describe your shopping needs**—the AI understands any language and any context.
3. **Browse and shop** from personalized recommendations instantly.

---
