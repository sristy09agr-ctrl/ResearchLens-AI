"""
ResearchLens AI - Backward-Compatible Backend Entry Point.
Redirects to the modular app architecture in app.main.
"""

from app.main import app

if __name__ == "__main__":
    import uvicorn
    from app.config import settings
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
