# Media Upload Flow (Future Implementation)

**Status:** Planned for future implementation  
**Date:** February 2025

This document describes the media upload gap and proposed solution for the marketing automation platform. Users create their own content (images, videos) and want to post it across YouTube, Instagram, and Facebook. The platform needs to handle this flow correctly.

---

## Current State

| Platform | How It Accepts Media | User's Local File |
|----------|----------------------|--------------------|
| **YouTube** | Local file path (`video_path`) | ✅ Works – YouTube API uploads file directly |
| **Instagram** | Public URL (`media_url`) | ❌ Gap – user has file, not URL |
| **Facebook** | Public URL (`media_url` / `image_url`) | ❌ Same gap |

### What Works Today

- **YouTube**: User provides a local file path → platform uploads the file directly via the YouTube Data API (`MediaFileUpload`). No cloud storage needed.
- **Instagram/Facebook**: Their APIs require a **publicly accessible URL**. Meta's servers fetch the media from that URL. They do not accept file uploads.

### The Gap

When a user has a local file (e.g. `my_video.mp4` or `my_image.jpg`):

1. **YouTube** – Works as-is: we use `video_path` and upload the file.
2. **Instagram / Facebook** – We need a public URL. A local path like `C:\Users\...\video.mp4` is not usable because Meta's servers cannot access it.

---

## Required Flow

```
User's file (local)
       │
       ▼
┌──────────────────────────────────────┐
│  Step 1: Upload to cloud storage     │
│  (S3, Cloudinary, etc.)             │
│  → Returns public URL                │
└──────────────────────────────────────┘
       │
       ├──► YouTube: use local path directly (already works)
       │
       ├──► Instagram: use public URL
       │
       └──► Facebook: use public URL
```

---

## Options for Hosting User Media

| Option | How It Works | Pros | Cons |
|--------|--------------|------|------|
| **Cloudinary** | Upload file → get URL | Free tier, simple API, handles images/videos | External service |
| **AWS S3** | Upload file → make object public → get URL | Flexible, scalable | More setup, billing |
| **Google Cloud Storage** | Same idea as S3 | Fits if you already use GCP | Same as S3 |
| **Self-hosted** | Store in `uploads/` and serve via your app | No extra service | App must be publicly reachable; not suitable for localhost |

---

## Recommended Approach

Add a **media upload service** that:

1. Accepts the user's file (via API, dashboard, or CLI).
2. Uploads it to a storage provider (e.g. Cloudinary or S3).
3. Returns a public URL.
4. Stores that URL in the campaign config for Instagram/Facebook.

Then the flow becomes:

1. User selects their video/image.
2. Platform uploads it to storage and gets a public URL.
3. **YouTube**: use `video_path` (local file) for upload.
4. **Instagram**: use the public URL for Reel/post.
5. **Facebook**: use the same public URL for the post.

---

## Implementation Notes

- **YouTube** execution handler already supports `video_path` in campaign config.
- **Instagram** and **Facebook** execution handlers expect `media_url` in campaign config.
- A new media upload module or service should:
  - Accept file uploads (multipart/form-data or similar).
  - Integrate with chosen storage provider (Cloudinary recommended for simplicity).
  - Return public URL for use in campaign config.
  - Optionally: support both `video_path` and `media_url` in campaign config, with logic to upload local files first and use the resulting URL for Instagram/Facebook.

---

## Related Documents

- [MULTI_PLATFORM_MEDIA_FUTURE.md](MULTI_PLATFORM_MEDIA_FUTURE.md) – Transforming one piece of content for different platform aspect ratios (Shorts, Reels, etc.)

## Related Files

- `services/execution_handlers.py` – YouTube, Instagram, Facebook handlers
- `api_integrations/youtube.py` – `upload_video()` uses local path
- `api_integrations/instagram.py` – `publish_media()` requires `media_url`
- `api_integrations/facebook.py` – photo/video posts require `media_url`
