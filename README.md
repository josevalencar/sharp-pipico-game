# Distance Target Combo Game

This project consists of a game developed in Python using the Pygame library, controlled by a distance sensor (Sharp Infrared) connected to a Raspberry Pi Pico.

https://github.com/user-attachments/assets/b5c945fd-b056-463c-ac68-fbdcdc10387d

## Functionality

The game features a vertical bar where a target moves randomly. The player controls a marker that must be aligned with the target using the distance sensor.

- The sensor sends normalized values (0.0 to 1.0) via serial to the computer.
- The player must keep the marker inside the target area for a short period to score points.
- The game features a scoring system, hit counter, and streak counter.
- If the sensor is unavailable, it is possible to play using the keyboard arrow keys (fallback).

## Requirements

### Hardware
- Raspberry Pi Pico (or similar)
- Analog distance sensor (e.g., Sharp GP2Y0A41SK0F) or ultrasonic sensor
- USB cable for serial connection

### Software
- Python 3.11+
- Python libraries listed in `requirements.txt`
- MicroPython firmware installed on the Raspberry Pi Pico

## Installation

1. Clone this repository.
2. Create a virtual environment (optional but recommended):
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
3. Install dependencies:
   pip install -r requirements.txt

## Hardware Configuration (Raspberry Pi Pico)

1. Connect the sensor to the Pico.
   - For Sharp sensor (analog): Connect the output to pin GP26 (ADC0).
2. Open the `sharp.py` file (or the corresponding code for your sensor).
3. Use a MicroPython-compatible IDE (such as Thonny IDE).
4. Save the sensor code content inside the Pico as `main.py`. This ensures the script runs automatically when USB power is connected.

## Execution

1. Connect the Raspberry Pi Pico to the computer's USB port.
2. Verify the correct serial port in the `game.py` file (`SERIAL_PORT` variable).
   - macOS/Linux: usually `/dev/cu.usbmodem...` or `/dev/ttyACM...`
   - Windows: usually `COM3`, `COM4`, etc.
3. Run the game:
   python3 game.py

## Controls

- Distance Sensor: Move your hand or object in front of the sensor to control the marker height.
- Keyboard (only if the sensor fails):
  - Up Arrow: Move marker up.
  - Down Arrow: Move marker down.
- Menu/Game:
  - SPACE: Start game.
  - R: Restart game (on Game Over screen).
  - ESC: Return to menu.

## Project Structure

- game.py: Main game code (Pygame).
- sharp.py: MicroPython code for Raspberry Pi Pico (sensor reading).
- test_serial.py: Utility script to test serial communication and read raw data.
- requirements.txt: Project dependencies list.
