"""Shelly actuator (Gen1 CoAP/HTTP + Plus WS/MQTT/HTTP)."""
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
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class ShellyActuator(BaseActuator):
    """Shelly device actuator supporting Gen1 (CoAP/HTTP) and Plus (WS/MQTT/HTTP)."""
    
    GENERATION_1 = "gen1"
    GENERATION_PLUS = "plus"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Required config
        self.ip = config.get("ip")
        if not self.ip:
            raise ValueError("ShellyActuator requires 'ip' in config")
        
        # Optional config
        self.generation = config.get("generation", self.GENERATION_PLUS)  # "gen1" or "plus"
        self.auth_key = config.get("auth_key")  # for Plus auth
        self.mqtt_host = config.get("mqtt_host")
        self.mqtt_port = config.get("mqtt_port", 1883)
        self.mqtt_user = config.get("mqtt_user")
        self.mqtt_password = config.get("mqtt_password")
        self.device_id = config.get("device_id")  # for Plus MQTT
        
        # HTTP settings
        self.http_timeout = config.get("http_timeout", 5)
        self.use_rpc = config.get("use_rpc", True)  # use RPC for Plus
        
        # Connection state
        self._last_status: Optional[bool] = None
        self._ws_client = None
        self._ws_thread = None
        
        # Initialize based on generation
        if self.generation == self.GENERATION_PLUS:
            self._init_plus()
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for Plus devices."""
        if self.auth_key:
            return {"Authorization": f"Bearer {self.auth_key}"}
        return {}
    
    def _send_http_request(self, method: str, endpoint: str, payload: Optional[Dict] = None) -> Optional[Dict]:
        """Send HTTP request to Shelly device."""
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            import requests
            url = f"http://{self.ip}/{endpoint}"
            headers = {"Content-Type": "application/json"}
            headers.update(self._get_auth_headers())
            
            if method.upper() == "GET":
                r = requests.get(url, headers=headers, timeout=self.http_timeout)
            elif method.upper() == "POST":
                r = requests.post(url, headers=headers, json=payload, timeout=self.http_timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if r.status_code == 200:
                return r.json()
            else:
                print(f"ShellyActuator HTTP {r.status_code}: {r.text}")
                return None
        except Exception as e:
            print(f"ShellyActuator HTTP request failed: {e}")
            return None
    
    def _send_rpc(self, method: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Send RPC call (Plus generation)."""
        if self.generation != self.GENERATION_PLUS:
            return None
        
        payload = {"id": 1, "method": method, "params": params or {}}
        return self._send_http_request("POST", "rpc", payload)
    
    def turn_on(self) -> bool:
        """Turn the relay ON."""
        try:
            if self.generation == self.GENERATION_PLUS:
                result = self._send_rpc("Switch.Set", {"id": 0, "on": True})
                if result and result.get("result", {}).get("on") is True:
                    self._last_status = True
                    return True
            else:
                # Gen1: HTTP GET /relay/0?turn=on
                if REQUESTS_AVAILABLE:
                    try:
                        import requests
                        url = f"http://{self.ip}/relay/0?turn=on"
                        r = requests.get(f"http://{self.ip}/relay/0?turn=on", timeout=self.http_timeout)
                        if r.status_code == 200:
                            self._last_status = True
                            return True
                    except Exception as e:
                        print(f"ShellyActuator Gen1 turn_on failed: {e}")
            return False
        except Exception as e:
            print(f"ShellyActuator turn_on failed: {e}")
            return False
    
    def turn_off(self) -> bool:
        """Turn the relay OFF."""
        try:
            if self.generation == self.GENERATION_PLUS:
                result = self._send_rpc("Switch.Set", {"id": 0, "on": False})
                if result and result.get("result", {}).get("on") is False:
                    self._last_status = False
                    return True
            else:
                if REQUESTS_AVAILABLE:
                    try:
                        import requests
                        r = requests.get(f"http://{self.ip}/relay/0?turn=off", timeout=self.http_timeout)
                        if r.status_code == 200:
                            self._last_status = False
                            return True
                    except Exception as e:
                        print(f"ShellyActuator Gen1 turn_off failed: {e}")
            return False
        except Exception as e:
            print(f"ShellyActuator turn_off failed: {e}")
            return False
    
    def get_status(self) -> bool:
        """Get current relay status."""
        try:
            if self.generation == self.GENERATION_PLUS:
                result = self._send_rpc("Switch.GetStatus", {"id": 0})
                if result and "result" in result:
                    status = result["result"].get("on", False)
                    self._last_status = status
                    return status
            else:
                # Gen1: HTTP GET /relay/0
                if REQUESTS_AVAILABLE:
                    import requests
                    r = requests.get(f"http://{self.ip}/relay/0", timeout=self.http_timeout)
                    if r.status_code == 200:
                        data = r.json()
                        status = data.get("ison", False)
                        self._last_status = status
                        return status
        except Exception as e:
            print(f"ShellyActuator get_status failed: {e}")
        
        return self._last_status if self._last_status is not None else False
    
    def get_power(self) -> Optional[float]:
        """Get current power consumption in watts (Plus only)."""
        try:
            if self.generation == self.GENERATION_PLUS:
                result = self._send_rpc("Switch.GetStatus", {"id": 0})
                if result and "result" in result:
                    return float(result["result"].get("apower", 0))
        except Exception as e:
            print(f"ShellyActuator get_power failed: {e}")
        return None
    
    def get_voltage(self) -> Optional[float]:
        """Get current voltage."""
        try:
            if self.generation == self.GENERATION_PLUS:
                result = self._send_rpc("Switch.GetStatus", {"id": 0})
                if result and "result" in result:
                    return float(result["result"].get("voltage", 0))
        except Exception as e:
            print(f"ShellyActuator get_voltage failed: {e}")
        return None
    
    def get_energy(self) -> Optional[float]:
        """Get total energy consumption."""
        try:
            if self.generation == self.GENERATION_PLUS:
                result = self._send_rpc("Switch.GetStatus", {"id": 0})
                if result and "result" in result:
                    return float(result["result"].get("aenergy", {}).get("total", 0))
        except Exception as e:
            print(f"ShellyActuator get_energy failed: {e}")
        return None
    
    def get_full_status(self) -> Dict[str, Any]:
        """Get complete device status."""
        status = {"relay": self.get_status()}
        if self.get_power() is not None:
            status["power"] = self.get_power()
        if self.get_voltage() is not None:
            status["voltage"] = self.get_voltage()
        return status
    
    def close(self):
        """Clean up connections."""
        pass


# Backward compatibility factory
def create_shelly_actuator(config: Dict[str, Any]) -> 'ShellyActuator':
    """Factory function for backward compatibility."""
    return ShellyActuator(config)


# Export for the actuators package
__all__ = ["ShellyActuator", "create_shelly_actuator"]