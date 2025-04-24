import json
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("home-io.config_manager")

class ConfigManager:
    """Manages configuration for the Home-IO system"""
    
    def __init__(self, config_path: str = None):
        """Initialize configuration manager"""
        self.config_path = config_path or "config/config.json"
        self.config = {}
        self.loaded = False
        
    def load(self) -> bool:
        """Load configuration from file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Load config if file exists
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    self.config = json.load(f)
                    
                logger.info(f"Configuration loaded from {self.config_path}")
            else:
                # Create default configuration
                self.config = self._get_default_config()
                self.save()  # Save default config
                logger.info(f"Default configuration created at {self.config_path}")
                
            self.loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            
            # If config fails to load, use default
            self.config = self._get_default_config()
            self.loaded = True
            
            return False
    
    def save(self) -> bool:
        """Save configuration to file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Save config
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
                
            logger.info(f"Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
            return False
    
    def get(self, key: str = None, default: Any = None) -> Any:
        """
        Get configuration value
        
        If key is None, returns the entire config
        If key is a dot-separated path (e.g., "server.port"), navigates the config
        """
        if not self.loaded:
            self.load()
            
        if key is None:
            return self.config
            
        # Handle dot notation for nested access
        if "." in key:
            parts = key.split(".")
            current = self.config
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return default
                    
            return current
            
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any, save_file: bool = True) -> bool:
        """
        Set configuration value
        
        If key is a dot-separated path (e.g., "server.port"), navigates and updates the config
        """
        if not self.loaded:
            self.load()
            
        # Handle dot notation for nested access
        if "." in key:
            parts = key.split(".")
            current = self.config
            
            # Navigate to the parent of the target key
            for part in parts[:-1]:
                if part not in current or not isinstance(current[part], dict):
                    current[part] = {}
                current = current[part]
                
            # Set the value at the target key
            current[parts[-1]] = value
        else:
            self.config[key] = value
            
        # Save to file if requested
        if save_file:
            return self.save()
            
        return True
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "system": {
                "name": "Home-IO",
                "version": "0.1.0",
                "log_level": "INFO"
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "debug": True,
                "cors_origins": ["*"]
            },
            "database": {
                "path": "data/home_io.db",
                "backup_path": "data/backups",
                "auto_backup": True,
                "backup_interval_hours": 24
            },
            "plugins": {
                "enabled": ["zwave", "zigbee", "sensors"],
                "discovery": True,
                "path": "plugins",
                "config": {
                    "zwave": {
                        "controller_path": "/dev/ttyUSB0",
                        "mock_network": True
                    },
                    "zigbee": {
                        "controller_path": "/dev/ttyUSB1",
                        "mock_network": True
                    },
                    "sensors": {
                        "scan_interval": 30
                    }
                }
            },
            "ui": {
                "theme": "dark",
                "title": "Home-IO Hub",
                "refresh_interval": 5,
                "tiles_per_row": 4,
                "default_view": "dashboard"
            },
            "security": {
                "enable_auth": False,
                "pin_required": False,
                "pin": "1234",
                "session_timeout_minutes": 30,
                "allowed_ips": ["127.0.0.1", "192.168.0.0/24"]
            },
            "notifications": {
                "enabled": True,
                "retention_days": 7,
                "max_count": 100
            }
        }