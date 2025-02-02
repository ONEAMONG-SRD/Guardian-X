import androidhelper
import time
from collections import deque
import requests

# Disable SSL warnings (optional)
requests.packages.urllib3.disable_warnings()

# Initialize Android helper
droid = androidhelper.Android()

# Constants
COLLISION_THRESHOLD = 2.5  # Threshold for collision detection (in m/s²)
SMOOTHING_WINDOW_SIZE = 10  # Number of samples for moving average
EMERGENCY_CONTACT = "9884851545"  # Replace with emergency contact number
API_KEY = "your_fast2sms_api_key_here"  # Replace with your Fast2SMS API key

# Moving average buffer
accel_history = deque(maxlen=SMOOTHING_WINDOW_SIZE)

def smooth_acceleration(accel_data):
    """
    Apply a moving average to smooth accelerometer data.
    """
    accel_history.append(accel_data)
    if len(accel_history) == SMOOTHING_WINDOW_SIZE:
        avg_x = sum(data[0] for data in accel_history) / SMOOTHING_WINDOW_SIZE
        avg_y = sum(data[1] for data in accel_history) / SMOOTHING_WINDOW_SIZE
        avg_z = sum(data[2] for data in accel_history) / SMOOTHING_WINDOW_SIZE
        return avg_x, avg_y, avg_z
    return accel_data  # Return the latest data if buffer is not full

def detect_collision():
    """
    Detect collisions using the accelerometer.
    """
    droid.startSensingTimed(1, 250)  # Start accelerometer sensing (250ms delay)
    print("Collision detection started...")

    while True:
        accel_data = droid.sensorsReadAccelerometer().result
        if accel_data:
            smoothed_data = smooth_acceleration(accel_data)
            if smoothed_data:
                x, y, z = smoothed_data
                total_acceleration = (x**2 + y**2 + z**2) ** 0.5

                # Compare to gravity (9.8 m/s²) to detect significant changes
                if abs(total_acceleration - 9.8) > COLLISION_THRESHOLD:
                    print("Collision detected!")
                    trigger_emergency_message()
                    break
        time.sleep(0.1)

def get_gps_location():
    """
    Retrieve the device's current GPS location.
    """
    droid.startLocating()
    time.sleep(2)  # Wait for location to update
    location = droid.readLocation().result

    # Extract latitude and longitude
    if 'network' in location:
        lat = location['network']['latitude']
        lon = location['network']['longitude']
    elif 'gps' in location:
        lat = location['gps']['latitude']
        lon = location['gps']['longitude']
    else:
        lat, lon = None, None

    droid.stopLocating()
    return lat, lon

def send_emergency_sms(latitude, longitude):
    """
    Send an emergency SMS with the accident location.
    """
    emergency_message = f"Emergency! Accident detected at: Latitude = {latitude}, Longitude = {longitude}"
    print(emergency_message)

    # Fast2SMS API URL
    url = "https://www.fast2sms.com/dev/bulkV2"

    # Parameters for the API request
    params = {
        "authorization": API_KEY,
        "message": emergency_message,
        "language": "english",
        "route": "q",
        "numbers": EMERGENCY_CONTACT,
    }

    # Sending the GET request
    response = requests.get(url, params=params)

    # Displaying the response
    print(response.json())

def trigger_emergency_message():
    """
    Trigger the emergency messaging system.
    """
    latitude, longitude = get_gps_location()
    if latitude and longitude:
        send_emergency_sms(latitude, longitude)
    else:
        print("Failed to retrieve GPS location.")

def display_ui():
    """
    Display a simple text-based UI for the app.
    """
    print("===== Emergency App =====")
    print("1. Check Sensor Status")
    print("2. Send Test Emergency Message")
    print("3. Start Collision Detection")
    print("4. Exit")

    choice = input("Enter your choice: ")
    if choice == "1":
        droid.startSensingTimed(1, 250)
        print("Checking sensor status...")
        accel_data = droid.sensorsReadAccelerometer().result
        if accel_data:
            print(f"Accelerometer Data: X={accel_data[0]}, Y={accel_data[1]}, Z={accel_data[2]}")
        else:
            print("No accelerometer data available.")
    elif choice == "2":
        print("Sending test emergency message...")
        latitude, longitude = get_gps_location()
        if latitude and longitude:
            send_emergency_sms(latitude, longitude)
    elif choice == "3":
        print("Starting collision detection...")
        detect_collision()
    elif choice == "4":
        print("Exiting...")
        exit()
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    display_ui()