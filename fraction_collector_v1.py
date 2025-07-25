from drip_counter import DripCounter
from cnc_machine import CNC_Machine
from Elveflow64 import ElveflowMUXWrapper  
import time


class FractionCollector:
    counter = None
    cnc_machine = None
    valve_controller = None
    mux_id = None

    def __init__(self, sensor_id=1, mux_com_port='COM6'):
        self.counter = DripCounter(sensor_id=sensor_id)
        self.cnc_machine = CNC_Machine()
        self.valve_controller = ElveflowMUXWrapper()
        self.mux_id = self.valve_controller.initialize(mux_com_port)
        if self.mux_id < 0:
            raise RuntimeError("Failed to initialize Elveflow MUX device.")

    def collect_fraction(self, threshold, location, location_index, rinse_time = 10, timeout=None, poll_interval=0.1):
        self.move_to_waste()
        # Rinse collection tubing 
        self.set_valve_state(state=0)
        print(f"Rinsing collection tubing for {rinse_time} seconds...\n")
        time.sleep(rinse_time)  # To be replaced with tubing rinse time
        self.set_valve_state(state=1)  # Close valve 1 (waste)
        print("Rinsing complete.\n")

        # Move to the vial
        self.cnc_machine.move_to_location(location, location_index, safe=False)
        self.cnc_machine.move_to_point(z=-35)
        # Open valve 1
        self.set_valve_state(state=0)
        print(f"Collecting fraction at {location} (index {location_index}) until {threshold} drops are counted...\n")
        # Start the counter
        self.counter.reset()
        print("Starting fraction collection...\n")
        if not self.counter.wait_for_drops(threshold, timeout=timeout, poll_interval=poll_interval):
            print("Failed to collect enough drops.\n")

            # Close valve 1 even on failure
            self.set_valve_state(state=1)
            return False
        print("Fraction collection complete.\n")

        # Move to the CNC waste location
        self.move_to_waste()

        return True

    def set_valve_state(self, state: int):
        """Turn valve 1 on (0) or off (1)."""
        pattern = [0] * 16
        pattern[0] = state  # only valve 1 is affected
        err = self.valve_controller.wire_set_all_valves(self.mux_id, pattern=pattern)
        if err != 0:
            print(f"Warning: failed to set valve 1 to {state}, error code {err}")

    def move_to_waste(self, location = "cnc_waste_location", location_index=0, safe=False):
        """Close valve and move to the CNC waste location."""
        self.set_valve_state(state=1)
        self.cnc_machine.move_to_location(location, location_index, safe=safe)
        self.cnc_machine.move_to_point(z=-35)
