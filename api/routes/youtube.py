from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import json

from core.database import get_db
from core.config import get_settings
from api_integrations.youtube import YouTubeIntegration

router = APIRouter()
settings = get_settings()

def get_youtube_integration():
    """Dependency for YouTube integration."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    token_file = os.path.join(project_root, "youtube_token.json")
    
    creds = {"api_key": settings.youtube_api_key}
    if os.path.exists(token_file):
        creds["oauth2_credentials"] = token_file
        
    return YouTubeIntegration(creds)

import logging

logger = logging.getLogger(__name__)

def get_channel_id_from_oauth(integration):
    """Get authenticated user's channel ID using OAuth."""
    try:
        if not integration.youtube_oauth:
            logger.warning("OAuth client not initialized")
            return None
            
        request = integration.youtube_oauth.channels().list(
            part="id",
            mine=True
        )
        response = request.execute()
        
        if response.get("items"):
            channel_id = response["items"][0]["id"]
            logger.info(f"Detected channel ID from OAuth: {channel_id}")
            return channel_id
    except Exception as e:
        logger.error(f"Failed to get channel ID from OAuth: {e}")
    return None

@router.get("/status")
async def get_youtube_status():
    """Check YouTube OAuth token validity."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    token_file = os.path.join(project_root, "youtube_token.json")
    
    exists = os.path.exists(token_file)
    valid = False
    
    if exists:
        try:
            integration = get_youtube_integration()
            valid = integration.test_connection()
            if not valid:
                logger.warning("YouTube integration test returned False")
        except Exception as e:
            logger.error(f"YouTube status check error: {e}")
            valid = False
            
    return {
        "token_exists": exists,
        "is_valid": valid,
        "status": "active" if valid else "error"
    }

@router.get("/stats")
async def get_youtube_stats():
    """Fetch high-level channel stats."""
    integration = get_youtube_integration()
    
    # Try env variable first, then OAuth auto-detect
    channel_id = os.getenv("YOUTUBE_CHANNEL_ID")
    
    if not channel_id:
        logger.info("YOUTUBE_CHANNEL_ID not set, attempting OAuth detection...")
        channel_id = get_channel_id_from_oauth(integration)
        
    if not channel_id:
        logger.error("Could not determine channel ID from env or OAuth")
        return {
            "error": "Channel ID not found. Set YOUTUBE_CHANNEL_ID env variable.",
            "subscriber_count": 0,
            "video_count": 0,
            "view_count": 0,
            "channel_name": "Unknown"
        }
    
    logger.info(f"Fetching stats for channel: {channel_id}")
    stats = integration.sync_channel_stats(channel_id)
    return stats

@router.get("/analytics")
async def get_youtube_analytics():
    """Fetch video analytics for the chart."""
    integration = get_youtube_integration()
    
    # Try env variable first, then OAuth auto-detect
    channel_id = os.getenv("YOUTUBE_CHANNEL_ID")
    
    if not channel_id:
        logger.info("YOUTUBE_CHANNEL_ID not set, attempting OAuth detection...")
        channel_id = get_channel_id_from_oauth(integration)
        
    if not channel_id:
        logger.error("Could not determine channel ID from env or OAuth")
        return {
            "error": "Channel ID not found. Set YOUTUBE_CHANNEL_ID env variable.",
            "videos": [],
            "total_videos": 0
        }
    
    logger.info(f"Fetching analytics for channel: {channel_id}")
    analytics = integration.sync_video_analytics(channel_id, max_videos=50)
    
    # Ensure we always return valid structure   
    if "error" in analytics:
        return {
            "error": analytics["error"],
            "videos": [],
            "total_videos": 0
        }
    
    return analytics