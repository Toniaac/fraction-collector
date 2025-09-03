import serial
import time
import matplotlib.pyplot as plt
from collections import deque

COM_PORT = 'COM15'  # Update this to your serial port
BAUD_RATE = 19200
MAX_POINTS = 100

weights = deque(maxlen=MAX_POINTS)
x_vals = deque(maxlen=MAX_POINTS)

def main():
    try:
        ser = serial.Serial(
            port=COM_PORT,
            baudrate=BAUD_RATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        print(f"Connected to {COM_PORT} at {BAUD_RATE} baud.")

        plt.ion()  # Interactive mode on
        fig, ax = plt.subplots()
        line, = ax.plot([], [], lw=2)
        ax.set_title("FX-120i Live Weight")
        ax.set_xlabel("Samples")
        ax.set_ylabel("Weight (g)")
        ax.grid(True)

        sample_num = 0

        while True:
            ser.write(b'Q\r\n')
            time.sleep(0.3)
            raw = ser.readline().decode(errors='ignore').strip()
            print("Raw:", raw or "No response")

            weight = None
            if raw.startswith("ST,") or raw.startswith("US,"):
                try:
                    weight_str = raw.split(',')[1].strip().split()[0]
                    weight = float(weight_str)
                except Exception as e:
                    print(f"Parse error: {e}")

            if weight is not None:
                weights.append(weight)
                sample_num += 1
                x_vals.append(sample_num)

                line.set_data(x_vals, weights)
                ax.set_xlim(max(0, sample_num - MAX_POINTS), sample_num)
                ax.set_ylim(min(weights) - 1, max(weights) + 1)

                fig.canvas.draw()
                fig.canvas.flush_events()

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\nStopped by user")

    except serial.SerialException as e:
        print(f"Serial error: {e}")

    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")

if __name__ == "__main__":
    main()
