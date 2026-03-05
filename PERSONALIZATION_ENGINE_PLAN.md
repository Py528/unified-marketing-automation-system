# Personalization Engine Plan (Ollama-Powered)

**Status:** Planned for future implementation  
**Date:** February 2025  
**Module:** Module 4 – Personalization Engine

This document outlines the plan for AI-powered post personalization using Ollama. The engine supports two modes: (1) **AI-generated** content when the user provides little or no input, and (2) **suggestions and enhancements** when the user provides their own details (topic, product, key points).

---

## Overview

| Mode | User Input | What Ollama Does |
|------|------------|------------------|
| **AI-generated** | Minimal or none (e.g. "product launch") | Generates titles, captions, tags, ideas from scratch |
| **User-provided** | Topic, product name, key points, draft copy | Suggests tags, title variations, caption improvements, content ideas |

---

## Features to Implement

### 1. Title Suggestions

- **YouTube**: Video titles (optimized for SEO, click-through)
- **Generic**: Catchy titles for any platform
- **Input**: Topic, product name, or key message
- **Output**: 3–5 title options

### 2. Caption / Description Suggestions

- **Instagram**: Short captions (with hashtag suggestions)
- **Facebook**: Feed post text
- **YouTube**: Video descriptions
- **Input**: Topic, tone (professional/casual/fun), key points
- **Output**: Platform-appropriate captions

### 3. Tag / Hashtag Suggestions

- **YouTube**: Tags for discoverability
- **Instagram**: Hashtags (mix of popular + niche)
- **Input**: Topic, niche, product category
- **Output**: 5–15 relevant tags/hashtags

### 4. Content Ideas

- **Input**: Niche, past topics, goals
- **Output**: 5–10 post/video ideas with angles

### 5. Channel-Specific Optimization

- **YouTube**: Longer descriptions, SEO-focused titles, tags
- **Instagram**: Short captions, emoji-friendly, hashtag-heavy
- **Facebook**: Conversational, shareable, call-to-action
- **Input**: Same base content
- **Output**: Platform-tailored versions

---

## User Flows

### Flow A: User Has Minimal Input

```
User: "I'm launching a new coffee brand called BeanBliss"
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ Personalization Service (Ollama)                          │
│ - Generate 5 title ideas                                 │
│ - Generate 3 caption variations (short, medium, long)    │
│ - Suggest 10 hashtags                                    │
│ - Suggest 5 content ideas for future posts              │
└─────────────────────────────────────────────────────────┘
       │
       ▼
User picks or edits suggestions → Uses in campaign
```

### Flow B: User Provides Their Own Content

```
User: "Title: My Morning Routine | Topic: productivity"
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ Personalization Service (Ollama)                          │
│ - Suggest improvements to the title                      │
│ - Suggest 5 alternative titles                           │
│ - Suggest tags: productivity, morning routine, etc.      │
│ - Suggest caption ideas based on the topic               │
└─────────────────────────────────────────────────────────┘
       │
       ▼
User picks suggestions or keeps their original
```

### Flow C: Multi-Channel Campaign from One Idea

```
User: "Promoting our summer sale - 30% off"
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ Personalization Service (Ollama)                          │
│ - YouTube: SEO title + description + tags                │
│ - Instagram: Short caption + hashtags                    │
│ - Facebook: Feed post with CTA                           │
└─────────────────────────────────────────────────────────┘
       │
       ▼
One idea → Platform-specific content for each channel
```

---

## Proposed API

### Endpoint: `POST /api/suggestions` (or `/api/personalize`)

**Request body:**
```json
{
  "mode": "generate",
  "topic": "coffee brand launch",
  "product_name": "BeanBliss",
  "user_content": {
    "draft_title": "Our new coffee is here",
    "draft_caption": "Check out our latest blend"
  },
  "channels": ["youtube", "instagram", "facebook"],
  "tone": "casual",
  "include": ["titles", "captions", "tags", "ideas"]
}
```

**Response:**
```json
{
  "titles": [
    "BeanBliss Coffee Is Here – Your New Morning Ritual",
    "Introducing BeanBliss: Premium Coffee, Delivered"
  ],
  "captions": {
    "instagram": "Your new morning ritual starts here ☕ BeanBliss is live!",
    "youtube": "In this video we're introducing BeanBliss, our new premium coffee blend...",
    "facebook": "We're excited to announce BeanBliss! 30% off for launch week..."
  },
  "tags": ["coffee", "BeanBliss", "morning routine", "premium coffee", "new launch"],
  "hashtags": ["#BeanBliss", "#CoffeeLovers", "#MorningRitual", "#NewLaunch"],
  "ideas": [
    "Behind-the-scenes: How we source our beans",
    "Taste test: Comparing our blends",
    "Customer unboxing experience"
  ]
}
```

### Simpler Endpoint: `POST /api/suggest-tags`

**Request:**
```json
{
  "topic": "productivity tips",
  "platform": "instagram"
}
```

**Response:**
```json
{
  "hashtags": ["#productivity", "#productivitytips", "#mornings", "#routine", "#goals"]
}
```

---

## Implementation Architecture

### New Module: `services/personalization_service.py`

