import serial
import time

class MicroConnection:
    """
    A class that makes use of PySerial in order to give commands to the Adafruit microcontroller
    """
    
    # Initializes MicroConnection
    def __init__(self):
        """
        Initializes the MicroConnection object

        Establishes a serial connection to the Adafruit microcontroller using the specified COM port

        :return None
        """
        # Replace with your Metro's actual COM port (Default is normally 'COM5')
        self.ser = serial.Serial('YOUR_COM_PORT', 115200, timeout=1) # Opens connection to serial port
        time.sleep(2)  # Wait for the board to reset after opening serial port


    # Communicates to the microcontroller to warn the driver falling asleep using LED, buzzer, and servo
    def sleep_warning(self):
        """
        Writes info 1/0 (ON/OFF) to the Adafruit microcontroller's code.py file in order to control LED, buzzer, and servo

        Acts as a warning for a person falling asleep while driving

        :return None
        """
        self.ser.write(b'1')  # Send '1' to turn LED, buzzer, and servo ON
        time.sleep(5) # Buzzer/light stays on for 5 seconds
        self.ser.write(b'0')  # Send '0' to turn LED, buzzer, and servo OFF