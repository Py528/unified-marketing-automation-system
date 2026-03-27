from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text
import os

from core.database import get_db
from api.routes import campaigns, youtube, uploads, publish, cdp, meta
from api.routes.youtube import get_youtube_status
from services.ngrok_service import ngrok_service

app = FastAPI(title="Unified Marketing Automation System API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(youtube.router, prefix="/api/youtube", tags=["youtube"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["uploads"])
app.include_router(publish.router, prefix="/api/publish", tags=["Publishing"])
app.include_router(cdp.router, prefix="/api/cdp", tags=["CDP"])
app.include_router(meta.router, prefix="/api/meta", tags=["meta"])

@app.on_event("startup")
async def startup_event():
    # Start ngrok tunnel in development
    if os.getenv("ENABLE_NGROK", "true").lower() == "true":
        public_url = ngrok_service.start_tunnel(8000)
        if public_url:
            print(f"🚀 Public API URL: {public_url}")

# Serve static files from uploads directory
UPLOAD_DIR = "/Users/pranavshinde/Developer/unified-marketing-automation-system/uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.get("/api/status")
async def get_status(db: Session = Depends(get_db)):
    """Check system health status."""
    health = {
        "database": "error",
        "celery": "active",
        "youtube": False,
        "system": "online"
    }
    
    try:
        # Check DB
        db.execute(text("SELECT 1"))
        health["database"] = "active"
    except Exception as e:
        print(f"HEALTH_CHECK_DB_ERROR: {e}")
        
    try:
        # Check YouTube
        yt_status = await get_youtube_status()
        health["youtube"] = yt_status.get("is_valid", False)
    except Exception as e:
        print(f"HEALTH_CHECK_YT_ERROR: {e}")

    try:
        # Check Meta Status
        meta_status = await meta.get_meta_status()
        health["meta"] = meta_status.get("is_valid", False)
    except Exception as e:
        print(f"HEALTH_CHECK_META_ERROR: {e}")
        
    return health

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
