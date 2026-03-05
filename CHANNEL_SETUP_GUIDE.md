# Channel Setup Guide: YouTube, Instagram & Facebook

**A step-by-step guide for teammates** to set up YouTube, Instagram, and Facebook so the Marketing Automation Platform works on your machine. No prior API experience needed—just follow along.

---

## Table of Contents

1. [Overview: What You're Setting Up](#1-overview-what-youre-setting-up)
2. [YouTube Setup](#2-youtube-setup)
3. [Instagram & Facebook Setup](#3-instagram--facebook-setup)
4. [Add Everything to .env](#4-add-everything-to-env)
5. [Test Your Setup](#5-test-your-setup)
6. [Troubleshooting](#6-troubleshooting)
7. [Quick Checklist](#7-quick-checklist)

---

## 1. Overview: What You're Setting Up

The platform connects to three marketing channels. Each needs different credentials:

| Channel | What You Get | What It Enables |
|---------|--------------|-----------------|
| **YouTube** | API Key + OAuth Token | Read channel stats, **upload videos** |
| **Instagram** | Access Token + Business Account ID | Read posts/insights, **publish images/videos** |
| **Facebook** | Access Token + Page ID | Read page insights, **publish posts** |

**You can set up one, two, or all three.** The platform works with whichever you configure.

---

## 2. YouTube Setup

### What You Need

- A **Google account**
- A **YouTube channel** (can be your personal one)
- About **15–20 minutes**

### Part A: API Key (for reading data)

1. **Open Google Cloud Console**
   - Go to: [console.cloud.google.com](https://console.cloud.google.com/)

2. **Create or select a project**
   - Click the project dropdown at the top
   - Click **New Project**
   - Name: `Marketing Automation Platform` (or any name)
   - Click **Create**

3. **Enable YouTube Data API**
   - Go to: [APIs & Services → Library](https://console.cloud.google.com/apis/library)
   - Search for **YouTube Data API v3**
   - Click it → Click **Enable**

4. **Create an API key**
   - Go to: [APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials)
   - Click **Create Credentials** → **API Key**
   - Copy the key
   - *(Optional)* Click **Restrict Key** → restrict to "YouTube Data API v3" → Save

5. **Save it** — you'll add this to `.env` as `YOUTUBE_API_KEY`

---

### Part B: OAuth (for uploading videos)

You need OAuth credentials so the platform can upload videos to your channel.

#### Step 1: Configure OAuth consent screen

1. Go to [APIs & Services → OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)
2. Select **External** (unless you have Google Workspace) → **Create**
3. Fill in:
   - **App name**: `Marketing Automation Platform`
   - **User support email**: your email
   - **Developer contact email**: your email
4. Click **Save and Continue**
5. **Scopes** → **Add or Remove Scopes**
   - Search for `youtube`
   - Check: `.../auth/youtube.upload`
   - Click **Update** → **Save and Continue**
6. **Test users** → **Add Users**
   - Add the Google account you'll use to upload
   - Click **Add** → **Save and Continue**
7. Click **Back to Dashboard**

#### Step 2: Create OAuth 2.0 Client ID

1. Go to [APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **Create Credentials** → **OAuth 2.0 Client ID**
3. **Application type**: **Desktop app**
4. **Name**: `YouTube Upload Client`
5. Click **Create**

#### Step 3: Download credentials

1. In the popup (or in the credentials list), find your OAuth 2.0 Client ID
2. Click the **Download JSON** button
3. Rename the file to: `youtube_oauth_credentials.json`
4. Move it to the **project root** (same folder as `README.md`)

#### Step 4: Add redirect URIs

1. Go to [Credentials](https://console.cloud.google.com/apis/credentials)
2. Click your OAuth 2.0 Client ID (the name, not the edit icon)
3. Under **Authorized redirect URIs**, click **Add URI**
4. Add: `http://localhost:8080`
5. Add: `http://localhost`
6. Click **Save**

#### Step 5: Generate the token

1. Open a terminal in the project folder
2. Activate the virtual environment:
   - Windows: `.\venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
3. Run:
   ```bash
   python scripts/generate_youtube_token.py
   ```
4. A browser window opens → sign in with your Google account → click **Allow**
5. You'll be redirected back; the token is saved to `youtube_token.json`

**YouTube setup is complete.**

---

## 3. Instagram & Facebook Setup

Instagram and Facebook use the same Facebook Developer app. You set up **one app** and get tokens for both.

### What You Need

- A **Facebook account**
- An **Instagram Business or Creator account** (not Personal)
- A **Facebook Page** linked to that Instagram account
- About **25–30 minutes**

### Part A: Create the Facebook App

1. **Go to Facebook Developers**
   - Visit: [developers.facebook.com](https://developers.facebook.com/)
   - Sign in with your Facebook account

2. **Create an app**
   - Click **My Apps** → **Create App**
   - Choose **Business** → **Next**
   - **App name**: `Marketing Automation Platform`
   - **App contact email**: your email
   - Click **Create App**

3. **Add products**
   - In the app dashboard, find **Add Products**
   - Add **Instagram Graph API** → Set Up
   - Add **Facebook Login** → Set Up

4. **Get App ID and App Secret**
   - Go to **Settings** → **Basic**
   - Copy **App ID**
   - Click **Show** next to App Secret → copy it
   - Add **Privacy Policy URL** and **Terms of Service URL** if asked (e.g. `https://example.com/privacy`)

5. **Configure Facebook Login**
   - Go to **Facebook Login** → **Settings**
   - Under **Valid OAuth Redirect URIs**, add: `http://localhost:8080/`
   - Save

---

### Part B: Link Instagram to a Facebook Page

1. **Convert Instagram to Business/Creator** (if not already)
   - Open Instagram app → **Settings** → **Account**
   - Tap **Switch to Professional Account**
   - Choose **Business** or **Creator**
   - Connect to your Facebook Page when prompted

2. **Link Instagram to your Page**
   - Go to [business.facebook.com](https://business.facebook.com/) (Meta Business Suite)
   - Select your **Page**
   - **Settings** → **Instagram** (or **Page Settings** → **Instagram**)
   - Click **Connect Instagram Account** and follow the steps

3. **Check Page roles**
   - Go to your Facebook Page → **Settings** → **Page Roles**
   - Ensure your Facebook account is **Admin** or **Editor**

---

### Part C: Add yourself as a developer (important)

If someone else created the app, they must add you:

1. In the app dashboard → **App Roles** → **Roles**
2. Click **Add People**
3. Enter your Facebook email or name
4. Select **Developer** or **Admin**
5. Click **Add**
6. Accept the invitation when you receive it

---

### Part D: Get access tokens

#### Step 1: Get a User token (Graph API Explorer)

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from the **Meta App** dropdown
3. Click **Generate Access Token**
4. In the permissions list, add:
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_manage_posts`
   - `instagram_basic`
   - `instagram_manage_insights`
   - `instagram_content_publish`
5. Click **Generate Access Token** and complete the login
6. You get a **User token** (short-lived)

#### Step 2: Get the Page token

1. In Graph API Explorer, set:
   - **GET** request
   - Endpoint: `me/accounts`
2. Click **Submit**
3. In the response, find your Page
4. Copy the **`access_token`** for that Page — this is your **Page token**
5. Copy the **`id`** for that Page — this is your **Page ID**

#### Step 3: Get the Instagram Business Account ID

1. In Graph API Explorer, set:
   - **GET** request
   - Endpoint: `{page_id}?fields=instagram_business_account`
   - Replace `{page_id}` with your Page ID from Step 2
2. Click **Submit**
3. Copy the `instagram_business_account.id` value — this is your **Instagram Business Account ID**

> **Important:** For Instagram, you use the **same Page token** as for Facebook. The Page token works for both when Instagram is linked to that Page.

#### Step 4: Make tokens long-lived (recommended)

Short-lived tokens expire in about an hour. To get a long-lived token (about 60 days):

1. Open this URL in your browser (replace the placeholders):
   ```
   https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_LIVED_USER_TOKEN
   ```
2. The response contains a new `access_token` — that's your long-lived User token
3. Use that token in Graph API Explorer to call `me/accounts` again
4. Copy the Page's `access_token` from the response — that Page token is now long-lived

---

### Part E: Instagram media requirement

For **posting to Instagram**, images and videos must be at a **public URL** (e.g. CDN, S3, or any public HTTPS link). Local files or `localhost` URLs will not work.

---

## 4. Add Everything to .env

Create or edit the `.env` file in the project root. Add the variables for the channels you set up.

### Minimum (database + Redis)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/marketing_cdp
REDIS_URL=redis://localhost:6379/0
```

### YouTube

```env
YOUTUBE_API_KEY=your_api_key_here
```

*(OAuth uses `youtube_oauth_credentials.json` and `youtube_token.json` in the project root — no .env entry needed.)*

### Instagram

```env
INSTAGRAM_ACCESS_TOKEN=your_page_access_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_ig_business_account_id

# Optional: public image URL for testing
INSTAGRAM_TEST_MEDIA_URL=https://example.com/test-image.jpg
```

### Facebook

```env
FACEBOOK_ACCESS_TOKEN=your_page_access_token
FACEBOOK_PAGE_ID=your_page_id
```

### Facebook App (for token exchange / long-lived tokens)

```env
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
```

### Example: All channels configured

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/marketing_cdp
REDIS_URL=redis://localhost:6379/0

# YouTube
YOUTUBE_API_KEY=AIzaSy...

# Instagram (use Page token)
INSTAGRAM_ACCESS_TOKEN=EAAx...
INSTAGRAM_BUSINESS_ACCOUNT_ID=17841400000000000
INSTAGRAM_TEST_MEDIA_URL=https://your-cdn.com/test.jpg

# Facebook
FACEBOOK_ACCESS_TOKEN=EAAx...
FACEBOOK_PAGE_ID=123456789012345

# Facebook App (optional but useful)
FACEBOOK_APP_ID=123456789
FACEBOOK_APP_SECRET=abc123...
```

---

## 5. Test Your Setup

### Prerequisites

1. Docker running: `docker compose up -d`
2. Database initialized: `python scripts/init_db.py`
3. Virtual environment activated

### Test commands

```bash
# Test foundations (database, config, CDP)
python test_module1.py

# Test campaign management
python test_module2.py

# Test YouTube upload (needs OAuth + video in uploads/)
python test_youtube_upload.py

# Test Instagram publish (needs token + business ID + public media URL)
python test_instagram_publish.py

# Test Facebook publish
python test_facebook_publish.py
```

---

## 6. Troubleshooting

### YouTube

| Error | What to do |
|-------|------------|
| `redirect_uri_mismatch` | Add `http://localhost:8080` and `http://localhost` to OAuth Client redirect URIs in Google Cloud Console |
| `access_denied` or "App is being tested" | Add your Google account as a test user in OAuth consent screen |
| `invalid_grant: Token expired` | Delete `youtube_token.json` and run `python scripts/generate_youtube_token.py` again |
| Can't find "Download JSON" | Go to Credentials → click your OAuth Client name → look for Download JSON on the details page |

### Instagram & Facebook

| Error | What to do |
|-------|------------|
| **Insufficient Developer Role** | Add your account in App Roles → Roles as Admin/Developer/Tester |
| **This account is not a business account** | Convert Instagram to Business/Creator and link to a Facebook Page |
| **media_url is required** | For Instagram posts, provide a public HTTPS URL for the image/video |
| **(#200) requires pages_read_engagement and pages_manage_posts** | Regenerate token with both permissions, then get a new Page token from `me/accounts` |
| **Invalid media URL** | Use a public URL (no localhost). The URL must be reachable from the internet |

### General

| Error | What to do |
|------|------------|
| `ModuleNotFoundError: No module named 'core'` | Activate virtual environment and run from project root |
| Database connection failed | Run `docker compose up -d` and check containers with `docker compose ps` |
| Token expired | Regenerate tokens and update `.env` |

**More help:** See `FIX_INSTAGRAM_DEVELOPER_ROLE.md` for details on the "Insufficient Developer Role" error.

---

## 7. Quick Checklist

Use this to confirm your setup before testing.

### YouTube

- [ ] Google Cloud project created
- [ ] YouTube Data API v3 enabled
- [ ] API key created and added to `.env` as `YOUTUBE_API_KEY`
- [ ] OAuth consent screen configured (with `youtube.upload` scope)
- [ ] Test user added (your Google account)
- [ ] OAuth 2.0 Client ID created (Desktop app)
- [ ] `youtube_oauth_credentials.json` in project root
- [ ] Redirect URIs `http://localhost:8080` and `http://localhost` added
- [ ] `python scripts/generate_youtube_token.py` run successfully
- [ ] `youtube_token.json` exists in project root

### Instagram

- [ ] Facebook App created
- [ ] Instagram Graph API and Facebook Login added
- [ ] Instagram account is Business/Creator
- [ ] Instagram linked to Facebook Page
- [ ] Your account is Admin/Developer/Tester of the app
- [ ] Page token obtained from `me/accounts`
- [ ] Permissions include `instagram_content_publish`
- [ ] `INSTAGRAM_ACCESS_TOKEN` = Page token (in `.env`)
- [ ] `INSTAGRAM_BUSINESS_ACCOUNT_ID` set (in `.env`)
- [ ] For posting: public image/video URL available

### Facebook

- [ ] Same Facebook App as Instagram
- [ ] Page token obtained from `me/accounts`
- [ ] Permissions include `pages_manage_posts` and `pages_read_engagement`
- [ ] `FACEBOOK_ACCESS_TOKEN` = Page token (in `.env`)
- [ ] `FACEBOOK_PAGE_ID` set (in `.env`)

### Project

- [ ] `.env` file created and configured
- [ ] Docker containers running (`docker compose up -d`)
- [ ] Database initialized (`python scripts/init_db.py`)
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)

---

**When all items are checked, you're ready to run the platform.**

For questions or issues, check the troubleshooting section above or ask your team lead.
