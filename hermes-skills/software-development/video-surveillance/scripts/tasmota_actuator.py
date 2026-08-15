"""Tasmota actuator (MQTT + HTTP + WebSocket)."""
from typing import Dict, Any, Optional
import json
import threading
import time
from .base import BaseActuator

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class TasmotaActuator(BaseActuator):
    """Generic Tasmota device actuator (MQTT + HTTP + WebSocket)."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Required config
        self.ip = config.get("ip")
        if not self.ip:
            raise ValueError("TasmotaActuator requires 'ip' in config")
        
        # Optional config
        self.mqtt_host = config.get("mqtt_host")
        self.mqtt_port = config.get("mqtt_port", 1883)
        self.mqtt_user = config.get("mqtt_user")
        self.mqtt_password = config.get("mqtt_password")
        self.mqtt_topic = config.get("mqtt_topic", "cmnd/tasmota")
        self.device_name = config.get("device_name", "tasmota")
        
        # HTTP settings
        self.http_timeout = config.get("http_timeout", 5)
        self.use_http_fallback = config.get("use_http_fallback", True)
        
        # Connection state
        self._mqtt_client = None
        self._mqtt_connected = False
        self._last_status: Optional[bool] = None
        
        # Initialize MQTT if configured
        if self.mqtt_host and MQTT_AVAILABLE:
            self._init_mqtt()
    
    def _init_mqtt(self):
        """Initialize MQTT client."""
        if not MQTT_AVAILABLE:
            return
        
        self._mqtt_client = mqtt.Client(client_id=f"superguard_{self.device_name}")
        if self.mqtt_user and self.mqtt_password:
            self._mqtt_client.username_pw_set(self.mqtt_user, self.mqtt_password)
        
        self._mqtt_client.on_connect = self._on_mqtt_connect
        self._mqtt_client.on_disconnect = self._on_mqtt_disconnect
        self._mqtt_client.on_message = self._on_mqtt_message
        
        try:
            self._mqtt_client.connect(self.mqtt_host, self.mqtt_port, 60)
            self._mqtt_client.loop_start()
        except Exception as e:
            print(f"TasmotaActuator MQTT connect failed: {e}")
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._mqtt_connected = True
            client.subscribe(f"stat/{self.device_name}/#")
            print(f"TasmotaActuator MQTT connected to {self.mqtt_host}")
        else:
            print(f"TasmotaActuator MQTT connect failed: {rc}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        self._mqtt_connected = False
        print(f"TasmotaActuator MQTT disconnected: {rc}")
    
    def _on_mqtt_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = msg.payload.decode()
            if "POWER" in topic.upper():
                self._last_status = payload.upper() == "ON"
        except Exception as e:
            print(f"TasmotaActuator MQTT message error: {e}")
    
    def _send_mqtt_command(self, command: str) -> bool:
        """Send command via MQTT (Tasmota format: cmnd/topic/command)."""
        if not self._mqtt_connected or not self._mqtt_client:
            return False
        try:
            topic = f"cmnd/{self.device_name}/{command.upper()}"
            self._mqtt_client.publish(topic, "ON" if "ON" in command.upper() else "OFF")
            return True
        except Exception as e:
            print(f"TasmotaActuator MQTT publish failed: {e}")
            return False
    
    def _send_http_command(self, endpoint: str, payload: Optional[Dict] = None) -> bool:
        """Send command via HTTP (Tasmota HTTP API)."""
        if not REQUESTS_AVAILABLE:
            return False
        try:
            url = f"http://{self.ip}/{endpoint}"
            if payload:
                r = requests.post(url, json=payload, timeout=self.http_timeout)
            else:
                r = requests.get(url, timeout=self.http_timeout)
            return r.status_code == 200
        except Exception as e:
            print(f"TasmotaActuator HTTP command failed: {e}")
            return False
    
    def _execute_with_fallback(self, mqtt_cmd: str, http_endpoint: str, http_payload: Optional[Dict] = None) -> bool:
        """Execute command with MQTT first, fallback to HTTP."""
        if self.mqtt_host and MQTT_AVAILABLE and self._mqtt_connected:
            if self._send_mqtt_command(mqtt_cmd):
                return True
        
        if self.use_http_fallback and REQUESTS_AVAILABLE:
            return self._send_http_command(http_endpoint, http_payload)
        
        return False
    
    def turn_on(self) -> bool:
        """Turn the relay ON."""
        try:
            if self._execute_with_fallback("POWER", "cm", {"POWER": "ON"}):
                self._last_status = True
                return True
            return False
        except Exception as e:
            print(f"TasmotaActuator turn_on failed: {e}")
            return False
    
    def turn_off(self) -> bool:
        """Turn the relay OFF."""
        try:
            if self._execute_with_fallback("POWER", "cm", {"POWER": "OFF"}):
                self._last_status = False
                return True
            return False
        except Exception as e:
            print(f"TasmotaActuator turn_off failed: {e}")
            return False
    
    def get_status(self) -> bool:
        """Get current relay status."""
        if self._last_status is not None:
            return self._last_status
        
        # Try HTTP status
        if REQUESTS_AVAILABLE:
            try:
                r = requests.get(f"http://{self.ip}/cm?cmnd=STATUS%208", timeout=self.http_timeout)
                if r.status_code == 200:
                    data = r.json()
                    if "StatusSNS" in data and "POWER" in data["StatusSNS"]:
                        status = data["StatusSNS"]["POWER"] == "ON"
                        self._last_status = status
                        return status
            except Exception as e:
                print(f"TasmotaActuator get_status HTTP failed: {e}")
        
        return self._last_status if self._last_status is not None else False
    
    def get_power(self) -> Optional[float]:
        """Get current power consumption (if supported)."""
        if REQUESTS_AVAILABLE:
            try:
                r = requests.get(f"http://{self.ip}/cm?cmnd=STATUS%208", timeout=self.http_timeout)
                if r.status_code == 200:
                    data = r.json()
                    if "StatusSNS" in data and "ENERGY" in data["StatusSNS"]:
                        return float(data["StatusSNS"]["ENERGY"].get("Power", 0))
            except Exception as e:
                print(f"TasmotaActuator get_power failed: {e}")
        return None
    
    def get_voltage(self) -> Optional[float]:
        if REQUESTS_AVAILABLE:
            try:
                r = requests.get(f"http://{self.ip}/cm?cmnd=STATUS%208", timeout=self.http_timeout)
                if r.status_code == 200:
                    data = r.json()
                    if "StatusSNS" in data and "ENERGY" in data["StatusSNS"]:
                        return float(data["StatusSNS"]["ENERGY"].get("Voltage", 0))
            except Exception as e:
                print(f"TasmotaActuator get_voltage failed: {e}")
        return None
    
    def get_energy(self) -> Optional[float]:
        if REQUESTS_AVAILABLE:
            try:
                r = requests.get(f"http://{self.ip}/cm?cmnd=STATUS%208", timeout=self.http_timeout)
                if r.status_code == 200:
                    data = r.json()
                    if "StatusSNS" in data and "ENERGY" in data["StatusSNS"]:
                        return float(data["StatusSNS"]["ENERGY"].get("Total", 0))
            except Exception as e:
                print(f"TasmotaActuator get_energy failed: {e}")
        return None
    
    def get_full_status(self) -> Dict[str, Any]:
        status = {"relay": self.get_status()}
        if self.get_power() is not None:
            status["power"] = self.get_power()
        if self.get_voltage() is not None:
            status["voltage"] = self.get_voltage()
        return status
    
    def close(self):
        """Clean up connections."""
        if self._mqtt_client:
            self._mqtt_client.loop_stop()
            self._mqtt_client.disconnect()
            self._mqtt_client = None
            self._mqtt_connected = False


def create_tasmota_actuator(config: Dict[str, Any]) -> 'TasmotaActuator':
    """Factory function for backward compatibility."""
    return TasmotaActuator(config)