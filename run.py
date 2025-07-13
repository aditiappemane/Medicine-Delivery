#!/usr/bin/env python3
"""
Startup script for Medicine Delivery API
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get configuration from environment or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"Starting Medicine Delivery API on {host}:{port}")
    print("API Documentation will be available at:")
    print(f"  - Swagger UI: http://{host}:{port}/docs")
    print(f"  - ReDoc: http://{host}:{port}/redoc")
    print(f"  - Health Check: http://{host}:{port}/health")
    print()
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    ) 