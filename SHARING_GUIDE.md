# 🏥 Medical Diary — 24/7 Cloud Deployment & Sharing Guide

This guide explains how to:
1. **Host the app online 24/7** so it stays accessible on your phone and PC even when your computer is completely turned off.
2. **Share with New Users** so they can start with their own private, independent medical diary.
3. **Migrate Existing Users** with zero data loss so all their existing medical records and history carry over seamlessly.

---

## ☁️ Step 1: Host Online 24/7 (Free Cloud Deployment)

To keep the application accessible around the clock with your PC turned off, host it on a free cloud hosting platform like **Render.com** or **Railway.app**.

### Deploying to Render.com (Recommended & Free):

1. **Push this project to GitHub**:
   - If not already on GitHub, create a private or public GitHub repository (e.g., `medical-diary`).
   - Push your code to your GitHub repository:
     ```bash
     git remote add origin https://github.com/YOUR_USERNAME/medical-diary.git
     git push -u origin master
     ```
2. **Create a Free Account on Render**:
   - Go to [render.com](https://render.com) and sign in with your GitHub account.
3. **Create a New Web Service**:
   - Click **New +** -> **Web Service**.
   - Select your `medical-diary` repository.
   - Set the following settings:
     - **Name**: `medical-diary` (or your preferred name)
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn src.app:app --host 0.0.0.0 --port $PORT`
     - **Instance Type**: `Free`
   - *(Optional Persistent Disk)*: In **Disks**, add a disk mounted at `/app/data` (1 GB) so the SQLite database persists across redeploys.
4. **Click "Deploy Web Service"**:
   - Within 2-3 minutes, Render provides your permanent public HTTPS URL:
     ```
     https://medical-diary-xxxx.onrender.com
     ```
   - **Your PC can now be powered off.** The app will run 24/7 and be accessible from any phone, tablet, or computer anywhere in the world!

---

## 👥 Step 2: Sharing with NEW Users

When giving the app to a friend, family member, or client who is starting fresh:

1. **Send them your cloud link**:
   - Example: `https://medical-diary-xxxx.onrender.com`
2. **They Create Their Private Account**:
   - When they open the link, they will see the secure sign-in page.
   - They click **"Create Account"** (or "Зарегистрироваться" / "Registruj se").
   - They enter their name, email, and a password.
3. **100% Private & Isolated Vault**:
   - Their account is completely independent.
   - They start with a clean diary for themselves and can add their own family members.
   - They will **never** see your records or anyone else's records.
4. **Install on Phone Home Screen (1-Tap Native App Feel)**:
   - **iPhone (Safari)**:
     1. Open the web link in Safari.
     2. Tap the **Share** button (box with arrow pointing up).
     3. Tap **"Add to Home Screen"**.
     4. Tap **Add**.
   - **Android (Chrome)**:
     1. Open the web link in Chrome.
     2. Tap the three dots (⋮) in the top-right corner.
     3. Tap **"Install app"** or **"Add to Home Screen"**.
   - Now the app opens with its official icon, full-screen, without any browser address bar!

---

## 🔄 Step 3: Upgrading for EXISTING Users (Zero Data Loss)

If you or someone has already been using the diary on your local PC and has existing medical records, follow these 3 simple steps to transfer all data:

### 1. Download Backup from the Existing / Local App:
- Open your local app in the browser (`http://localhost:8000`).
- In the top header bar, click the **Download Backup** button (<i class="fa-solid fa-download"></i>).
  *(Or navigate directly to `http://localhost:8000/api/export?download=true`)*.
- A backup file named `medical_diary_backup.json` will be saved to your device. This file contains 100% of your profiles, medical history, lab records, and reminders.

### 2. Sign In to the New Cloud App:
- Open your new 24/7 cloud URL (e.g. `https://medical-diary-xxxx.onrender.com`).
- Log in to your account (or register with your email).

### 3. One-Click Import:
- In the top header bar, click the **Import Backup Data** button (<i class="fa-solid fa-file-import"></i>).
- Select your `medical_diary_backup.json` file.
- Click **"Import Now"**.
- All family profiles, past doctor visits, lab tests, prescriptions, and calendar reminders will immediately appear in your private cloud account!

---

## 🔒 Step 4: Privacy & Security Architecture

- **Cryptographic Password Security**: Passwords are never stored in plaintext. They are salted with cryptographically secure random bytes and hashed using `PBKDF2-HMAC-SHA256` (100,000 rounds).
- **Session Authentication**: Secure tamper-proof HMAC-signed tokens (`user_id:timestamp:signature`) prevent session hijacking.
- **Row-Level User Isolation**: Every profile, clinical record, biomarker trend, and reminder is strictly tagged with `user_id`. Every database query enforces `WHERE user_id = ?`, making cross-account data leaks mathematically impossible.
- **Isolated File Attachments**: Uploaded lab PDFs and medical images are segregated into per-user directories (`uploads/user_<id>/`).

---

## 📋 Summary of Sharing Cheatsheet

| Target User | What to Give Them | What They Do | Data Privacy |
| :--- | :--- | :--- | :--- |
| **New User** | Cloud Web URL | Click "Create Account" -> Add to phone home screen | Clean, 100% private account |
| **Existing User** | Cloud Web URL + Backup instructions | Export JSON from old app -> Register on cloud -> Click "Import Backup Data" | All existing records restored into their private account |
