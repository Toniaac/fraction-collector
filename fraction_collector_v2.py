from drip_counter_v2 import DripCounter
from cnc_machine import CNC_Machine
from Elveflow64 import ElveflowMUXWrapper  # assumes wrapper class is defined here


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

    def collect_fraction(self, threshold, location, location_index, timeout=10.0, rate_index=8):
        # Move to the vial
        self.cnc_machine.move_to_location(location, location_index, safe=True)

        # Open valve 1
        self.set_valve_state(state=0)

        # Start the counter
        self.counter.reset()
        print("Starting fraction collection...")
        if not self.counter.wait_for_drops(threshold, rate_index, timeout):
            print("Failed to collect enough drops.")

            # Close valve 1 even on failure
            self.set_valve_state(state=1)
            return False

        print("Fraction collection complete.")

        # Close valve 1
        self.set_valve_state(state=1)
        return True

    def set_valve_state(self, state: int):
        """Turn valve 1 on (0) or off (1)."""
        pattern = [0] * 16
        pattern[0] = state  # only valve 1 is affected
        err = self.valve_controller.wire_set_all_valves(self.mux_id, pattern=pattern)
        if err != 0:
            print(f"Warning: failed to set valve 1 to {state}, error code {err}")
