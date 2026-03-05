# Multi-Platform Media Transformation (Future Implementation)

**Status:** Planned for future implementation  
**Date:** February 2025  
**Related:** [MEDIA_UPLOAD_FUTURE.md](MEDIA_UPLOAD_FUTURE.md)

This document describes how to take **one piece of user content** (video or image) and adapt it for different platforms according to their aspect ratio and format requirements. The user uploads once; the platform delivers to YouTube (Shorts), Instagram (Reel/post), Facebook (post), etc.

---

## Platform Requirements

| Platform | Format | Aspect Ratio | Dimensions | Duration | Notes |
|----------|--------|--------------|------------|----------|-------|
| **YouTube Shorts** | Video | 9:16 (vertical) | 1080×1920 | ≤60 sec | Must be vertical |
| **YouTube (regular)** | Video | 16:9 (landscape) | 1920×1080 | Any | Standard video |
| **Instagram Reel** | Video | 9:16 (vertical) | 1080×1920 | ≤90 sec | Same as Shorts |
| **Instagram Feed** | Image/Video | 1:1, 4:5, 1.91:1 | 1080×1080 typical | — | Square or portrait |
| **Instagram Story** | Image/Video | 9:16 | 1080×1920 | ≤15 sec | Vertical |
| **Facebook Feed** | Image/Video | 1:1, 16:9, 9:16 | Flexible | — | Accepts many ratios |
| **Facebook Reel** | Video | 9:16 | 1080×1920 | — | Vertical |

**Key insight:** YouTube Shorts, Instagram Reels, and Facebook Reels all use **9:16**. If the user provides vertical content, it can go to all three with minimal or no transformation. If the user provides landscape (16:9) or square (1:1), we need to transform it.

---

## The Problem

User has **one** video or image. Different platforms need different aspect ratios:

```
User uploads: landscape video (16:9)
       │
       ├──► YouTube Shorts: needs 9:16  → transform
       ├──► Instagram Reel: needs 9:16 → transform
       ├──► Facebook Reel: needs 9:16  → transform
       └──► YouTube (regular): 16:9 OK → use as-is
```

```
User uploads: vertical video (9:16)
       │
       ├──► YouTube Shorts: 9:16 OK → use as-is
       ├──► Instagram Reel: 9:16 OK  → use as-is
       └──► Facebook Reel: 9:16 OK  → use as-is
```

---

## Transformation Strategies

### 1. Crop (Center Crop)

- Crop the center of the frame to the target aspect ratio.
- **Pros:** No black bars, fills the frame.
- **Cons:** May cut off important content at edges.

**Example:** 16:9 → 9:16: crop the sides, keep center.

### 2. Letterbox / Pillarbox (Add Bars)

- Scale to fit inside target ratio, add black (or colored) bars to fill.
- **Pros:** No content lost.
- **Cons:** Bars may look odd on some platforms.

### 3. Scale (Stretch)

- Stretch/squash to fit target ratio.
- **Pros:** Simple.
- **Cons:** Distorts the image; generally **not recommended**.

### 4. Smart Crop (AI-Assisted)

- Use face/object detection to keep the "important" part in frame.
- **Pros:** Better preservation of subject.
- **Cons:** More complex, may need ML libraries.

---

## Recommended Approach: Crop + Scale

For most cases, **center crop** is the simplest and most visually acceptable:

1. **If source is wider than target** (e.g. 16:9 → 9:16): Crop the sides (center crop).
2. **If source is taller than target** (e.g. 9:16 → 1:1): Crop top/bottom (center crop).
3. **If source matches target**: Use as-is or scale to target resolution.

---

## Implementation: Media Transformation Service

### Tools

| Tool | Use Case | Pros | Cons |
|------|----------|------|------|
| **FFmpeg** | Video resize, crop, format conversion | Industry standard, fast, no Python deps for processing | Requires FFmpeg installed |
| **ffmpeg-python** | Python wrapper for FFmpeg | Easy to use from Python | Wrapper only |
| **MoviePy** | Video editing in Python | Pure Python API, already used for Shorts validation | Slower than FFmpeg |
| **Pillow (PIL)** | Image resize, crop | Simple for images | Images only |

**Recommendation:** Use **FFmpeg** (via `ffmpeg-python` or `subprocess`) for video. Use **Pillow** for images. FFmpeg is faster and more reliable for video.

### Proposed Module: `services/media_transformer.py`

