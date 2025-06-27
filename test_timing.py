import urllib.request
import time
import json


class DripCounter:
    def __init__(self, sensor_id=1, sensor_type="DropCounter", host="localhost", port=22006):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.base_url = f"http://{host}:{port}/NeuLogAPI"

    def _get(self, command: str):
        url = f"{self.base_url}?{command}"
        try:
            with urllib.request.urlopen(url) as response:
                return response.read().decode("utf-8").strip()
        except Exception as e:
            print("HTTP error:", e)
            return None

    def _start_experiment(self, rate_index: int, samples: int) -> bool:
        command = f"StartExperiment:[{self.sensor_type}],[{self.sensor_id}],[{rate_index}],[{samples}]"
        response = self._get(command)
        return response == '{"StartExperiment":"True"}'

    def _stop_experiment(self):
        self._get("StopExperiment")

    def _get_samples(self):
        command = f"GetExperimentSamples:[{self.sensor_type}],[{self.sensor_id}]"
        response = self._get(command)
        try:
            data = json.loads(response)
            sample_list = data["GetExperimentSamples"][0][2:]  # skip sensor name and ID
            print(f"Retrieved {len(sample_list)} samples.")
            return sample_list
        except Exception as e:
            print("Failed to parse experiment samples:", e)
            return []


    def wait_for_drops(self, threshold: int, rate_index: int = 8, timeout: float = 10.0):
        """
        Waits for at least `threshold` drops using experiment sampling.
        - `rate_index` sets the sample rate (default 8 = 10 Hz)
        - `timeout` is total experiment duration in seconds
        """
        samples = int(timeout * self._rate_to_hz(rate_index))
        print(f"Starting experiment: {samples} samples at rate index {rate_index} (timeout: {timeout}s)")

        if not self._start_experiment(rate_index, samples):
            print("Failed to start experiment.")
            return False

        time.sleep(timeout + 0.5)  # Wait for experiment to finish

        values = self._get_samples()
        print("Raw sample values:", values)
        if not values:
            print("No data received.")
            return False

        max_value = max(values)
        print(f"Max drop count: {max_value}")
        return max_value >= threshold

    def reset(self):
        command = f"ResetSensor:[{self.sensor_type}],[{self.sensor_id}]"
        response = self._get(command)
        return response == '{"CalibSensor":"True"}'

    def _rate_to_hz(self, rate_index):
        # Derived from the NeuLog docs
        rate_map = {
            1: 10000, 2: 3000, 3: 2000, 4: 1000, 5: 100, 6: 50, 7: 20, 8: 10,
            9: 5, 10: 2, 11: 1, 12: 0.5, 13: 0.25, 14: 0.1, 15: 0.033, 16: 0.016,
            17: 0.0083, 18: 0.0042, 19: 0.0017, 20: 0.0005, 21: 0.0003
        }
        return rate_map.get(rate_index, 10)  # default to 10 Hz if unknown


# --- Example usage ---
if __name__ == "__main__":
    counter = DripCounter(sensor_id=1)
    counter.reset()

    success = counter.wait_for_drops(threshold=5, rate_index=8, timeout=5)

    if success:
        print("[SIGNAL] Required drop count reached.")
    else:
        print("[WARNING] Drop threshold not met.")
