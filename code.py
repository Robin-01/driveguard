import board
import digitalio
import time
import usb_cdc
import pwmio

# Set up LEDs
led = digitalio.DigitalInOut(board.D3)
led.direction = digitalio.Direction.OUTPUT

# Set up buzzer
buzzer = pwmio.PWMOut(board.D2, duty_cycle=0, frequency=2000, variable_frequency=True)

# Set up servo
servo = pwmio.PWMOut(board.D4, duty_cycle = 0, frequency=50)

# Set up reference to serial channel
usb = usb_cdc.data


# Converts angle to PWM duty cycle for the servo motor
def angle_to_duty_cycle(angle):
    # """
    # Converts angle to PWM duty cycle for the servo motor

    # :param int angle: the angle of the servo motor

    # :return int: the corresponding duty cycle value for the angle
    # """
    min_duty = 2000    # corresponds to 0 degrees
    max_duty = 10000   # corresponds to 180 degrees
    return int(min_duty + (angle / 180) * (max_duty - min_duty)) # Calculate duty cycle between the min and max


while True:
    if usb.in_waiting > 0: # Check for data 
        data = usb.read(1)
        if data: # Checks if data is received
            if data == b'1': # Turn everything on
                led.value = True

                buzzer.frequency = 2000
                buzzer.duty_cycle = 60000
                
                # Sweeps servo motor back and forth
                for angle in range(0, 181, 10):
                    servo.duty_cycle = angle_to_duty_cycle(angle)
                    time.sleep(0.02)
                for angle in range(180, -1, -10):
                    servo.duty_cycle = angle_to_duty_cycle(angle)
                    time.sleep(0.02)

                # Release servo position/torque
                servo.duty_cycle = 0
                
            elif data == b'0': # Turn everything off
                led.value = False
                buzzer.duty_cycle = 0
                servo.duty_cycle = 0

    time.sleep(0.05) # Delay for processing