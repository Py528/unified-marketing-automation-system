"""Facebook Graph API integration."""

import logging
import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime

from api_integrations.base import BaseIntegration

logger = logging.getLogger(__name__)


class FacebookIntegration(BaseIntegration):
    """Integration with Facebook Graph API."""
    
    BASE_URL = "https://graph.facebook.com/v18.0"
    
    def __init__(self, credentials: Dict[str, Any]):
        """
        Initialize Facebook integration.
        
        Args:
            credentials: Should contain 'access_token' and optionally 'page_id'
        """
        super().__init__(credentials, rate_limit_calls=200, rate_limit_period=3600)  # 200/hour default
        self.access_token = credentials.get("access_token")
        self.page_id = credentials.get("page_id")
        
        if not self.access_token:
            raise ValueError("Facebook access token is required")
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to Facebook Graph API."""
        if not params:
            params = {}
        params["access_token"] = self.access_token
        
        try:
            self._handle_rate_limit()
            response = requests.get(f"{self.BASE_URL}/{endpoint}", params=params, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Facebook API request failed: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test Facebook API connection."""
        try:
            self._make_request("me")
            return True
        except Exception as e:
            logger.error(f"Facebook connection test failed: {e}")
            return False
    
    def sync_page_insights(self, page_id: Optional[str] = None, metrics: Optional[list] = None) -> Dict[str, Any]:
        """
        Sync Facebook page insights.
        
        Args:
            page_id: Facebook page ID (uses self.page_id if not provided)
            metrics: List of metrics to fetch (default: page_fans, page_impressions, page_engaged_users)
        """
        target_page_id = page_id or self.page_id
        if not target_page_id:
            return {"error": "Facebook Page ID is required"}
        
        if not metrics:
            metrics = ["page_fans", "page_impressions", "page_engaged_users"]
        
        try:
            # Get insights for last 30 days
            params = {
                "metric": ",".join(metrics),
                "period": "day",
                "since": int((datetime.utcnow().timestamp() - 30 * 86400)),
                "until": int(datetime.utcnow().timestamp())
            }
            
            response = self._make_request(
                f"{target_page_id}/insights",
                params=params
            )
            
            insights_data = {}
            for insight in response.get("data", []):
                metric_name = insight.get("name")
                values = insight.get("values", [])
                if values:
                    # Get the most recent value
                    insights_data[metric_name] = {
                        "current": values[-1].get("value", 0),
                        "values": [v.get("value", 0) for v in values],
                        "end_time": values[-1].get("end_time")
                    }
            
            return {
                "insights": insights_data,
                "synced_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return self._handle_error(e, "sync_page_insights")
    
    def sync_page_posts(self, page_id: Optional[str] = None, limit: int = 25) -> Dict[str, Any]:
        """
        Sync Facebook page posts.
        
        Args:
            page_id: Facebook page ID
            limit: Maximum number of posts to fetch
        """
        target_page_id = page_id or self.page_id
        if not target_page_id:
            return {"error": "Facebook Page ID is required"}
        
        try:
            params = {
                "fields": "id,message,created_time,likes.summary(true),comments.summary(true),shares",
                "limit": min(limit, 25)
            }
            
            response = self._make_request(
                f"{target_page_id}/posts",
                params=params
            )
            
            posts = []
            for item in response.get("data", []):
                likes_data = item.get("likes", {}).get("summary", {})
                comments_data = item.get("comments", {}).get("summary", {})
                shares_data = item.get("shares", {})
                
                posts.append({
                    "post_id": item.get("id"),
                    "message": item.get("message", ""),
                    "created_time": item.get("created_time"),
                    "likes": likes_data.get("total_count", 0),
                    "comments": comments_data.get("total_count", 0),
                    "shares": shares_data.get("count", 0)
                })
            
            return {
                "posts": posts,
                "total_posts": len(posts),
                "synced_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return self._handle_error(e, "sync_page_posts")
    
    def sync_ad_performance(self, ad_account_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Sync Facebook ad performance data.
        
        Args:
            ad_account_id: Facebook ad account ID
        
        Returns:
            Dictionary with ad performance data
        """
        if not ad_account_id:
            return {"error": "Ad account ID is required", "note": "Ad performance sync requires ad account access"}
        
        try:
            params = {
                "fields": "id,name,status,insights{impressions,clicks,spend,reach,cpc,cpp,cpm}",
                "limit": 25
            }
            
            response = self._make_request(
                f"act_{ad_account_id}/ads",
                params=params
            )
            
            ads = []
            for item in response.get("data", []):
                insights = item.get("insights", {}).get("data", [])
                if insights:
                    insight = insights[0]
                    ads.append({
                        "ad_id": item.get("id"),
                        "name": item.get("name"),
                        "status": item.get("status"),
                        "impressions": insight.get("impressions", 0),
                        "clicks": insight.get("clicks", 0),
                        "spend": insight.get("spend", 0),
                        "reach": insight.get("reach", 0),
                        "cpc": insight.get("cpc", 0),
                        "cpp": insight.get("cpp", 0),
                        "cpm": insight.get("cpm", 0)
                    })
            
            return {
                "ads": ads,
                "total_ads": len(ads),
                "synced_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return self._handle_error(e, "sync_ad_performance")
    
    def publish_post(self, message: str) -> str:
        """Publish a simple text post to the Facebook page."""
        if not self.page_id:
            raise ValueError("Facebook Page ID is required for publishing")
            
        endpoint = f"{self.page_id}/feed"
        params = {
            "message": message,
            "access_token": self.access_token
        }
        
        try:
            response = requests.post(f"{self.BASE_URL}/{endpoint}", params=params, timeout=90)
            if response.status_code != 200:
                print(f"Facebook API Error Body: {response.text}")
            response.raise_for_status()
            return response.json().get("id")
        except requests.exceptions.HTTPError as e:
            error_detail = response.text
            try:
                error_json = response.json()
                error_detail = error_json.get("error", {}).get("message", response.text)
            except:
                pass
            print(f"Failed to publish Facebook post: {error_detail}")
            raise Exception(f"Facebook API Error: {error_detail}")
        except Exception as e:
            print(f"Failed to publish Facebook post: {e}")
            raise

    def publish_photo(self, photo_source: str, message: str = "") -> str:
        """Publish a photo to the Facebook page. photo_source can be a URL or local path."""
        if not self.page_id:
            raise ValueError("Facebook Page ID is required for publishing")
            
        endpoint = f"{self.page_id}/photos"
        is_local = os.path.exists(photo_source)
        
        params = {
            "caption": message,
            "access_token": self.access_token
        }
        
        try:
            if is_local:
                with open(photo_source, 'rb') as f:
                    files = {'source': f}
                    response = requests.post(f"{self.BASE_URL}/{endpoint}", params=params, files=files, timeout=90)
            else:
                params["url"] = photo_source
                response = requests.post(f"{self.BASE_URL}/{endpoint}", params=params, timeout=90)
                
            if response.status_code != 200:
                print(f"Facebook API Error Body: {response.text}")
            response.raise_for_status()
            return response.json().get("post_id") or response.json().get("id")
        except requests.exceptions.HTTPError as e:
            error_detail = response.text
            try:
                error_json = response.json()
                error_detail = error_json.get("error", {}).get("message", response.text)
            except:
                pass
            print(f"Failed to publish Facebook photo: {error_detail}")
            raise Exception(f"Facebook API Error: {error_detail}")
        except Exception as e:
            print(f"Failed to publish Facebook photo: {e}")
            raise

    def publish_video(self, video_source: str, description: str = "") -> str:
        """Publish a video to the Facebook page. video_source can be a URL or local path."""
        if not self.page_id:
            raise ValueError("Facebook Page ID is required for publishing")
            
        endpoint = f"{self.page_id}/videos"
        is_local = os.path.exists(video_source)
        
        params = {
            "description": description,
            "access_token": self.access_token
        }
        
        try:
            if is_local:
                with open(video_source, 'rb') as f:
                    files = {'source': f}
                    response = requests.post(f"{self.BASE_URL}/{endpoint}", params=params, files=files, timeout=300) # Increased for direct upload
            else:
                params["file_url"] = video_source
                response = requests.post(f"{self.BASE_URL}/{endpoint}", params=params, timeout=120)
                
            if response.status_code != 200:
                print(f"Facebook API Error Body: {response.text}")
            response.raise_for_status()
            return response.json().get("id")
        except requests.exceptions.HTTPError as e:
            error_detail = response.text
            try:
                error_json = response.json()
                error_detail = error_json.get("error", {}).get("message", response.text)
            except:
                pass
            print(f"Failed to publish Facebook video: {error_detail}")
            raise Exception(f"Facebook API Error: {error_detail}")
        except Exception as e:
            print(f"Failed to publish Facebook video: {e}")
            raise

    def sync_data(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Sync all Facebook data.
        
        Args:
            since: Only sync data since this datetime
        
        Returns:
            Dictionary with all synced data
        """
        result = {
            "channel": "facebook",
            "page_insights": {},
            "page_posts": {},
            "ad_performance": {},
            "success": True,
            "errors": [],
            "synced_at": datetime.utcnow().isoformat()
        }
        
        # Sync page insights
        try:
            insights = self.sync_page_insights()
            if "error" in insights:
                result["success"] = False
                result["errors"].append(insights["error"])
            else:
                result["page_insights"] = insights
        except Exception as e:
            result["success"] = False
            result["errors"].append(str(e))
        
        # Sync page posts
        try:
            posts = self.sync_page_posts()
            if "error" in posts:
                result["success"] = False
                result["errors"].append(posts["error"])
            else:
                result["page_posts"] = posts
        except Exception as e:
            result["success"] = False
            result["errors"].append(str(e))
        
        # Sync ad performance (if ad account ID is available)
        ad_account_id = self.credentials.get("ad_account_id")
        if ad_account_id:
            try:
                ads = self.sync_ad_performance(ad_account_id)
                if "error" not in ads:
                    result["ad_performance"] = ads
            except Exception as e:
                result["errors"].append(f"Ad sync error: {str(e)}")
        
        return result

