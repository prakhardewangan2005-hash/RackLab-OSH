import random
import time

class HardwareSimulator:
    def __init__(self):
        self.fan_speed = 50
        self.temperature = 35.0

    def set_fan_speed(self, value: int):
        self.fan_speed = value
        return {"fan_speed": self.fan_speed}

    def apply_load(self, watts: int, duration_sec: int):
        for _ in range(duration_sec):
            self.temperature += watts / 300
            time.sleep(0.2)
        return {"temperature": round(self.temperature, 2)}

    def read_temperature(self):
        noise = random.uniform(-1.5, 1.5)
        return {"temperature": round(self.temperature + noise, 2)}
