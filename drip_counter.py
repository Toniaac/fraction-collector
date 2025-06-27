import urllib.request
import time


class DripCounter:
    def __init__(self, sensor_id=1):
        self.sensor_id = sensor_id
        self.sensor_type = "DropCounter"
        self.url_base = "http://localhost:22006/NeuLogAPI"

    def _get(self, endpoint):
        try:
            with urllib.request.urlopen(endpoint) as response:
                return response.read().decode("utf-8").strip()
        except Exception as e:
            print("HTTP error:", e)
            return None

    def _get_drop_count(self):
        url = f"{self.url_base}?GetSensorValue:[{self.sensor_type}],[{self.sensor_id}]"
        result = self._get(url)
        if result and result.startswith("{\"GetSensorValue\":[") and result.endswith("]}"):
            try:
                return int(result.split("[")[1].split("]")[0])
            except Exception as parse_error:
                print("Parsing error:", parse_error)
        else:
            print("Unexpected response:", result)
        return None

    def wait_for_drops(self, threshold, timeout=None, poll_interval=0.1):
        self.reset()
        start_time = time.time()
        print(f"Waiting for {threshold} drops...")

        while True:
            loop_start = time.time()
            count = self._get_drop_count()
            loop_duration = time.time() - loop_start

            if count is not None:
                print(f"Drops counted: {count} (poll took {loop_duration:.3f} s)")
                if count >= threshold:
                    print(f"Threshold reached: {count}")
                    return True

            if timeout is not None and (time.time() - start_time) > timeout:
                print("Timeout reached.")
                return False

            time.sleep(max(0, poll_interval - loop_duration))


    def reset(self):
        url = f"{self.url_base}?ResetSensor:[{self.sensor_type}],[{self.sensor_id}]"
        result = self._get(url)
        if result == '{"CalibSensor":"True"}':
            print("Sensor reset successful.")
            return True
        else:
            print("Sensor reset failed or returned unexpected response:", result)
            return False

if __name__ == "__main__":
    counter = DripCounter(sensor_id=1)
    success = counter.wait_for_drops(threshold=10, timeout=30, poll_interval=0.1)

    if success:
        print("[SIGNAL] Collected required drops.")
    else:
        print("[WARNING] Did not reach drop target in time.")