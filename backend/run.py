import sys

import uvicorn

from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    prod = "--prod" in sys.argv
    uvicorn.run(
        "app.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=not prod,
    )
