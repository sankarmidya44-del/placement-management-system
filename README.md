# Student Placement Management System (SPMS) 🚀

An enterprise, cloud-native Student Placement Management System (SPMS) designed for college placement cells and corporate recruiters.

- **Cloud Database:** Serverless **Neon PostgreSQL** with connection pooling & SSL
- **Backend Service:** **Python Flask 3.1 & Gunicorn** (optimized for **Render Free Tier**)
- **Frontend & Edge Portal:** **Glassmorphism UI, Chart.js & Vercel Edge CDN** (optimized for **Vercel Free Tier**)

---

## 📁 Clean Production Architecture

```text
dbms/
├── backend/                  # Flask REST API & WSGI Service (Deploy to Render)
│   ├── database/             # Relational SQL triggers, views, and schemas
│   ├── docs/                 # System architecture, ER diagrams, test cases
│   ├── models/               # SQLAlchemy ORM models (PostgreSQL 18 compatible)
│   ├── routes/               # Modular blueprints (Auth, Admin, Jobs, API, etc.)
│   ├── services/             # Analytics and placement business logic
│   ├── static/               # Server-rendered static assets
│   ├── templates/            # Jinja2 HTML templates
│   ├── tests/                # Automated pytest suite (13 passing tests)
│   ├── .env.example          # Backend environment template
│   ├── app.py                # Application factory & database auto-init
│   ├── config.py             # Neon PostgreSQL pooling & production settings
│   ├── Dockerfile            # Container definition for cloud deployments
│   ├── gunicorn_config.py    # Gunicorn worker concurrency & timeout config
│   ├── Procfile              # Process manager declaration for Render
│   ├── render.yaml           # 1-Click Render Blueprint specification
│   ├── requirements.txt      # Production python dependencies
│   ├── run.py                # Local development server runner
│   └── wsgi.py               # WSGI entry point for Gunicorn
│
├── frontend/                 # Client UI & Edge Portal (Deploy to Vercel)
│   ├── static/               # Glassmorphic CSS, JS scripts, and Chart.js
│   ├── templates/            # Shared templates
│   ├── index.html            # Vercel Production Portal & System Status Hub
│   ├── package.json          # Vercel project descriptor
│   ├── vercel.json           # Vercel Edge CDN caching & routing
│   ├── vercel.proxy.json     # Optional full reverse proxy config for Render
│   └── README.md             # Vercel deployment walkthrough
│
├── .gitignore                # Production ignore rules
└── README.md                 # Project overview and deployment guide
```

---

## ☁️ Free Cloud Deployment Walkthrough

### 1. Backend on Render (Free Tier)
1. Push your repository to **GitHub**.
2. Go to [render.com](https://render.com) and log in.
3. Click **New +** &rarr; **Blueprint** and select your repository (it automatically picks up `backend/render.yaml`).
   *Alternatively, create a **Web Service** with:*
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -c gunicorn_config.py wsgi:app`
   - **Environment Variables:**
     - `DATABASE_URL` = `postgresql://neondb_owner:npg_nCVKtBg2dhM4@ep-blue-wave-b3o5k41a-pooler.c-4.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require`
     - `FLASK_ENV` = `production`
     - `SECRET_KEY` = `(auto-generate)`
     - `CORS_ORIGIN` = `*`
   - **Health Check Path:** `/health`
4. Click **Create Web Service**. Your backend will be live at `https://<your-service>.onrender.com`!

---

### 2. Frontend on Vercel (Free Tier)
1. Go to [vercel.com](https://vercel.com) and click **Add New...** &rarr; **Project**.
2. Import your GitHub repository.
3. Set **Root Directory** to `frontend`.
4. Click **Deploy**.
5. Once deployed, open `frontend/vercel.json` and set your Render URL under `rewrites` to enable full edge reverse proxying:
```json
{
  "rewrites": [
    { "source": "/static/(.*)", "destination": "/static/$1" },
    { "source": "/(.*)", "destination": "https://<your-render-backend>.onrender.com/$1" }
  ]
}
```

---

## 🔑 Pre-Seeded Neon Database Demo Logins

| Role | Username | Password | Access Details |
| :--- | :--- | :--- | :--- |
| **Admin / TPO** | `admin` | `admin123` | Full placement management, analytics dashboard, jobs & student records |
| **Student** | `aarav.sharma` | `student123` | Student dashboard (Placed at Google India) |
| **Student** | `priya.patel` | `student123` | Student dashboard (Shortlisted candidate) |

---

## 💻 Local Quickstart

```bash
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Run backend server
python backend/run.py

# Access URLs:
# - Web App: http://127.0.0.1:5000
# - Health:  http://127.0.0.1:5000/api/health
# - Stats:   http://127.0.0.1:5000/api/stats
```
