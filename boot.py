import usb_cdc

# Sets up USB CDC to let microcontroller act as a USB serial device
usb_cdc.enable(console=False, data=True) # Disables REPL and enables an extra port to receive/send data