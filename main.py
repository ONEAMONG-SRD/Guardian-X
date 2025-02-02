import androidhelper
import time
import threading
from collections import deque
import requests
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMPLEMENTOFDEFAULT"


# Initialize Android helper
droid = androidhelper.Android()

# Constants
COLLISION_THRESHOLD = 2.5  # Threshold for collision detection (in m/s²)
SMOOTHING_WINDOW_SIZE = 10  # Number of samples for moving average
EMERGENCY_CONTACT = "REPLACE WITH EMERGENCY CONTACT NUMBER"  # Replace with emergency contact number

# Moving average buffer
accel_history = deque(maxlen=SMOOTHING_WINDOW_SIZE)

# Global variables
collision_detected = False

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
    return None

def detect_collision():
    """
    Detect collisions using the accelerometer in the background.
    """
    global collision_detected
    while not collision_detected:
        droid.startSensingTimed(1, 250)  # Start accelerometer sensing (250ms delay)

        accel_data = droid.sensorsReadAccelerometer().result
        if accel_data:
            smoothed_data = smooth_acceleration(accel_data)
            if smoothed_data:
                x, y, z = smoothed_data
                total_acceleration = (x*2 + y2 + z*2) ** 0.5

                # Compare to gravity (9.8 m/s²) to detect significant changes
                if abs(total_acceleration - 9.8) > COLLISION_THRESHOLD:
                    collision_detected = True
                    droid.ttsSpeak("Crash detected!")  # TTS Alert
                    print(f"Crash detected! CID Escape!")
                    trigger_emergency_message()
                    break
        time.sleep(0.1)

def get_gps_location():
    """
    Retrieve the device's current GPS location.
    """
    droid.startLocating()
    time.sleep(2)  
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
    
    if lat and lon:
        return lat, lon
    else:
        return None, None

def send_emergency_sms(latitude, longitude):
    """
    Send an emergency SMS with the accident location.
    """
    emergency_message = f"Emergency! Accident detected at: Latitude = {latitude}, Longitude = {longitude}"

    # Fast2SMS API
    API_KEY = "REPLACE WITH FAST2SMS API KEY
    PHONE_NUMBER = "REPLACE WITH EMERGENCY CONTACT NUMBER"
    MESSAGE = emergency_message
    url = "https://www.fast2sms.com/dev/bulkV2"

    params = {
        "authorization": API_KEY,
        "message": MESSAGE,
        "language": "english",
        "route": "q",
        "numbers": PHONE_NUMBER,
    }

    response = requests.get(url, params=params)

def trigger_emergency_message():
    """
    Trigger the emergency messaging system.
    """
    latitude, longitude = get_gps_location()
    print(f"Crash detected at Latitude = {latitude}, Longitude = {longitude}")
    if latitude and longitude:
        send_emergency_sms(latitude, longitude)

def start_collision_detection():
    """
    Start collision detection in a background thread.
    """
    detection_thread = threading.Thread(target=detect_collision)
    detection_thread.start()

def send_test_emergency_message():
    """
    Send a test emergency message.
    """
    latitude, longitude = get_gps_location()
    if latitude and longitude:
        send_emergency_sms(latitude, longitude)
        droid.makeToast(f"Emergency message sent: Latitude = {latitude}, Longitude = {longitude}")

def exit_app():
    """
    Action for exit: Exit the app.
    """
    droid.makeToast("Exiting app...")
    droid.exit()

def handle_click(result):
    """
    Handle button clicks based on selection index
    """
    if result['item'] == 0:  # Button 1: Start Collision Detection
        start_collision_detection()
    elif result['item'] == 1:  # Button 2: Send Test Emergency Message
        send_test_emergency_message()
    elif result['item'] == 2:  # Button 3: Exit App
        exit_app()

def create_ui():
    """
    Create a simple UI with buttons.
    """
    droid.dialogCreateAlert("Emergency App")
    droid.dialogSetMessage("Choose an option to see the result")
    droid.dialogSetItems(["Start Collision Detection", "Send Test Emergency Message", "Exit"])
    # Show the dialog and handle the response
    response = droid.dialogShow().result
    while True:
        event = droid.eventWait().result
        if event['name'] == 'dialog':
            handle_click(event['data'])
            break

# Start the app
create_ui()