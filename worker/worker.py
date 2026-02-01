import yaml
import time
from simulator.sim import HardwareSimulator

def execute_testplan(plan_path: str):
    sim = HardwareSimulator()

    with open(plan_path) as f:
        plan = yaml.safe_load(f)

    results = []

    for step in plan["steps"]:
        action = step["action"]

        if action == "set_fan_speed":
            res = sim.set_fan_speed(step["value"])

        elif action == "apply_load":
            res = sim.apply_load(step["watts"], step["duration_sec"])

        elif action == "read_temperature":
            res = sim.read_temperature()
            if res["temperature"] > step["expect_max_c"]:
                res["status"] = "FAIL"
            else:
                res["status"] = "PASS"

        else:
            res = {"error": "Unknown action"}

        results.append({
            "step": step["id"],
            "result": res,
            "timestamp": int(time.time())
        })

    return results
