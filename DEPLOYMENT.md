# 🚀 Deploying Be Your — Production Deployment Guide

This guide provides step-by-step instructions for deploying the **Be Your** platform to professional hosting environments such as **Render** or **Railway**, along with configuring production PostgreSQL databases, secure environment variables, and Gmail SMTP services.

---

## 📋 Environment Variables Reference

When deploying to production, do not hardcode credentials. Set these environment variables in your hosting provider's dashboard:

| Variable | Description | Recommended Value |
| :--- | :--- | :--- |
| `FLASK_APP` | The entry-point runner file | `run.py` |
| `FLASK_ENV` | Mode of the application environment | `production` |
| `SECRET_KEY` | Flask session secret (must be secure) | *Generate secure hash* |
| `JWT_SECRET_KEY` | JWT authentication signature hash | *Generate secure hash* |
| `DATABASE_URL` | Production PostgreSQL connection string | *Provided by hosting platform* |
| `UPLOAD_FOLDER` | Destination for user uploaded resumes | `uploads/resumes` |
| `MAX_CONTENT_LENGTH` | Max allowed file size in bytes (5MB) | `5242880` |
| `MAIL_SERVER` | SMTP Mail Server URL | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP connection port | `587` |
| `MAIL_USE_TLS` | Enforce TLS secure transfer | `True` |
| `MAIL_USERNAME` | Your verified Gmail address | `your-email@gmail.com` |
| `MAIL_PASSWORD` | Secure 16-character App Password | *Gmail App Password* |

> [!TIP]
> You can quickly generate a secure key using Python in your terminal:
> ```bash
> python3 -c "import secrets; print(secrets.token_hex(24))"
> ```

---

## 🌐 Option 1: Deploying to Render (Recommended)

Render offers a fully-managed cloud platform with native PostgreSQL database services.

### 1. Create a PostgreSQL Database
1. Go to the **Render Dashboard** and click **New > PostgreSQL**.
2. Name your database (e.g., `be_your_db`).
3. Set the region closest to your users.
4. Click **Create Database**.
5. Once active, copy the **Internal Database URL** (for Render services) or **External Database URL** (for local testing).

### 2. Create the Web Service
1. Click **New > Web Service**.
2. Connect your GitHub repository (`Be_your-`).
3. Configure the following service settings:
   - **Name:** `be-your`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app --workers 2 --timeout 120 --log-level info`
4. Expand **Advanced** and add the environment variables listed in the Reference table above. Set `DATABASE_URL` to your **Internal Database URL**.
5. Click **Create Web Service**.

### 3. Run Database Migrations on Render
To automatically synchronize your database schema on every build, modify your **Build Command** under Render's settings:
```bash
pip install -r requirements.txt && flask db upgrade
```

---

## ⚡ Option 2: Deploying to Railway

Railway auto-provisions databases and automatically detects Python buildpacks.

### 1. Provision Platform and DB
1. In **Railway**, click **New Project > Deploy from GitHub repo**.
2. Select your repository (`Be_your-`).
3. Click **Add a Service > Database > Add PostgreSQL**.
4. Railway will automatically inject the `DATABASE_URL` variable directly into your application environment.

### 2. Configure Environment Variables
1. Select your Web Service block.
2. Go to the **Variables** tab.
3. Add the required environment keys (`SECRET_KEY`, `JWT_SECRET_KEY`, `MAIL_SERVER`, etc.).
4. Double check that the automatically injected `DATABASE_URL` matches your PostgreSQL service.

### 3. Deploy
Railway will auto-detect the `Procfile` in the root of the project and execute:
```bash
gunicorn run:app --workers 2 --timeout 120 --log-level info
```
Railway also supports running migrations via a pre-deploy shell trigger or by modifying the custom start command to:
```bash
flask db upgrade && gunicorn run:app
```

---

## 📧 Setting Up Gmail SMTP securely
To allow the registration flow to send secure verification OTPs:
1. Go to your Google Account settings, select **Security**.
2. Enable **2-Step Verification**.
3. Go to **App passwords** (under 2-step verification).
4. Select **Other (Custom name)**, type `Be Your App`, and click **Generate**.
5. Copy the secure 16-character passcode and paste it into the `MAIL_PASSWORD` environment variable (without spaces).

---

## 🧪 Production Health Checklist
Before sharing your live link with recruiters:
- [ ] Run `pytest` to make sure all units tests are green.
- [ ] Verify that database migrations (`flask db upgrade`) ran without issues.
- [ ] Upload a dummy PDF resume to test the robust fallback parser hierarchy (`pdfplumber` ➔ `pypdfium2` ➔ `pdfminer`).
- [ ] Ensure that custom portfolio themes (`zinc_indigo`, `cyberpunk`, `minimalist`) render perfectly.
