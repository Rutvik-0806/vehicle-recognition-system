# Publishing and hosting

## Live site on Render (recommended)

**One-click deploy** (connects your GitHub repo and creates the web service + database):

**[Deploy to Render](https://render.com/deploy?repo=https://github.com/Rutvik-0806/vehicle-recognition-system)**

1. Sign in to [Render](https://render.com/) with GitHub.
2. Click the link above (or **New** → **Blueprint** → paste repo URL).
3. Approve the blueprint (`render.yaml` creates a **Web Service** and **PostgreSQL**).
4. Wait for the first deploy (about 5–15 minutes).
5. Open your live URL: `https://vehicle-recognition-system.onrender.com` (or the name Render shows on the dashboard).

**Login after deploy:** `admin` / `admin123` (change the password in Render → **Environment** if you keep the app public).

**Note:** The Render image omits PyTorch/YOLO to stay within free-tier limits. Upload and OCR still work via **Tesseract** and OpenCV.

---

## Push this project to GitHub

1. **Install Git** (if needed): https://git-scm.com/download/win  
2. On GitHub, create a **new empty repository** (no README/license if you already have them locally):  
   https://github.com/new  
3. In PowerShell from the project folder:

```powershell
cd d:\projectvehicle
git init
git branch -M main
git add .
git status
```

Confirm that **`.env`**, **`venv/`**, and **`db.sqlite3`** do **not** appear in `git status`. If they do, fix `.gitignore` before committing.

```powershell
git commit -m "Initial commit: Vehicle Recognition System"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your GitHub user and repository name. Use a [personal access token](https://github.com/settings/tokens) as the password when Git prompts you (HTTPS), or set up [SSH keys](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).

### After cloning elsewhere

Copy `env_example.txt` to `.env`, run `python setup.py` (or your usual setup), then `python manage.py migrate` and create a superuser as needed.

---

## “Live” hosting and Vercel

This project is a **full Django app** with **SQLite**, **file uploads**, **Tesseract OCR**, **OpenCV**, and **PyTorch / YOLOv5**. Those pieces need a **long-running server**, a **writable disk** (or external storage), and **large dependencies**. **Vercel’s default Python/serverless model is not a good fit** for that stack (strict bundle size limits, no traditional always-on Django server, no persistent local SQLite for production).

**Practical options for a public URL:**

| Platform | Notes |
|----------|--------|
| [**Render**](https://render.com/) | Python web service; use **PostgreSQL** instead of SQLite for production; add **persistent disk** or S3 for `MEDIA`; install Tesseract in the build. |
| [**Railway**](https://railway.app/) | Similar: web service + volume or object storage for media. |
| [**Fly.io**](https://fly.io/) | Docker-based; good if you package the app in a container. |

For a **simple demo**, start with **Render** or **Railway**: connect the **same GitHub repo**, set the start command (e.g. `gunicorn vehicle_system.wsgi:application`), set environment variables from `env_example.txt`, and use a **hosted database** (not SQLite) for anything you care about keeping.

If you specifically need **Vercel**, you would need a **different architecture** (for example: thin API or serverless functions **without** bundling PyTorch in the same deployment, or a separate GPU/ML service). That is a separate refactor, not a one-click import of this repository.
