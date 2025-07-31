from sleep_detector import SleepDetector
from sleep_database import SleepDatabase


# Initializes sleep database
sleep_database = SleepDatabase()
"""
Uncomment each of the 2 following method calls to display sleep trends/info from database
"""
#sleep_database.most_common_sleep_hour()
#sleep_database.plot_sleep_trend()

# Initializes sleep detector
sleep_detector = SleepDetector(
        video_path=0, # Change number for video path depending on intended webcam
        ear_threshold=0.24, # Calibration for eye detection
        consec_frames=90, # Approximately 3 seconds for sleep
        asleep=False,
        database=sleep_database # Passes the already created database connection to be used within the SleepDetector class
    )
sleep_detector.process_video() # Initializes video capture

sleep_database.close_connection() # Closes database connection