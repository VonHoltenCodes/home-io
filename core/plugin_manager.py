import os
import importlib
import logging
import inspect
from typing import Dict, List, Any, Optional, Type, Set
import pkgutil
import sys

logger = logging.getLogger("home-io.plugin_manager")

class PluginInterface:
    """Base interface that all plugins must implement"""
    
    # Class properties to be defined by plugins
    plugin_name: str = "base_plugin"
    plugin_version: str = "0.1.0"
    plugin_description: str = "Base plugin interface"
    
    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """Return plugin metadata"""
        return {
            "name": cls.plugin_name,
            "version": cls.plugin_version,
            "description": cls.plugin_description
        }
    
    def initialize(self, config: Dict[str, Any] = None) -> bool:
        """Initialize the plugin with configuration"""
        raise NotImplementedError("Plugin must implement initialize method")
    
    def shutdown(self) -> bool:
        """Clean up resources when shutting down"""
        raise NotImplementedError("Plugin must implement shutdown method")


class PluginManager:
    """Manages loading, initialization, and access to plugins"""
    
    def __init__(self, plugin_dirs: List[str] = None):
        self.plugins: Dict[str, PluginInterface] = {}
        self.plugin_dirs = plugin_dirs or ["plugins"]
        self.loaded_plugin_classes: Dict[str, Type[PluginInterface]] = {}
        
    def discover_plugins(self) -> Set[str]:
        """Find all available plugins in the plugin directories"""
        discovered_plugins = set()
        
        for plugin_dir in self.plugin_dirs:
            if not os.path.exists(plugin_dir):
                logger.warning(f"Plugin directory {plugin_dir} does not exist")
                continue
                
            # Add plugin directory to path temporarily
            sys.path.insert(0, os.path.abspath(plugin_dir))
            
            # Walk through all modules in the directory
            for _, name, is_pkg in pkgutil.iter_modules([plugin_dir]):
                if not is_pkg:  # Skip non-package modules
                    continue
                
                try:
                    discovered_plugins.add(name)
                except Exception as e:
                    logger.error(f"Error discovering plugin {name}: {str(e)}")
            
            # Remove from path
            sys.path.pop(0)
                
        return discovered_plugins
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin by name"""
        if plugin_name in self.loaded_plugin_classes:
            logger.info(f"Plugin {plugin_name} already loaded")
            return True
            
        # Find the plugin module
        plugin_found = False
        
        for plugin_dir in self.plugin_dirs:
            plugin_path = os.path.join(plugin_dir, plugin_name)
            
            if not os.path.exists(plugin_path):
                continue
                
            sys.path.insert(0, os.path.abspath(os.path.dirname(plugin_path)))
            
            try:
                # Import the module
                module = importlib.import_module(f"{plugin_name}.plugin")
                
                # Find plugin classes (subclasses of PluginInterface)
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, PluginInterface) and 
                        obj != PluginInterface):
                        
                        self.loaded_plugin_classes[plugin_name] = obj
                        logger.info(f"Loaded plugin class: {obj.__name__}")
                        plugin_found = True
                        break
                        
            except ImportError as e:
                logger.error(f"Failed to import plugin {plugin_name}: {str(e)}")
            except Exception as e:
                logger.error(f"Error loading plugin {plugin_name}: {str(e)}")
            finally:
                sys.path.pop(0)
                
            if plugin_found:
                break
                
        return plugin_found
    
    def load_all_plugins(self) -> Dict[str, bool]:
        """Discover and load all available plugins"""
        results = {}
        
        for plugin_name in self.discover_plugins():
            results[plugin_name] = self.load_plugin(plugin_name)
            
        return results
    
    def initialize_plugin(self, plugin_name: str, config: Dict[str, Any] = None) -> bool:
        """Initialize a loaded plugin with configuration"""
        if plugin_name not in self.loaded_plugin_classes:
            logger.error(f"Cannot initialize plugin {plugin_name} - not loaded")
            return False
            
        if plugin_name in self.plugins:
            logger.info(f"Plugin {plugin_name} already initialized")
            return True
            
        try:
            # Create plugin instance
            plugin_class = self.loaded_plugin_classes[plugin_name]
            plugin_instance = plugin_class()
            
            # Initialize plugin
            config = config or {}
            success = plugin_instance.initialize(config)
            
            if success:
                self.plugins[plugin_name] = plugin_instance
                logger.info(f"Initialized plugin: {plugin_name}")
                return True
            else:
                logger.error(f"Plugin {plugin_name} initialization returned failure")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing plugin {plugin_name}: {str(e)}")
            return False
    
    def initialize_all_plugins(self, configs: Dict[str, Dict[str, Any]] = None) -> Dict[str, bool]:
        """Initialize all loaded plugins"""
        results = {}
        configs = configs or {}
        
        for plugin_name in self.loaded_plugin_classes:
            plugin_config = configs.get(plugin_name, {})
            results[plugin_name] = self.initialize_plugin(plugin_name, plugin_config)
            
        return results
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """Get an initialized plugin instance by name"""
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, PluginInterface]:
        """Get all initialized plugin instances"""
        return self.plugins
    
    def shutdown_plugin(self, plugin_name: str) -> bool:
        """Shutdown a specific plugin"""
        if plugin_name not in self.plugins:
            logger.warning(f"Cannot shutdown plugin {plugin_name} - not initialized")
            return False
            
        try:
            success = self.plugins[plugin_name].shutdown()
            
            if success:
                del self.plugins[plugin_name]
                logger.info(f"Shutdown plugin: {plugin_name}")
                return True
            else:
                logger.error(f"Plugin {plugin_name} shutdown returned failure")
                return False
                
        except Exception as e:
            logger.error(f"Error shutting down plugin {plugin_name}: {str(e)}")
            return False
    
    def shutdown_all_plugins(self) -> Dict[str, bool]:
        """Shutdown all initialized plugins"""
        results = {}
        
        # Create a list of plugin names to avoid modifying dictionary during iteration
        plugin_names = list(self.plugins.keys())
        
        for plugin_name in plugin_names:
            results[plugin_name] = self.shutdown_plugin(plugin_name)
            
        return results