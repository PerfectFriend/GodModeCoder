"""Tuya Smart Plug actuator (local control via tinytuya)."""
from typing import Dict, Any, Optional
import json
import threading
import time
from .base import BaseActuator


class TuyaActuator(BaseActuator):
    """Tuya Smart Plug actuator using local control (tinytuya 3.4+)."""
    
    # DPS codes for standard Tuya plugs
    DPS_RELAY = 1      # Relay (bool)
    DPS_VOLTAGE = 20   # Voltage (0.1V units)
    DPS_POWER = 22     # Power (0.1W units)
    DPS_ENERGY = 23    # Energy (Wh)
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Required config
        self.ip = config.get("ip")
        self.device_id = config.get("device_id")
        self.local_key = config.get("local_key")
        
        if not all([self.ip, self.device_id, self.local_key]):
            raise ValueError("TuyaActuator requires ip, device_id, and local_key in config")
        
        # Optional config
        self.port = config.get("port", 6668)
        self.version = config.get("version", 3.4)
        self.connection_timeout = config.get("connection_timeout", 5)
        
        # Internal state
        self._device = None
        self._conn_lock = threading.Lock()
        self._last_status: Optional[bool] = None
        self._last_power: Optional[float] = None
    
    def _get_device(self):
        """Get or create Tuya device with fresh connection."""
        with self._conn_lock:
            if self._device is None:
                import tinytuya
                self._device = tinytuya.OutletDevice(
                    dev_id=self.device_id,
                    address=self.ip,
                    local_key=self.local_key,
                    version=self.version
                )
                self._device.set_socketPersistent(False)
                self._device.set_socketTimeout(self.connection_timeout)
            return self._device
    
    def _execute_with_retry(self, func, max_retries=2):
        """Execute Tuya command with retry on connection failure."""
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                return func()
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    # Force new connection on next attempt
                    with self._conn_lock:
                        self._device = None
                    time.sleep(0.5)
                else:
                    raise
        raise last_error
    
    def turn_on(self) -> bool:
        """Turn the plug ON."""
        def _on():
            device = self._get_device()
            result = device.set_value(self.DPS_RELAY, True)
            return result
        
        try:
            result = self._execute_with_retry(_on)
            if result:
                self._last_status = True
            return bool(result)
        except Exception as e:
            print(f"TuyaActuator turn_on failed: {e}")
            return False
    
    def turn_off(self) -> bool:
        """Turn the plug OFF."""
        def _off():
            device = self._get_device()
            result = device.set_value(self.DPS_RELAY, False)
            return result
        
        try:
            result = self._execute_with_retry(_off)
            if result:
                self._last_status = False
            return bool(result)
        except Exception as e:
            print(f"TuyaActuator turn_off failed: {e}")
            return False
    
    def get_status(self) -> bool:
        """Get current relay status."""
        def _status():
            device = self._get_device()
            data = device.status()
            if data and "dps" in data:
                return bool(data["dps"].get(self.DPS_RELAY, False))
            return False
        
        try:
            status = self._execute_with_retry(_status)
            self._last_status = status
            return status
        except Exception as e:
            print(f"TuyaActuator get_status failed: {e}")
            return self._last_status if self._last_status is not None else False
    
    def get_power(self) -> Optional[float]:
        """Get current power consumption in watts."""
        def _power():
            device = self._get_device()
            data = device.status()
            if data and "dps" in data:
                # Power is in 0.1W units (DPS 22)
                raw_power = data["dps"].get(self.DPS_POWER)
                if raw_power is not None:
                    return float(raw_power) / 10.0
            return None
        
        try:
            power = self._execute_with_retry(_power)
            self._last_power = power
            return power
        except Exception as e:
            print(f"TuyaActuator get_power failed: {e}")
            return self._last_power
    
    def get_voltage(self) -> Optional[float]:
        """Get current voltage."""
        def _voltage():
            device = self._get_device()
            data = device.status()
            if data and "dps" in data:
                raw_voltage = data["dps"].get(self.DPS_VOLTAGE)
                if raw_voltage is not None:
                    return float(raw_voltage) / 10.0
            return None
        
        try:
            return self._execute_with_retry(_voltage)
        except Exception as e:
            print(f"TuyaActuator get_voltage failed: {e}")
            return None
    
    def get_energy(self) -> Optional[float]:
        """Get total energy consumption."""
        def _energy():
            device = self._get_device()
            data = device.status()
            if data and "dps" in data:
                return float(data["dps"].get(self.DPS_ENERGY, 0))
            return None
        
        try:
            return self._execute_with_retry(_energy)
        except Exception as e:
            print(f"TuyaActuator get_energy failed: {e}")
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
        with self._conn_lock:
            self._device = None


# Backward compatibility factory
def create_tuya_actuator(config: Dict[str, Any]) -> 'TuyaActuator':
    """Factory function for backward compatibility."""
    return TuyaActuator(config)