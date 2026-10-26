# SPMS Frontend - Vercel Edge Deployment

Production-optimized frontend for the **Student Placement Management System (SPMS)** with Edge CDN caching, instant loading, and seamless backend reverse proxying.

---

## 🚀 Free Deployment on Vercel (Step-by-Step)

### Option 1: Vercel Dashboard (Fastest, 2 Minutes)
1. Push your repository to **GitHub**.
2. Go to [vercel.com](https://vercel.com) and log in with GitHub.
3. Click **Add New...** &rarr; **Project**.
4. Import your `dbms` repository.
5. In the configuration screen:
   - **Framework Preset:** `Other`
   - **Root Directory:** Click `Edit` and select **`frontend`**
   - Click **Deploy**!

### Option 2: Full Reverse Proxy to Render Backend
Once your Render backend is live (e.g. `https://spms-backend.onrender.com`), enable direct reverse proxying so users access everything via your single Vercel custom domain:

1. Open `frontend/vercel.json`
2. Update the rewrites to point to your Render backend:
```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "version": 2,
  "cleanUrls": true,
  "headers": [
    {
      "source": "/static/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ],
  "rewrites": [
    {
      "source": "/static/(.*)",
      "destination": "/static/$1"
    },
    {
      "source": "/(.*)",
      "destination": "https://YOUR-RENDER-BACKEND.onrender.com/$1"
    }
  ]
}
```
3. Commit and push. Vercel will automatically redeploy!

---

## 🛠️ Local Development
To test the frontend locally:
```bash
# Using Node / serve:
npx serve frontend

# Or using Python:
python -m http.server 3000 --directory frontend
```
Open [http://localhost:3000](http://localhost:3000).
