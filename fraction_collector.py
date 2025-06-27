from drip_counter_v2 import DripCounter
from cnc_machine import CNC_Machine

class FractionCollector:
    counter=None
    cnc_machine=None

    def __init__(self, sensor_id=1):
        self.counter = DripCounter(sensor_id=sensor_id)
        self.cnc_machine = CNC_Machine()

    def collect_fraction(self, threshold, location, location_index, timeout=10.0, rate_index=8):
        
        #Move to the vial
        self.cnc_machine.move_to_location(location, location_index, safe=True)

        #Start the counter
        self.counter.reset()
        print("Starting fraction collection...")
        if not self.counter.wait_for_drops(threshold, rate_index, timeout):
            print("Failed to collect enough drops.")
            return False
        
        print("Fraction collection complete.")
        return True