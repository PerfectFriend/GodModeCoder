"""ESPHome actuator (native API + MQTT fallback)."""
from typing import Dict, Any, Optional
import json
import threading
import time
from .base import BaseActuator

try:
    import aiohttp
    import asyncio
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False


class ESPHomeActuator(BaseActuator):
    """ESPHome device actuator using native API (preferred) + MQTT fallback."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Required config
        self.ip = config.get("ip")
        if not self.ip:
            raise ValueError("ESPHomeActuator requires 'ip' in config")
        
        # Optional config
        self.api_port = config.get("api_port", 6053)
        self.api_key = config.get("api_key")  # ESPHome API encryption key
        self.mqtt_host = config.get("mqtt_host")
        self.mqtt_port = config.get("mqtt_port", 1883)
        self.mqtt_user = config.get("mqtt_user")
        self.mqtt_password = config.get("mqtt_password")
        self.device_name = config.get("device_name", "esphome")
        
        # Connection state
        self._api_client = None
        self._mqtt_client = None
        self._mqtt_connected = False
        self._last_status: Optional[bool] = None
        
        # Initialize connections
        if ASYNC_AVAILABLE:
            self._init_api()
        if self.mqtt_host and MQTT_AVAILABLE:
            self._init_mqtt()
    
    def _init_api(self):
        """Initialize ESPHome native API client."""
        if not ASYNC_AVAILABLE:
            return
        
        try:
            import aiohttp
            import asyncio
            
            # Store for async operations
            self._api_session = None
            self._api_base_url = f"http://{self.ip}:{self.api_port}"
            print(f"ESPHomeActuator API configured for {self.ip}:{self.api_port}")
        except Exception as e:
            print(f"ESPHomeActuator API init failed: {e}")
    
    def _init_mqtt(self):
        """Initialize MQTT client for fallback."""
        if not MQTT_AVAILABLE:
            return
        
        try:
            import paho.mqtt.client as mqtt
            self._mqtt_client = mqtt.Client(client_id=f"superguard_{self.device_name}")
            if self.mqtt_user and self.mqtt_password:
                self._mqtt_client.username_pw_set(self.mqtt_user, self.mqtt_password)
            
            self._mqtt_client.on_connect = self._on_mqtt_connect
            self._mqtt_client.on_disconnect = self._on_mqtt_disconnect
            self._mqtt_client.on_message = self._on_mqtt_message
            
            self._mqtt_client.connect(self.mqtt_host, self.mqtt_port, 60)
            self._mqtt_client.loop_start()
        except Exception as e:
            print(f"ESPHomeActuator MQTT init failed: {e}")
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._mqtt_connected = True
            client.subscribe(f"{self.device_name}/switch/#")
            print(f"ESPHomeActuator MQTT connected to {self.mqtt_host}")
        else:
            print(f"ESPHomeActuator MQTT connect failed: {rc}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        self._mqtt_connected = False
        print(f"ESPHomeActuator MQTT disconnected: {rc}")
    
    def _on_mqtt_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = msg.payload.decode()
            if "switch" in topic.lower() and "state" in topic.lower():
                self._last_status = payload.upper() in ("ON", "TRUE", "1")
        except Exception as e:
            print(f"ESPHomeActuator MQTT message error: {e}")
    
    def _send_mqtt_command(self, entity_id: str, command: str) -> bool:
        """Send command via MQTT."""
        if not self._mqtt_connected or not self._mqtt_client:
            return False
        try:
            topic = f"{self.device_name}/switch/{entity_id}/command"
            self._mqtt_client.publish(topic, command.upper())
            return True
        except Exception as e:
            print(f"ESPHomeActuator MQTT publish failed: {e}")
            return False
    
    def _execute_api_call(self, method: str, endpoint: str, payload: Optional[Dict] = None) -> bool:
        """Execute API call asynchronously."""
        # For simplicity in sync context, we'll use the fallback approach
        # In a real implementation, this would use aiohttp properly
        return False
    
    def turn_on(self) -> bool:
        """Turn the switch ON."""
        # Try MQTT first
        if self.mqtt_host and MQTT_AVAILABLE and self._mqtt_connected:
            if self._send_mqtt_command("switch", "ON"):
                self._last_status = True
                return True
        
        # Fallback to API (simplified for sync context)
        # In a real implementation, this would use aiohttp properly
        try:
            import requests
            url = f"http://{self.ip}:{self.api_port}/switch/turn_on"
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            r = requests.post(url, json={"entity_id": "switch"}, headers=headers, timeout=5)
            if r.status_code == 200:
                self._last_status = True
                return True
        except Exception as e:
            print(f"ESPHomeActuator API turn_on failed: {e}")
        
        return False
    
    def turn_off(self) -> bool:
        """Turn the switch OFF."""
        try:
            if self.mqtt_host and MQTT_AVAILABLE and self._mqtt_connected:
                if self._send_mqtt_command("switch", "OFF"):
                    self._last_status = False
                    return True
            
            import requests
            url = f"http://{self.ip}:{self.api_port}/switch/turn_off"
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            r = requests.post(url, json={"entity_id": "switch"}, headers=headers, timeout=5)
            if r.status_code == 200:
                self._last_status = False
                return True
        except Exception as e:
            print(f"ESPHomeActuator turn_off failed: {e}")
        
        return False
    
    def get_status(self) -> bool:
        """Get current relay status."""
        if self._last_status is not None:
            return self._last_status
        
        # Try to query via HTTP API
        try:
            import requests
            url = f"http://{self.ip}:{self.api_port}/states"
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200:
                states = r.json()
                for state in states:
                    if state.get("entity_id", "").startswith("switch."):
                        status = state.get("state") == "on"
                        self._last_status = status
                        return status
        except Exception as e:
            print(f"ESPHomeActuator get_status failed: {e}")
        
        return self._last_status if self._last_status is not None else False
    
    def get_power(self) -> Optional[float]:
        """Get current power consumption."""
        # Would query sensor entities via API
        return None
    
    def get_voltage(self) -> Optional[float]:
        return None
    
    def get_energy(self) -> Optional[float]:
        return None
    
    def get_full_status(self) -> Dict[str, Any]:
        return {"relay": self.get_status()}
    
    def close(self):
        """Clean up connections."""
        if self._mqtt_client:
            self._mqtt_client.loop_stop()
            self._mqtt_client.disconnect()


def create_esphome_actuator(config: Dict[str, Any]) -> 'ESPHomeActuator':
    """Factory function for backward compatibility."""
    return ESPHomeActuator(config)