import json

config = json.load(open("config.json"))

kinematics_config = config["geometry"]
kinematics_config["steps_per_rev"] = config["steppers"]["steps_per_rev"]

motion_config = config["motion"]

stepper_config = config["steppers"]

leds_config = config["leds"]