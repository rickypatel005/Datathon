# DataMind AI (Data Analyst AI)

DataMind AI is an intelligent, full-stack Data Analytics platform that empowers users to upload datasets, perform automated Exploratory Data Analysis (EDA), train Machine Learning models, and chat with an AI assistant to gain insights from their data. 

Built with a sleek, glassmorphism-inspired UI featuring a vibrant emerald and sky-blue palette, the platform supports seamless dark/light modes and robust JWT-based authentication.

## 🚀 Key Features

*   **Intelligent Data Uploads:** Upload `.csv`, `.xlsx`, or `.json` datasets. The platform automatically infers column types, computes missing values, and generates statistical summaries.
*   **AI Data Analyst Chat:** Conversational interface powered by LLMs (LangChain/CrewAI) to ask complex queries about your dataset.
*   **Machine Learning Studio:** Train and evaluate Supervised (Classification, Regression) and Unsupervised (Clustering) models directly in the browser using algorithms like Random Forest, XGBoost, SVM, and K-Means.
*   **Automated EDA:** Run deep automated data cleaning, missing value imputation, and correlation analysis.
*   **Interactive Visualizations:** Generate dynamic charts (Bar, Line, Scatter, Pie) powered by `recharts`.
*   **JWT Authentication:** Secure user registration, login, and password management using bcrypt hashing and HTTP Bearer Tokens.
*   **Customizable Workspace:** Fully synced user preferences for UI themes (Light/Dark/System), email notifications, and data sharing toggles.

## 🛠️ Technology Stack

### Frontend
*   **Framework:** React 18 with TypeScript and Vite
*   **Styling:** Tailwind CSS (with custom HSL color variables for theming)
*   **State Management:** Zustand
*   **Routing:** React Router DOM v6
*   **Icons:** Lucide React
*   **Visualizations:** Recharts

### Backend
*   **Framework:** FastAPI (Python)
*   **Database:** SQLAlchemy ORM (PostgreSQL/SQLite)
*   **Authentication:** PyJWT, passlib, bcrypt
*   **Data Science:** Pandas, Scikit-Learn, XGBoost, Numpy
*   **AI/LLM Integration:** LangChain, CrewAI

## ⚙️ Local Development Setup

### 1. Clone the repository
```bash
git clone https://github.com/Rishik-sai/data-analayst-ai.git
cd data-analayst-ai
```

### 2. Backend Setup
Navigate to the backend directory and set up the Python environment:
```bash
cd backend
python -m venv venv

# Activate Virtual Environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:
```ini
DATABASE_URL=sqlite:///./datamind.db # Or PostgreSQL URL
SECRET_KEY=your_super_secret_jwt_key
OPENAI_API_KEY=your_openai_key # If using OpenAI LLMs
GROQ_API_KEY=your_groq_key # If using Groq LLMs
```

Run the FastAPI server:
```bash
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`.

### 3. Frontend Setup
Open a new terminal and navigate to the frontend directory:
```bash
cd frontend

# Install dependencies
npm install

# Start the Vite dev server
npm run dev
```
The frontend will be available at `http://localhost:5173`.

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
