import io
import socket
import time
from PIL import Image
import picamera

# --- Configuration ---
# IMPORTANT: Replace with your ESP32's IP address
ESP32_IP = "192.168.1.123" 
ESP32_PORT = 8888
FRAME_RATE = 15 # Target frames per second
OLED_WIDTH = 128
OLED_HEIGHT = 64

# Setup the UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"Streaming to {ESP32_IP}:{ESP32_PORT} at {FRAME_RATE} FPS...")

with picamera.PiCamera() as camera:
    camera.resolution = (OLED_WIDTH, OLED_HEIGHT)
    camera.framerate = FRAME_RATE
    time.sleep(2)  # Give the camera time to warm up

    stream = io.BytesIO()
    
    # Use capture_continuous for efficient streaming
    for foo in camera.capture_continuous(stream, format='jpeg', use_video_port=True):
        stream.seek(0)
        
        # Open the image with Pillow
        image = Image.open(stream)
        
        # Convert the image to 1-bit black and white with dithering
        # '1' mode uses Floyd-Steinberg dithering by default
        bw_image = image.convert('1')
        
        # Get the raw byte buffer
        buffer = bw_image.tobytes()
        
        # Send the buffer over UDP
        sock.sendto(buffer, (ESP32_IP, ESP32_PORT))
        
        # Reset the stream for the next frame
        stream.seek(0)
        stream.truncate()
        
        # Optional: Add a small delay to control the frame rate more precisely
        # time.sleep(1 / FRAME_RATE)

print("Streaming stopped.")
