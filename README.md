<p align="center">
  <img src="https://img.shields.io/badge/DataMind-AI-00C896?style=for-the-badge&logo=sparkles&logoColor=white" alt="DataMind AI" />
</p>

<h1 align="center">🧠 DataMind AI — Autonomous Data Analyst Platform</h1>

<p align="center">
  <em>Upload your data. Let AI do the analysis. Get actionable insights in minutes.</em>
</p>

<p align="center">
  <a href="https://github.com/Rishik-sai/data-analayst-ai/actions/workflows/test.yml">
    <img src="https://github.com/Rishik-sai/data-analayst-ai/actions/workflows/test.yml/badge.svg" alt="Backend Tests" />
  </a>
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License" />
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white" alt="React 19" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/TypeScript-5.0+-3178C6?logo=typescript&logoColor=white" alt="TypeScript" />
</p>

---

## 🌐 Live Demo

| Service | URL |
|---------|-----|
| **🖥️ Frontend (React App)** | [https://datamind-frontend1.onrender.com](https://datamind-frontend1.onrender.com) |
| **⚙️ Backend (FastAPI)** | [https://data-analayst-backend.onrender.com](https://data-analayst-backend.onrender.com) |
| **📂 GitHub Repository** | [https://github.com/Rishik-sai/data-analayst-ai](https://github.com/Rishik-sai/data-analayst-ai) |

> **Note:** The app is hosted on Render's free tier. The first request may take ~30 seconds while the server spins up.

---

## 📖 About the Project

**DataMind AI** is a full-stack, AI-powered data analytics platform that transforms raw data into actionable insights. Built with a modern glassmorphism-inspired UI, it provides an end-to-end workflow for data professionals — from uploading datasets, performing automated exploratory data analysis (EDA), training machine learning models, to conversing with an AI assistant that understands your data.

The platform leverages a **multi-agent architecture** powered by CrewAI and LangChain, where 8 specialized AI agents collaborate to analyze your data:

| Agent | Role |
|-------|------|
| 🔍 **Senior Data Analyst** | Understands dataset structure, column types & relationships |
| 🧹 **Data Quality Engineer** | Cleans data — handles missing values, duplicates & outliers |
| 📊 **Statistical Analyst** | Performs EDA — correlations, distributions & trend analysis |
| 🎨 **Visualization Expert** | Creates insightful charts and visualizations |
| 🤖 **ML Engineer** | Trains, evaluates & optimizes machine learning models |
| 💼 **Business Analyst** | Translates findings into actionable business insights |
| 📝 **Report Writer** | Compiles professional analysis reports |
| ✅ **QA Analyst** | Validates accuracy and detects potential errors |

---

## 🚀 Key Features

### 📁 Intelligent Data Uploads
- Upload `.csv`, `.xlsx`, or `.json` datasets (up to 100 MB)
- Automatic column type inference, missing value detection & statistical summaries
- Real-time upload progress tracking with status indicators

### 💬 AI Data Analyst Chat
- Conversational interface powered by LLMs (OpenAI / Groq / Anthropic)
- Ask complex natural language questions about your dataset
- Context-aware responses with persistent chat history per session

### 🧪 Machine Learning Studio
Train and evaluate models directly in the browser:

| Type | Algorithms |
|------|-----------|
| **Classification** | Random Forest, XGBoost, SVM, Logistic Regression, Decision Tree, KNN, Naive Bayes, Neural Network |
| **Regression** | Random Forest, Gradient Boosting, Linear Regression, Ridge, Lasso, SVR, Decision Tree, KNN, Neural Network |
| **Clustering** | K-Means, DBSCAN, Agglomerative, Gaussian Mixture |

- Automatic feature preparation & label encoding
- Comprehensive metrics: Accuracy, F1, Precision, Recall, R², MSE, Silhouette Score
- Model persistence & comparison

### 📈 Automated EDA
- Deep statistical analysis with correlation matrices
- Missing value analysis & automated imputation strategies
- Outlier detection and distribution analysis
- Data type inference and cardinality checks

### 📊 Interactive Visualizations
- Dynamic charts: Bar, Line, Scatter, Pie (powered by Recharts & Plotly)
- Auto-suggested visualizations based on column types
- Export-ready chart generation

### 🔐 JWT Authentication
- Secure user registration & login with bcrypt password hashing
- HTTP Bearer token authentication (stateless, no cookies)
- Role-based access control (Admin, Analyst, Viewer)
- Password management & profile settings

### 🎨 Customizable Workspace
- Light / Dark / System theme modes with smooth transitions
- User preferences synced to backend (theme, notifications, data sharing)
- Responsive sidebar navigation with collapse/expand
- Glassmorphism-inspired UI with Geist font

### 📄 Report Generation
- Auto-generated analysis reports combining EDA, ML & business insights
- Structured report sections with executive summaries
- Report history and management

---

## 🛠️ Technology Stack

### Frontend
| Technology | Purpose |
|-----------|---------|
| **React 19** | UI framework with TypeScript |
| **Vite 8** | Lightning-fast build tool & dev server |
| **Tailwind CSS 3** | Utility-first CSS with custom HSL theming |
| **Zustand** | Lightweight state management |
| **React Router v6** | Client-side routing with protected routes |
| **Recharts** | Responsive chart components |
| **Plotly.js** | Advanced interactive visualizations |
| **Lucide React** | Beautiful icon library |
| **Axios** | HTTP client for API communication |
| **React Markdown** | Markdown rendering for AI responses |

### Backend
| Technology | Purpose |
|-----------|---------|
| **FastAPI** | High-performance async Python web framework |
| **SQLAlchemy ORM** | Database abstraction (PostgreSQL / SQLite) |
| **Pydantic v2** | Data validation & settings management |
| **CrewAI** | Multi-agent AI orchestration framework |
| **LangChain** | LLM integration layer (OpenAI, Groq, Anthropic) |
| **Pandas & NumPy** | Data manipulation & numerical computing |
| **Scikit-Learn** | Machine learning algorithms & metrics |
| **XGBoost** | Gradient boosting implementation |
| **PyJWT** | JSON Web Token authentication |
| **Passlib + bcrypt** | Secure password hashing |

### DevOps & Infrastructure
| Technology | Purpose |
|-----------|---------|
| **Docker & Docker Compose** | Containerized development & deployment |
| **Render** | Cloud hosting (Frontend static site + Backend web service + PostgreSQL) |
| **GitHub Actions** | CI pipeline with automated testing |
| **PostgreSQL** | Production database |
| **SQLite** | Local development & testing database |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite)                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │Dashboard │ │ Datasets │ │   Chat   │ │  Models  │  ...       │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘            │
│       └─────────────┴────────────┴─────────────┘                 │
│                          │ Zustand Store                         │
│                          │ fetchWithAuth (Bearer Token)          │
└──────────────────────────┼───────────────────────────────────────┘
                           │ REST API (HTTPS)
┌──────────────────────────┼───────────────────────────────────────┐
│                    BACKEND (FastAPI)                              │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                     API Routes                            │    │
│  │  /api/auth/*  /api/datasets/*  /api/chat  /api/models/*  │    │
│  └────┬──────────────┬────────────────┬──────────┬──────────┘    │
│       │              │                │          │                │
│  ┌────▼────┐  ┌──────▼──────┐  ┌─────▼────┐ ┌──▼──────────┐    │
│  │  Auth   │  │  Analysis   │  │  CrewAI  │ │  ML Tools   │    │
│  │ (JWT)   │  │   Tools     │  │  Agents  │ │ (Sklearn)   │    │
│  └────┬────┘  └──────┬──────┘  └─────┬────┘ └──┬──────────┘    │
│       └──────────────┴───────────────┴──────────┘                │
│                          │                                       │
│              ┌───────────▼───────────┐                           │
│              │   SQLAlchemy ORM      │                           │
│              │ (PostgreSQL / SQLite) │                           │
│              └───────────────────────┘                           │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
data-analayst-ai/
├── .github/
│   └── workflows/
│       └── test.yml              # GitHub Actions CI pipeline
├── backend/
│   ├── agents/
│   │   ├── agents.py             # 8 CrewAI agent definitions
│   │   ├── chat_agent.py         # Conversational AI chat agent
│   │   ├── crew.py               # CrewAI orchestration & LLM config
│   │   └── tasks.py              # CrewAI task definitions
│   ├── api/
│   │   └── routes.py             # All FastAPI route handlers (603 lines)
│   ├── database/
│   │   ├── models.py             # SQLAlchemy ORM models (User, Dataset, MLModel, etc.)
│   │   ├── schemas.py            # Pydantic request/response schemas
│   │   └── session.py            # Database session management
│   ├── tools/
│   │   ├── analysis_tools.py     # Data loading, cleaning, EDA, visualization tools
│   │   └── ml_tools.py           # ML training, evaluation & model persistence
│   ├── tests/
│   │   ├── test_analysis_tools.py
│   │   ├── test_api_integration.py
│   │   └── test_ml_tools.py
│   ├── auth.py                   # JWT auth utilities (hash, verify, create token)
│   ├── config.py                 # Pydantic settings (env vars, LLM config)
│   ├── main.py                   # FastAPI app entry point
│   ├── migrate_db.py             # Database migration script
│   ├── seed.py                   # Database seeder with sample data
│   ├── Dockerfile                # Backend Docker image
│   └── requirements.txt          # Python dependencies
├── frontend/
│   ├── public/
│   │   └── _redirects             # SPA routing for Render static hosting
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.tsx         # App layout with sidebar
│   │   │   └── Sidebar.tsx        # Navigation sidebar
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx      # Overview with stats & recent activity
│   │   │   ├── Chat.tsx           # AI conversational interface
│   │   │   ├── Datasets.tsx       # Dataset upload & management
│   │   │   ├── Visualizations.tsx # Interactive chart builder
│   │   │   ├── Models.tsx         # ML model training studio
│   │   │   ├── Reports.tsx        # Analysis reports viewer
│   │   │   ├── Settings.tsx       # User preferences & profile
│   │   │   ├── Login.tsx          # Authentication page
│   │   │   └── Register.tsx       # User registration page
│   │   ├── store/
│   │   │   └── useStore.ts        # Zustand global state
│   │   ├── utils/
│   │   │   └── apiClient.ts       # Authenticated API helper
│   │   ├── App.tsx                # Root component with routing
│   │   ├── App.css                # Global styles
│   │   ├── index.css              # Tailwind directives & base styles
│   │   └── main.tsx               # React entry point
│   ├── Dockerfile                 # Frontend Docker image
│   ├── package.json               # Node.js dependencies
│   ├── tailwind.config.js         # Tailwind CSS configuration
│   ├── vite.config.ts             # Vite build configuration
│   └── tsconfig.json              # TypeScript configuration
├── docker-compose.yml             # Full-stack Docker orchestration
├── render.yaml                    # Render.com deployment blueprint
├── LICENSE                        # MIT License
└── README.md                      # This file
```

---

## ⚙️ Local Development Setup

### Prerequisites
- **Python 3.10+** with `pip`
- **Node.js 18+** with `npm`
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/Rishik-sai/data-analayst-ai.git
cd data-analayst-ai
```

### 2. Backend Setup
```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:
```ini
# Database (SQLite for local dev, PostgreSQL for production)
DATABASE_URL=sqlite:///./datamind.db

# JWT Secret (generate a strong random string)
SECRET_KEY=your_super_secret_jwt_key_here

# LLM Provider Configuration (choose one)
LLM_PROVIDER=groq          # Options: openai, groq, anthropic
LLM_MODEL=llama3-70b-8192  # Model name for your chosen provider

# API Keys (set the key for your chosen provider)
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
ANTHROPIC_API_KEY=your_anthropic_key
```

Run the FastAPI server:
```bash
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

### 3. Frontend Setup
Open a new terminal:
```bash
cd frontend

# Install dependencies
npm install --legacy-peer-deps

# Start the Vite dev server
npm run dev
```
The frontend will be available at `http://localhost:5173`.

### 4. Docker Setup (Alternative)
Run the entire stack with a single command:
```bash
docker-compose up --build
```
This starts PostgreSQL, Redis, the FastAPI backend, a Celery worker, and the React frontend — all pre-configured and connected.

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/register` | Register a new user |
| `POST` | `/api/login` | Login and receive JWT token |
| `GET` | `/api/users/me` | Get current user profile |
| `PUT` | `/api/users/me/preferences` | Update user preferences |

### Datasets
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/datasets/upload` | Upload a new dataset (CSV/XLSX/JSON) |
| `GET` | `/api/datasets` | List all user datasets |
| `GET` | `/api/datasets/{id}` | Get dataset details & metadata |
| `GET` | `/api/datasets/{id}/preview` | Preview dataset rows |
| `DELETE` | `/api/datasets/{id}` | Delete a dataset |

### Analysis & Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/analyze` | Run automated analysis on a dataset |
| `POST` | `/api/chat` | Send a message to the AI analyst |
| `POST` | `/api/visualize` | Generate chart data for a dataset |

### Machine Learning
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/models/train` | Train an ML model |
| `GET` | `/api/models` | List all trained models |

### Dashboard & Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/dashboard/stats` | Get dashboard statistics |
| `GET` | `/api/dashboard/activity` | Get recent activity feed |
| `GET` | `/api/reports` | List all generated reports |

> 📚 Full interactive API documentation is available at `/docs` (Swagger UI) when running the backend.

---

## 🧪 Testing

Run the backend test suite:
```bash
cd backend
PYTHONPATH=. pytest tests/ -v
```

Tests cover:
- **Analysis Tools** — Dataset loading, EDA, cleaning, chart generation
- **ML Tools** — Model training, evaluation metrics, feature preparation
- **API Integration** — End-to-end endpoint testing with auth flows

CI runs automatically on every push and PR to `main` via GitHub Actions.

---

## 🚢 Deployment

The project includes a **Render Blueprint** (`render.yaml`) for one-click deployment:

1. Fork this repository
2. Connect your GitHub account to [Render](https://render.com)
3. Create a new **Blueprint** and select this repo
4. Render will automatically provision:
   - **PostgreSQL** database (free tier)
   - **FastAPI** backend (Docker web service)
   - **React** frontend (static site with SPA routing)
5. Set your secret environment variables (`SECRET_KEY`, API keys) in the Render dashboard

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Rishik Sai**
- GitHub: [@Rishik-sai](https://github.com/Rishik-sai)

---

<p align="center">
  <b>⭐ Star this repo if you find it useful! ⭐</b>
</p>
