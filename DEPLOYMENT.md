# Publishing and hosting

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
