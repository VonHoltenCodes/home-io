from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import os
import logging
import asyncio
from typing import Dict, Any

# Import core components
from core.config_manager import ConfigManager
from core.db_manager import DatabaseManager
from core.plugin_manager import PluginManager

# Import API routes (will add more as we develop)
from api.routes.devices import router as devices_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("home-io")

# Initialize core components
config = ConfigManager()
config.load()

db = DatabaseManager(config.get("database.path"))
db.initialize()

plugin_manager = PluginManager(
    plugin_dirs=[config.get("plugins.path", "plugins")]
)

# Create FastAPI app
app = FastAPI(
    title=config.get("system.name", "Home-IO"),
    description="Custom home automation hub with modular IoT integration",
    version=config.get("system.version", "0.1.0"),
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get("server.cors_origins", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API routes
app.include_router(devices_router, prefix="/api/devices", tags=["devices"])

# Health check endpoint
@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint to verify API is running"""
    return {
        "status": "healthy",
        "version": config.get("system.version", "0.1.0"),
        "environment": os.environ.get("ENV", "development")
    }

# System info endpoint
@app.get("/api/system")
async def system_info() -> Dict[str, Any]:
    """System information and status"""
    return {
        "name": config.get("system.name", "Home-IO"),
        "version": config.get("system.version", "0.1.0"),
        "plugins": {
            "loaded": list(plugin_manager.loaded_plugin_classes.keys()),
            "active": list(plugin_manager.plugins.keys())
        },
        "uptime": "00:00:00",  # Will implement actual uptime tracking
        "ui_config": config.get("ui", {})
    }

# Base route
@app.get("/")
async def root():
    return {"message": f"Welcome to {config.get('system.name', 'Home-IO')} API. Access /docs for API documentation."}

# Error handlers
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )

# Events
@app.on_event("startup")
async def startup_event():
    """Runs when the API server starts"""
    logger.info("Starting Home-IO Hub")
    
    # Load plugins
    plugin_results = plugin_manager.load_all_plugins()
    logger.info(f"Loaded plugins: {plugin_results}")
    
    # Initialize plugins
    plugin_configs = config.get("plugins.config", {})
    init_results = plugin_manager.initialize_all_plugins(plugin_configs)
    logger.info(f"Initialized plugins: {init_results}")
    
    logger.info("Home-IO Hub startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Runs when the API server shuts down"""
    logger.info("Shutting down Home-IO Hub")
    
    # Shutdown plugins
    plugin_manager.shutdown_all_plugins()
    
    # Close database connection
    db.shutdown()
    
    logger.info("Home-IO Hub shutdown complete")

# For development, mount React app static files if available
if os.path.exists("./home-io-test/build"):
    app.mount("/app", StaticFiles(directory="./home-io-test/build", html=True), name="app")

# Main entry point
if __name__ == "__main__":
    # Start app with uvicorn for development
    uvicorn.run(
        "main:app", 
        host=config.get("server.host", "0.0.0.0"), 
        port=config.get("server.port", 8000),
        reload=config.get("server.debug", True)
    )