```python
# Pseudocode structure

class MediaTransformer:
    """Transform media for different platform formats."""

    PLATFORM_SPECS = {
        "youtube_shorts": {"aspect": "9:16", "max_duration": 60, "resolution": (1080, 1920)},
        "youtube_regular": {"aspect": "16:9", "resolution": (1920, 1080)},
        "instagram_reel": {"aspect": "9:16", "max_duration": 90, "resolution": (1080, 1920)},
        "instagram_feed": {"aspect": "1:1", "resolution": (1080, 1080)},
        "facebook_feed": {"aspect": "1:1", "resolution": (1080, 1080)},
    }

    def transform_video(self, source_path: str, target_format: str, output_path: str) -> str:
        """Crop/scale video to target format. Returns output path."""

    def transform_image(self, source_path: str, target_format: str, output_path: str) -> str:
        """Crop/scale image to target format. Returns output path."""
```

### FFmpeg Examples for Video

**16:9 → 9:16 (center crop):**
```bash
ffmpeg -i input.mp4 -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0" -c:a copy output.mp4
```

**9:16 → 1:1 (center crop):**
```bash
ffmpeg -i input.mp4 -vf "crop=min(iw,ih):min(iw,ih):(iw-min(iw,ih))/2:(ih-min(iw,ih))/2" -c:a copy output.mp4
```

**Scale to 1080×1920 (with padding if needed):**
```bash
ffmpeg -i input.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" -c:a copy output.mp4
```

---

## End-to-End Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User uploads ONE video/image                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Media Upload Service                                          │
│    - Store original in cloud (Cloudinary/S3)                     │
│    - Get public URL for original                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Media Transformer (for each target platform)                  │
│    - Detect source aspect ratio                                  │
│    - Generate platform-specific version (crop/scale)             │
│    - Upload transformed file to cloud                             │
│    - Get public URL for each version                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Campaign config (per channel)                                 │
│    YouTube Shorts:  video_path = local_9x16.mp4                  │
│    Instagram Reel:  media_url = https://.../reel_9x16.mp4        │
│    Facebook:       media_url = https://.../reel_9x16.mp4         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Execution handlers use the right config per channel          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Campaign Config Structure (Proposed)

Instead of a single `media_url` or `video_path`, support per-channel overrides:

```json
{
  "content": "Check out our new product!",
  "source_media": {
    "path": "/uploads/user_video.mp4",
    "type": "video"
  },
  "channel_overrides": {
    "youtube": {
      "format": "short",
      "video_path": "/tmp/transformed_9x16.mp4"
    },
    "instagram": {
      "format": "reel",
      "media_url": "https://cdn.example.com/reel_9x16.mp4"
    },
    "facebook": {
      "format": "feed",
      "media_url": "https://cdn.example.com/reel_9x16.mp4"
    }
  }
}
```

Or simpler: **one source**, transformer generates all versions at execution time, and each handler receives the appropriate version.

---

## Implementation Phases

### Phase 1: Same-Format Flow
- User provides 9:16 video → use for Shorts, Reels, Facebook Reel as-is.
- No transformation yet; just ensure one upload works everywhere when format matches.

### Phase 2: Media Upload Service
- Implement cloud upload (Cloudinary/S3).
- User file → public URL for Instagram/Facebook.
- See [MEDIA_UPLOAD_FUTURE.md](MEDIA_UPLOAD_FUTURE.md).

### Phase 3: Media Transformer
- Add `MediaTransformer` service.
- Support 16:9 → 9:16, 1:1 → 9:16, etc.
- Use FFmpeg for video, Pillow for images.

### Phase 4: Unified Campaign Flow
- User uploads once.
- Platform auto-generates versions for each selected channel.
- Execution handlers receive pre-transformed media.

---

## Dependencies to Add

```
# requirements.txt (future)
ffmpeg-python>=0.2.0   # or use subprocess + ffmpeg
Pillow>=10.0.0         # for image transformation
```

**System requirement:** FFmpeg must be installed on the server (e.g. `apt install ffmpeg` on Linux).

---

## Related Files

- `services/execution_handlers.py` – `_validate_shorts_video()` already checks 9:16
- `api_integrations/youtube.py` – `upload_video()` accepts local path
- `api_integrations/instagram.py` – `publish_media()` uses `media_url`
- `api_integrations/facebook.py` – photo/video posts use `media_url`
- [MEDIA_UPLOAD_FUTURE.md](MEDIA_UPLOAD_FUTURE.md) – Cloud storage for public URLs
