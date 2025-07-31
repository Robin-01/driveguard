import usb_cdc #this is a library for CircuitPython which runs on the Adafruit Microcontroller
# it will show it as a problem because VSCode doesn't recognize the library since it is for CircuitPython and only runs on the Microcontroller itself.

# Sets up USB CDC to let microcontroller act as a USB serial device
usb_cdc.enable(console=False, data=True) # Disables REPL and enables an extra port to receive/send data