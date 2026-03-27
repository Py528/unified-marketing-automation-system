from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import os

from core.database import get_db, ChannelType
from core.config import get_settings
from agents.campaign_manager import CampaignManagerAgent
from services.ngrok_service import ngrok_service
import json

router = APIRouter()
settings = get_settings()

def get_meta_credentials():
    """Load Meta credentials from file or fallback to environment."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    token_file = os.path.join(project_root, "meta_token.json")
    
    creds = {
        "access_token": settings.facebook_access_token,
        "page_id": settings.facebook_page_id,
        "instagram_business_account_id": settings.instagram_business_account_id
    }
    
    if os.path.exists(token_file):
        try:
            with open(token_file, 'r') as f:
                file_creds = json.load(f)
                if file_creds.get("facebook_access_token"):
                    creds["access_token"] = file_creds["facebook_access_token"]
                if file_creds.get("facebook_page_id"):
                    creds["page_id"] = file_creds["facebook_page_id"]
                if file_creds.get("instagram_business_account_id"):
                    creds["instagram_business_account_id"] = file_creds["instagram_business_account_id"]
        except Exception as e:
            print(f"Error loading meta_token.json: {e}")
            
    masked_token = f"{creds['access_token'][:10]}...{creds['access_token'][-10:]}" if creds.get('access_token') else "None"
    print(f"DEBUG: get_meta_credentials returning token starting with: {masked_token}")
    return creds

@router.post("/social")
async def publish_social(payload: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Publish content to Facebook or Instagram.
    Payload: {
        "platform": "facebook" | "instagram",
        "content": str,
        "media_url": str (optional),
        "media_type": "IMAGE" | "VIDEO" | "REELS" (optional)
    }
    """
    platform = payload.get("platform")
    content = payload.get("content")
    media_url = payload.get("media_url")
    media_type = payload.get("media_type", "IMAGE")
    
    if platform not in ["facebook", "instagram"]:
        raise HTTPException(status_code=400, detail="Invalid platform. Use 'facebook' or 'instagram'.")
    
    # Process media URL if it refers to a local file
    processed_media_url = media_url
    if media_url and not media_url.startswith(("http://", "https://")):
        # Assume it's a filename in the uploads directory
        public_base = ngrok_service.public_url
        if not public_base:
            # Fallback for local testing - though external APIs won't reach this
            host = settings.api_host if settings.api_host != "0.0.0.0" else "localhost"
            public_base = f"http://{host}:{settings.api_port}"
            
        processed_media_url = f"{public_base}/uploads/{media_url}"
        print(f"DEBUG: Generated processed_media_url: {processed_media_url}")
    
    # Initialize Agent
    agent = CampaignManagerAgent(db)
    
    # Map platform to ChannelType
    channel = ChannelType.FACEBOOK if platform == "facebook" else ChannelType.INSTAGRAM
    
    # Build campaign config
    config = {
        "media_url": processed_media_url,
        "media_type": media_type
    }
    if platform == "facebook":
        config["message"] = content
    else:
        config["content"] = content
        
    # Create Campaign
    create_result = agent.create_campaign(
        name=f"Social Publish - {platform.capitalize()}",
        channel=channel,
        config=config
    )
    
    if not create_result.get("success"):
        raise HTTPException(status_code=500, detail=create_result.get("error"))
    
    campaign_id = create_result["campaign_id"]
    
    # Prepare Credentials (from file or fallback to settings)
    meta_creds = get_meta_credentials()
    
    credentials = {}
    if platform == "facebook":
        credentials[ChannelType.FACEBOOK] = {
            "access_token": meta_creds["access_token"],
            "page_id": meta_creds["page_id"]
        }
    else:
        credentials[ChannelType.INSTAGRAM] = {
            "access_token": meta_creds["access_token"],
            "instagram_business_account_id": meta_creds["instagram_business_account_id"]
        }
        
    # Execute Campaign
    exec_result = agent.execute_campaign(campaign_id, credentials)
    
    if exec_result.get("success"):
        return {
            "success": True,
            "campaign_id": campaign_id,
            "post_id": exec_result.get("results", {}).get("post_id"),
            "public_media_url": processed_media_url
        }
    else:
        error_msg = exec_result.get("error")
        # Extract deeper error message if available from results
        if exec_result.get("results", {}).get("error"):
            error_msg = exec_result["results"]["error"]
            
        return {
            "success": False,
            "error": error_msg or "Failed to publish. Please check your integration settings.",
            "campaign_id": campaign_id
        }
