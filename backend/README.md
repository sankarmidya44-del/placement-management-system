# SPMS Backend - Render Deployment Guide

Production-ready Flask application powered by **Neon PostgreSQL** and served via **Gunicorn WSGI**.

---

## 🚀 Free Deployment on Render (Step-by-Step)

### Option 1: Render Blueprints (1-Click Automated)
1. Push your repository to **GitHub**.
2. Go to [render.com](https://render.com) and log in.
3. Click **New +** &rarr; **Blueprint**.
4. Select your `dbms` repository.
5. Render will automatically detect `backend/render.yaml` and configure the Web Service with:
   - Root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn -c gunicorn_config.py wsgi:app`
   - Health check path: `/health`
   - Pre-configured `DATABASE_URL` for Neon PostgreSQL
6. Click **Apply** to deploy!

---

### Option 2: Manual Web Service Setup
1. On [render.com](https://render.com), click **New +** &rarr; **Web Service**.
2. Connect your GitHub repository.
3. Configure settings:
   | Setting | Value |
   | :--- | :--- |
   | **Name** | `spms-backend` |
   | **Region** | `Singapore` (or nearest to your Neon region) |
   | **Branch** | `main` |
   | **Root Directory** | `backend` |
   | **Runtime** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `gunicorn -c gunicorn_config.py wsgi:app` |
   | **Plan** | `Free` |

4. Under **Environment Variables**, add:
   - `FLASK_ENV` = `production`
   - `DATABASE_URL` = `postgresql://neondb_owner:npg_nCVKtBg2dhM4@ep-blue-wave-b3o5k41a-pooler.c-4.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require`
   - `SECRET_KEY` = `(Click Generate or enter a strong secret)`
   - `CORS_ORIGIN` = `*`

5. Under **Health Check Path**, enter:
   - `/health`

6. Click **Create Web Service**.

---

## 🧪 Local Testing
```bash
# Navigate to backend:
cd backend

# Run with Gunicorn:
gunicorn -c gunicorn_config.py wsgi:app

# Or run with development server:
python run.py
```
Open [http://localhost:5000](http://localhost:5000).
