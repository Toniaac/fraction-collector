import urllib.request
import time

sensor_id = 1
url = f"http://localhost:22006/NeuLogAPI?GetSensorValue:[DropCounter],[{sensor_id}]"
print("Starting drip counter...")

while True:
    try:
        with urllib.request.urlopen(url) as response:
            body = response.read().decode("utf-8").strip()
            print("Raw response:", body)

            if body.startswith("{\"GetSensorValue\":[") and body.endswith("]}"):
                # Safely extract the drop count
                try:
                    count = int(body.split("[")[1].split("]")[0])
                    print(f"Drops counted: {count}")
                except Exception as parse_error:
                    print("Parsing error:", parse_error)
            else:
                print("Non-standard response (sensor may be initializing):", body)

    except Exception as e:
        print("Connection error:", e)

    time.sleep(1)
