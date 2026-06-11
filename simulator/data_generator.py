import random
import requests
import time


DATA_URL = "http://127.0.0.1:8000/data/"
SENSORS_URL = "http://127.0.0.1:8000/sensors/"
HEALTH_URL = "http://127.0.0.1:8000/"

# Keep high while testing
TEMPERATURE_ALERT_CHANCE = 100
HUMIDITY_ALERT_CHANCE = 100
DOOR_OPEN_ALERT_CHANCE = 100

SIMULATOR_DELAY = 60


def wait_for_backend():
    print("Waiting for backend to become available...")

    while True:
        try:
            response = requests.get(HEALTH_URL, timeout=2)

            if response.status_code == 200:
                print("Backend is available.")
                return

        except Exception:
            pass

        time.sleep(1)


def should_trigger_alert(chance_percent):
    return random.randint(1, 100) <= chance_percent


def fetch_sensors():
    try:
        response = requests.get(SENSORS_URL, timeout=5)

        if response.status_code == 200:
            sensors = response.json()

            active_sensors = [
                sensor for sensor in sensors
                if sensor.get("status") == "active"
            ]

            return active_sensors

        print("Failed to fetch sensors:", response.status_code)
        print("Response:", response.text)
        return []

    except Exception as e:
        print("Error fetching sensors:", e)
        return []


def generate_temperature_value():
    if should_trigger_alert(TEMPERATURE_ALERT_CHANCE):
        return round(random.uniform(201, 350), 2)
    return round(random.uniform(2, 180), 2)


def generate_humidity_value():
    if should_trigger_alert(HUMIDITY_ALERT_CHANCE):
        return round(random.uniform(101, 150), 2)
    return round(random.uniform(40, 95), 2)


def generate_door_open_value():
    return should_trigger_alert(DOOR_OPEN_ALERT_CHANCE)


def generate_payload(sensor):
    sensor_id = sensor["id"]
    sensor_type = sensor["sensor_type"]

    temperature = round(random.uniform(2, 180), 2)
    humidity = round(random.uniform(40, 95), 2)
    door_open = False

    if sensor_type == "temperature":
        temperature = generate_temperature_value()

    elif sensor_type == "humidity":
        humidity = generate_humidity_value()

    elif sensor_type == "door_open":
        door_open = generate_door_open_value()

    return {
        "sensor_id": sensor_id,
        "temperature": temperature,
        "humidity": humidity,
        "door_open": door_open
    }


def send_data(data):
    try:
        response = requests.post(DATA_URL, json=data, timeout=10)

        print("\n======================================")
        print("Sent Data:", data)
        print("Response Status:", response.status_code)

        try:
            body = response.json()
            print("Response Body:", body)

            alerts = body.get("alerts_generated", [])

            if alerts:
                print("ALERTS GENERATED:")
                for alert in alerts:
                    print("-", alert.get("message"))
            else:
                print("No alerts generated.")

        except Exception:
            print("Response Text:", response.text)

    except Exception as e:
        print("Error sending data:", e)


def main():
    print("Starting sensor simulator...")
    print(f"Temperature alert chance: {TEMPERATURE_ALERT_CHANCE}%")
    print(f"Humidity alert chance: {HUMIDITY_ALERT_CHANCE}%")
    print(f"Door open alert chance: {DOOR_OPEN_ALERT_CHANCE}%")
    print(f"Simulator delay: {SIMULATOR_DELAY} seconds")

    wait_for_backend()

    while True:
        sensors = fetch_sensors()

        if not sensors:
            print("No active sensors found. Create sensors first.")
            time.sleep(SIMULATOR_DELAY)
            continue

        selected_sensor = random.choice(sensors)

        print("\nSelected Sensor:", selected_sensor)

        data = generate_payload(selected_sensor)

        send_data(data)

        time.sleep(SIMULATOR_DELAY)


if __name__ == "__main__":
    main()
