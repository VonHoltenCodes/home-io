import sqlite3
import json
import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger("home-io.db_manager")

class DatabaseManager:
    """Manages database operations for the Home-IO system"""
    
    def __init__(self, db_path: str = None):
        """Initialize database manager"""
        self.db_path = db_path or "data/home_io.db"
        self.conn = None
        self.initialized = False
        
    def initialize(self) -> bool:
        """Initialize the database and create tables if they don't exist"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Connect to database
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            
            # Create tables if they don't exist
            self._create_tables()
            
            self.initialized = True
            logger.info(f"Database initialized at {self.db_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            return False
            
    def shutdown(self) -> bool:
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            
        self.initialized = False
        logger.info("Database connection closed")
        return True
            
    def _create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Devices table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            protocol TEXT NOT NULL,
            location TEXT,
            manufacturer TEXT,
            model TEXT,
            firmware_version TEXT,
            state TEXT,
            capabilities TEXT,
            config TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')
        
        # Sensor readings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            type TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (device_id) REFERENCES devices (id)
        )
        ''')
        
        # Device events table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            data TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (device_id) REFERENCES devices (id)
        )
        ''')
        
        # Automation rules table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS automation_rules (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            trigger TEXT NOT NULL,
            conditions TEXT,
            actions TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')
        
        # User settings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')
        
        # Commit changes
        self.conn.commit()
        logger.info("Database tables created/verified")
    
    # Device methods
    
    def get_devices(self, type_filter: str = None, location: str = None) -> List[Dict[str, Any]]:
        """Get list of devices with optional filtering"""
        if not self.initialized:
            logger.error("Database not initialized")
            return []
            
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM devices"
        params = []
        
        if type_filter or location:
            query += " WHERE "
            conditions = []
            
            if type_filter:
                conditions.append("type = ?")
                params.append(type_filter)
                
            if location:
                conditions.append("location = ?")
                params.append(location)
                
            query += " AND ".join(conditions)
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        devices = []
        for row in rows:
            device = dict(row)
            
            # Parse JSON fields
            device["state"] = json.loads(device["state"])
            device["capabilities"] = json.loads(device["capabilities"])
            device["config"] = json.loads(device["config"])
            
            devices.append(device)
            
        return devices
    
    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific device by ID"""
        if not self.initialized:
            logger.error("Database not initialized")
            return None
            
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
            
        device = dict(row)
        
        # Parse JSON fields
        device["state"] = json.loads(device["state"])
        device["capabilities"] = json.loads(device["capabilities"])
        device["config"] = json.loads(device["config"])
        
        return device
    
    def add_device(self, device: Dict[str, Any]) -> bool:
        """Add a new device to the database"""
        if not self.initialized:
            logger.error("Database not initialized")
            return False
            
        cursor = self.conn.cursor()
        
        # Convert JSON fields to strings
        device_data = device.copy()
        device_data["state"] = json.dumps(device.get("state", {}))
        device_data["capabilities"] = json.dumps(device.get("capabilities", []))
        device_data["config"] = json.dumps(device.get("config", {}))
        
        # Set timestamps
        now = datetime.now().isoformat()
        device_data["created_at"] = now
        device_data["updated_at"] = now
        
        try:
            cursor.execute('''
            INSERT INTO devices (
                id, name, type, protocol, location, manufacturer, model, 
                firmware_version, state, capabilities, config, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                device_data["id"],
                device_data["name"],
                device_data["type"],
                device_data["protocol"],
                device_data.get("location"),
                device_data.get("manufacturer"),
                device_data.get("model"),
                device_data.get("firmware_version"),
                device_data["state"],
                device_data["capabilities"],
                device_data["config"],
                device_data["created_at"],
                device_data["updated_at"]
            ))
            
            self.conn.commit()
            logger.info(f"Added device: {device_data['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add device: {str(e)}")
            return False
    
    def update_device(self, device_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing device"""
        if not self.initialized:
            logger.error("Database not initialized")
            return False
            
        # Get existing device
        existing_device = self.get_device(device_id)
        if not existing_device:
            logger.error(f"Device not found: {device_id}")
            return False
            
        # Prepare updates
        update_data = {}
        update_fields = []
        update_values = []
        
        for key, value in updates.items():
            if key in ["id", "created_at"]:
                continue  # Don't update these fields
                
            if key in ["state", "capabilities", "config"]:
                # Merge with existing data for JSON fields
                existing_value = existing_device.get(key, {} if key == "state" or key == "config" else [])
                
                if isinstance(existing_value, dict) and isinstance(value, dict):
                    # For dictionaries, update nested values
                    existing_value.update(value)
                    update_value = json.dumps(existing_value)
                elif isinstance(existing_value, list) and isinstance(value, list):
                    # For lists, replace entirely
                    update_value = json.dumps(value)
                else:
                    # Direct replacement
                    update_value = json.dumps(value)
            else:
                # Regular field
                update_value = value
                
            update_fields.append(f"{key} = ?")
            update_values.append(update_value)
        
        # Add updated_at timestamp
        update_fields.append("updated_at = ?")
        update_values.append(datetime.now().isoformat())
        
        # Add device_id for WHERE clause
        update_values.append(device_id)
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"UPDATE devices SET {', '.join(update_fields)} WHERE id = ?",
                tuple(update_values)
            )
            
            self.conn.commit()
            logger.info(f"Updated device: {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update device: {str(e)}")
            return False
    
    def delete_device(self, device_id: str) -> bool:
        """Delete a device from the database"""
        if not self.initialized:
            logger.error("Database not initialized")
            return False
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM devices WHERE id = ?", (device_id,))
            
            if cursor.rowcount == 0:
                logger.warning(f"Device not found for deletion: {device_id}")
                return False
                
            self.conn.commit()
            logger.info(f"Deleted device: {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete device: {str(e)}")
            return False
    
    # Sensor reading methods
    
    def add_sensor_reading(self, reading: Dict[str, Any]) -> bool:
        """Add a sensor reading to the database"""
        if not self.initialized:
            logger.error("Database not initialized")
            return False
            
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO sensor_readings (device_id, type, value, unit, timestamp)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                reading["device_id"],
                reading["type"],
                reading["value"],
                reading["unit"],
                reading.get("timestamp", datetime.now().isoformat())
            ))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to add sensor reading: {str(e)}")
            return False
    
    def get_sensor_readings(
        self, 
        device_id: str, 
        reading_type: str = None,
        start_time: str = None,
        end_time: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get sensor readings for a device with optional filtering"""
        if not self.initialized:
            logger.error("Database not initialized")
            return []
            
        query = "SELECT * FROM sensor_readings WHERE device_id = ?"
        params = [device_id]
        
        if reading_type:
            query += " AND type = ?"
            params.append(reading_type)
            
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
            
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
            
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.conn.cursor()
        cursor.execute(query, tuple(params))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # Event methods
    
    def add_event(self, event: Dict[str, Any]) -> bool:
        """Add a device event to the database"""
        if not self.initialized:
            logger.error("Database not initialized")
            return False
            
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO device_events (device_id, event_type, data, timestamp)
            VALUES (?, ?, ?, ?)
            ''', (
                event["device_id"],
                event["event_type"],
                json.dumps(event.get("data", {})),
                event.get("timestamp", datetime.now().isoformat())
            ))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to add event: {str(e)}")
            return False
    
    def get_events(
        self,
        device_id: str = None,
        event_type: str = None,
        start_time: str = None,
        end_time: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get events with optional filtering"""
        if not self.initialized:
            logger.error("Database not initialized")
            return []
            
        query = "SELECT * FROM device_events"
        params = []
        conditions = []
        
        if device_id:
            conditions.append("device_id = ?")
            params.append(device_id)
            
        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type)
            
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time)
            
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.conn.cursor()
        cursor.execute(query, tuple(params))
        
        events = []
        for row in cursor.fetchall():
            event = dict(row)
            event["data"] = json.loads(event["data"])
            events.append(event)
            
        return events
    
    # Automation rule methods
    
    def get_rules(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """Get all automation rules"""
        if not self.initialized:
            logger.error("Database not initialized")
            return []
            
        query = "SELECT * FROM automation_rules"
        params = []
        
        if enabled_only:
            query += " WHERE enabled = 1"
            
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        rules = []
        for row in cursor.fetchall():
            rule = dict(row)
            
            # Parse JSON fields
            rule["trigger"] = json.loads(rule["trigger"])
            rule["conditions"] = json.loads(rule["conditions"]) if rule["conditions"] else None
            rule["actions"] = json.loads(rule["actions"])
            
            # Convert enabled to boolean
            rule["enabled"] = bool(rule["enabled"])
            
            rules.append(rule)
            
        return rules
    
    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific automation rule"""
        if not self.initialized:
            logger.error("Database not initialized")
            return None
            
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM automation_rules WHERE id = ?", (rule_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
            
        rule = dict(row)
        
        # Parse JSON fields
        rule["trigger"] = json.loads(rule["trigger"])
        rule["conditions"] = json.loads(rule["conditions"]) if rule["conditions"] else None
        rule["actions"] = json.loads(rule["actions"])
        
        # Convert enabled to boolean
        rule["enabled"] = bool(rule["enabled"])
        
        return rule
    
    def add_rule(self, rule: Dict[str, Any]) -> bool:
        """Add a new automation rule"""
        if not self.initialized:
            logger.error("Database not initialized")
            return False
            
        cursor = self.conn.cursor()
        
        # Set timestamps
        now = datetime.now().isoformat()
        
        try:
            cursor.execute('''
            INSERT INTO automation_rules (
                id, name, description, trigger, conditions, actions, 
                enabled, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                rule["id"],
                rule["name"],
                rule.get("description"),
                json.dumps(rule["trigger"]),
                json.dumps(rule.get("conditions")) if rule.get("conditions") else None,
                json.dumps(rule["actions"]),
                1 if rule.get("enabled", True) else 0,
                now,
                now
            ))
            
            self.conn.commit()
            logger.info(f"Added automation rule: {rule['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add automation rule: {str(e)}")
            return False
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing automation rule"""
        if not self.initialized:
            logger.error("Database not initialized")
            return False
            
        # Get existing rule
        existing_rule = self.get_rule(rule_id)
        if not existing_rule:
            logger.error(f"Automation rule not found: {rule_id}")
            return False
            
        # Prepare updates
        update_data = {}
        update_fields = []
        update_values = []
        
        for key, value in updates.items():
            if key in ["id", "created_at"]:
                continue  # Don't update these fields
                
            if key in ["trigger", "conditions", "actions"]:
                # JSON fields
                update_value = json.dumps(value)
                if key == "conditions" and value is None:
                    update_value = None
            elif key == "enabled":
                # Boolean field
                update_value = 1 if value else 0
            else:
                # Regular field
                update_value = value
                
            update_fields.append(f"{key} = ?")
            update_values.append(update_value)
        
        # Add updated_at timestamp
        update_fields.append("updated_at = ?")
        update_values.append(datetime.now().isoformat())
        
        # Add rule_id for WHERE clause
        update_values.append(rule_id)
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"UPDATE automation_rules SET {', '.join(update_fields)} WHERE id = ?",
                tuple(update_values)
            )
            
            self.conn.commit()
            logger.info(f"Updated automation rule: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update automation rule: {str(e)}")
            return False
    
    def delete_rule(self, rule_id: str) -> bool:
        """Delete an automation rule"""
        if not self.initialized:
            logger.error("Database not initialized")
            return False
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM automation_rules WHERE id = ?", (rule_id,))
            
            if cursor.rowcount == 0:
                logger.warning(f"Automation rule not found for deletion: {rule_id}")
                return False
                
            self.conn.commit()
            logger.info(f"Deleted automation rule: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete automation rule: {str(e)}")
            return False
    
    # Settings methods
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting value by key"""
        if not self.initialized:
            logger.error("Database not initialized")
            return None
            
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        
        return row["value"] if row else None
    
    def get_settings(self, prefix: str = None) -> Dict[str, str]:
        """Get multiple settings with optional prefix filter"""
        if not self.initialized:
            logger.error("Database not initialized")
            return {}
            
        cursor = self.conn.cursor()
        
        if prefix:
            cursor.execute("SELECT key, value FROM settings WHERE key LIKE ?", (f"{prefix}%",))
        else:
            cursor.execute("SELECT key, value FROM settings")
            
        return {row["key"]: row["value"] for row in cursor.fetchall()}
    
    def set_setting(self, key: str, value: str) -> bool:
        """Set a setting value"""
        if not self.initialized:
            logger.error("Database not initialized")
            return False
            
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()
            
            # Use INSERT OR REPLACE to handle both new and existing settings
            cursor.execute(
                "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
                (key, value, now)
            )
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to set setting: {str(e)}")
            return False
    
    def delete_setting(self, key: str) -> bool:
        """Delete a setting"""
        if not self.initialized:
            logger.error("Database not initialized")
            return False
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM settings WHERE key = ?", (key,))
            
            if cursor.rowcount == 0:
                logger.warning(f"Setting not found for deletion: {key}")
                return False
                
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete setting: {str(e)}")
            return False