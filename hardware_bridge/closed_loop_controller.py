"""
Workplace Safety Sentinel - Hardware Closed-Loop Actuator Controller
Listens for edge vision inference alert events (via MQTT, Webhook, or Direct Call)
and commands the physical microcontroller (ESP32 / Relay / Siren) to act in real time.
"""

import json
import time
import logging
import threading
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] (Bridge) %(message)s")

class HardwareClosedLoopBridge:
    def __init__(self, serial_port: Optional[str] = None, baudrate: int = 115200):
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.serial_conn = None
        self.actuator_state = {
            "siren_active": False,
            "strobe_active": False,
            "machine_estop_interlock": False,
            "neopixel_color": "GREEN",
            "last_trigger_event": None,
            "last_trigger_timestamp": None,
            "hardware_connected": False
        }
        self.init_serial()

    def init_serial(self):
        if self.serial_port:
            try:
                import serial
                self.serial_conn = serial.Serial(self.serial_port, self.baudrate, timeout=1)
                self.actuator_state["hardware_connected"] = True
                logging.info(f"Connected to ESP32 on {self.serial_port} @ {self.baudrate} baud.")
            except Exception as e:
                logging.warning(f"Could not open serial port {self.serial_port}: {e}. Running in simulation mode.")
                self.actuator_state["hardware_connected"] = False
        else:
            logging.info("Hardware Bridge running in simulated hardware mode (Live Actuator Telemetry).")

    def handle_safety_event(self, event_data: dict):
        """
        Processes a perception violation event from PipeGen edge vision:
        - DANGER_ZONE_INTRUSION: Immediate machine interlock + red strobe + buzzer
        - PPE_VIOLATION: Yellow warning strobe + reminder chime
        - CLEAR: Reset to green safe status
        """
        event_type = event_data.get("event_type", "UNKNOWN")
        severity = event_data.get("severity", "LOW")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        logging.info(f"[PERCEPTION -> ACTION] Processing Event: {event_type} (Severity: {severity})")

        if severity == "CRITICAL" or event_type in ["DANGER_ZONE_INTRUSION", "WORKER_FALL"]:
            self.trigger_critical_alarm(event_data, timestamp)
        elif severity == "WARNING" or event_type == "PPE_VIOLATION":
            self.trigger_warning_alarm(event_data, timestamp)
        else:
            self.reset_all_clear()

    def trigger_critical_alarm(self, event_data: dict, timestamp: str):
        self.actuator_state["siren_active"] = True
        self.actuator_state["strobe_active"] = True
        self.actuator_state["machine_estop_interlock"] = True
        self.actuator_state["neopixel_color"] = "RED"
        self.actuator_state["last_trigger_event"] = event_data
        self.actuator_state["last_trigger_timestamp"] = timestamp

        cmd = json.dumps({"cmd": "ALARM_CRITICAL", "relay": 1, "buzzer": 1, "rgb": "FF0000"}) + "\n"
        self._send_command(cmd)

    def trigger_warning_alarm(self, event_data: dict, timestamp: str):
        self.actuator_state["siren_active"] = False
        self.actuator_state["strobe_active"] = True
        self.actuator_state["machine_estop_interlock"] = False
        self.actuator_state["neopixel_color"] = "YELLOW"
        self.actuator_state["last_trigger_event"] = event_data
        self.actuator_state["last_trigger_timestamp"] = timestamp

        cmd = json.dumps({"cmd": "ALARM_WARNING", "relay": 0, "buzzer": 0, "rgb": "FFFF00"}) + "\n"
        self._send_command(cmd)

    def reset_all_clear(self):
        self.actuator_state["siren_active"] = False
        self.actuator_state["strobe_active"] = False
        self.actuator_state["machine_estop_interlock"] = False
        self.actuator_state["neopixel_color"] = "GREEN"

        cmd = json.dumps({"cmd": "ALL_CLEAR", "relay": 0, "buzzer": 0, "rgb": "00FF00"}) + "\n"
        self._send_command(cmd)

    def _send_command(self, cmd_str: str):
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.write(cmd_str.encode('utf-8'))
            except Exception as e:
                logging.error(f"Error transmitting to microcontroller: {e}")
        else:
            logging.debug(f"[Simulated ESP32 Bus] Sent: {cmd_str.strip()}")

    def get_status(self) -> dict:
        return self.actuator_state

# Global singleton for backend integration
bridge = HardwareClosedLoopBridge()

if __name__ == "__main__":
    print("[Hardware Closed-Loop Bridge] Testing event handling...")
    bridge.handle_safety_event({"event_type": "DANGER_ZONE_INTRUSION", "severity": "CRITICAL", "worker_id": "T-102"})
    print("Actuator status:", bridge.get_status())
    time.sleep(1)
    bridge.reset_all_clear()
    print("Reset status:", bridge.get_status())