```python
# Pseudocode structure

class PersonalizationService:
    """Ollama-powered content suggestions and personalization."""

    def __init__(self, llm=None):
        # Use Ollama from config if llm not provided

    def suggest_titles(
        self,
        topic: str,
        product_name: Optional[str] = None,
        count: int = 5,
        platform: Optional[str] = None
    ) -> List[str]:
        """Generate title suggestions."""

    def suggest_captions(
        self,
        topic: str,
        platform: str,
        tone: str = "casual",
        max_length: Optional[int] = None
    ) -> List[str]:
        """Generate caption suggestions per platform."""

    def suggest_tags(
        self,
        topic: str,
        platform: str,
        count: int = 10
    ) -> Dict[str, List[str]]:
        """Suggest tags (YouTube) and hashtags (Instagram)."""

    def suggest_ideas(
        self,
        niche: str,
        count: int = 5
    ) -> List[Dict[str, str]]:
        """Suggest content ideas (title + angle)."""

    def personalize_for_channels(
        self,
        base_content: str,
        channels: List[str],
        tone: str = "casual"
    ) -> Dict[str, str]:
        """Adapt one piece of content for multiple platforms."""
```

### Prompt Templates

Use structured prompts for consistent output. Example for titles:

```
You are a marketing copywriter. Generate {count} catchy titles for:
Topic: {topic}
Product: {product_name}
Platform: {platform}

Requirements:
- Each title under 60 characters
- Include a hook or benefit
- No clickbait

Output as JSON array: ["title1", "title2", ...]
```

### Output Parsing

- Request JSON output from Ollama for structured data
- Fallback: regex or simple split if JSON parsing fails
- Validate output (e.g. title length, tag count) before returning

---

## Integration Points

### 1. Campaign Creation Flow

- **Before** user creates campaign: "Get suggestions" button → call PersonalizationService → show suggestions in UI
- **During** campaign creation: User can click "Suggest" next to title/caption/tags fields
- **Optional**: Auto-fill campaign config with AI suggestions if user chooses

### 2. Streamlit Dashboard (Module 3)

- Dedicated "Content Ideas" or "Suggestions" tab
- Input: topic, product, niche
- Output: titles, captions, tags, ideas in a simple form

### 3. API-Only (No UI Yet)

- Expose `POST /api/suggestions` for programmatic use
- CLI script: `python scripts/suggest_content.py --topic "coffee launch"`

---

## Dependencies

Already present:
- `langchain-ollama` or `langchain-community` (Ollama)
- `core.config` (ollama_model, ollama_base_url)

No new dependencies required for basic implementation.

---

## Implementation Phases

### Phase 1: Core Service (MVP)

- [ ] `PersonalizationService` class
- [ ] `suggest_titles()` – topic + product → 5 titles
- [ ] `suggest_tags()` – topic → tags + hashtags
- [ ] Simple prompts, no channel-specific logic yet
- [ ] Unit test with mock LLM

### Phase 2: Channel-Specific Suggestions

- [ ] `suggest_captions()` – per platform (YouTube, Instagram, Facebook)
- [ ] `personalize_for_channels()` – one content → multi-platform
- [ ] Platform-specific prompt templates (length, tone, hashtags)

### Phase 3: Content Ideas

- [ ] `suggest_ideas()` – niche → 5–10 post ideas
- [ ] Optional: use CDP data (past campaigns, engagement) for better ideas

### Phase 4: API & UI Integration

- [ ] `POST /api/suggestions` endpoint
- [ ] `POST /api/suggest-tags` (lightweight)
- [ ] Streamlit "Suggestions" tab (when Module 3 exists)
- [ ] CLI script for testing

### Phase 5: Enhancements

- [ ] Tone selector (professional, casual, fun)
- [ ] Language support (if needed)
- [ ] Caching for repeated topics
- [ ] A/B title suggestions (optional)

---

## Example Prompts (Reference)

### Title Generation
```
Generate 5 catchy video titles for a YouTube video about: {topic}
Product/brand: {product_name}
Keep each under 60 characters. Output as JSON array.
```

### Tag Suggestion
```
Suggest 10 relevant tags and hashtags for a social media post about: {topic}
Platform: {platform}
Include mix of popular and niche tags. Output as JSON: {"tags": [...], "hashtags": [...]}
```

### Caption (Instagram)
```
Write a short Instagram caption (1-2 sentences) for: {topic}
Tone: {tone}
Include 3-5 hashtags at the end. Keep under 150 characters for the main text.
```

### Content Ideas
```
Suggest 5 content ideas (posts or videos) for a brand in: {niche}
Each idea: title + one-sentence angle. Output as JSON array of objects.
```

---

## Error Handling & Fallbacks

- **Ollama not running**: Return friendly error, suggest starting Ollama
- **Invalid/malformed LLM output**: Retry with simplified prompt, or return empty + log
- **Timeout**: Set reasonable timeout (e.g. 30s), return partial results if possible
- **User provides no topic**: Prompt for at least a minimal topic

---

## Related Files

- `agents/campaign_manager.py` – Uses Ollama; could call PersonalizationService before create_campaign
- `core/config.py` – ollama_model, ollama_base_url, llm_provider
- `core/models.py` – May need `SuggestionRequest`, `SuggestionResponse` schemas
- [PRD.md](PRD.md) – Module 4: Personalization Engine
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) – Architecture
