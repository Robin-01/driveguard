import psycopg2
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


class SleepDatabase:
    """
    A class that connects to a local PostgreSQL database. Allowing for input of timestamps and generation of trend data visuals
    """

    # Initialize SleepDatabase
    def __init__(self):
        """
        Initializes the SleepDatabase object

        Establishes a connection to the PostgreSQL database and creates a table if not already available

        :return None
        """
        # The following connection variables are dependent on your local machine and can be found in pg Admin for Postgresql - PLEASE CHANGE ACCORDINGLY
        self.connection = psycopg2.connect(
            host="localhost", 
            dbname="DriveGuard", 
            user="your_username", 
            password="your_password", 
            port=5432
            )
        
        self.cursor = self.connection.cursor() # Connect to database cursor for executable actions
        self.create_table()


    # Creates a table in the PostgreSQL database if there is none existing
    def create_table(self):
        """
        Executes creation of a "driver_asleep" table in the PostgreSQL database

        Table consists of 1 attribute: Timestamp

        :return None
        """
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS driver (
                    driver_asleep TIMESTAMP PRIMARY KEY
                    );
                    """)


    # Takes a timestamp of when the person fell asleep and uploads it onto the database
    def take_sleep_timestamp(self):
        """
        Takes a timestamp of the person falling asleep and insterts into the PostgreSQL database

        Uses datetime to store the timestamp and pushes the changes

        :return None
        """
        timestamp = datetime.now() # Stores current timestamp

        self.cursor.execute("""INSERT INTO driver (driver_asleep) VALUES
                (%s)
                """, (timestamp,))
        self.connection.commit() # Pushes changes to database


    # Returns the most common hour that a person falls asleep and displays it in a window
    def most_common_sleep_hour(self):
        """
        Parses through the database to calculate the most frequent sleep hour

        Generates a matplot visualization showing both hour and the frequency

        :return None
        """
        self.cursor.execute("""SELECT EXTRACT(HOUR FROM driver_asleep) AS sleep_hour, COUNT(*) AS frequency
                    FROM driver
                    GROUP BY sleep_hour
                    ORDER BY frequency DESC
                    LIMIT 1;
                    """)
        result = self.cursor.fetchone() # Assigns a tuple with the most common sleep hour and the frequency of the hour
        
        if result: # Checks if the query was successful
            # Unpacking the tuple for the hour and the frequency
            sleep_hour = result[0]
            frequency = result[1]
            
            # Create matplotlib window to display the result
            plt.figure(figsize=(8, 6))
            plt.text(0.5, 0.6, f"Most Common Sleep Hour: {int(sleep_hour):02d}:00", 
                    fontsize=24, ha='center', va='center', weight='bold')
            plt.text(0.5, 0.4, f"Frequency: {frequency} occurrences", 
                    fontsize=16, ha='center', va='center')
            plt.xlim(0, 1)
            plt.ylim(0, 1)
            plt.axis('off')
            plt.title("Driver Sleep Analysis", fontsize=18, weight='bold', pad=20)
            plt.show()
        else:
            # Create matplotlib window in case of no data
            plt.figure(figsize=(8, 6))
            plt.text(0.5, 0.5, "No sleep records found", 
                    fontsize=20, ha='center', va='center', color='red')
            plt.xlim(0, 1)
            plt.ylim(0, 1)
            plt.axis('off')
            plt.title("Driver Sleep Analysis", fontsize=18, weight='bold', pad=20)
            plt.show() 


    # Creates a plot of sleep trends
    def plot_sleep_trend(self):
        """
        Creates and displays a bar chart with a trendline to show driver sleep trends throughout a day

        Based on military time

        :return None
        """
        # Fetch all timestamps
        self.cursor.execute("""
            SELECT driver_asleep FROM driver;
        """)
        rows = self.cursor.fetchall()

        # In case of no data to be displayed on a chart
        if not rows:
            print("No sleep data to display.")
            return

        # Prepare DataFrame and round timestamps to nearest hour
        df = pd.DataFrame(rows, columns=['timestamp'])
        df['hour'] = df['timestamp'].dt.floor('H')  # 'H' = hour

        # Count frequency per hour
        sleep_counts = df['hour'].value_counts().sort_index()

        # X = actual datetime labels for bars
        x_labels = sleep_counts.index
        y = sleep_counts.values

        # Convert datetime to numerical (in hours) for trendline fitting
        hours_since_start = (x_labels - x_labels[0]).total_seconds() / 3600

        # Plot bar chart
        plt.figure(figsize=(14, 6))
        plt.bar(x_labels, y, width=0.03, color='skyblue', edgecolor='black', label="Sleep Count (per hour)")

        # Plot trendline if enough data
        if len(x_labels) >= 3:
            z = np.polyfit(hours_since_start, y, 2)
            p = np.poly1d(z)
            plt.plot(x_labels, p(hours_since_start), "r--", label="Trendline")

        # Formatting
        plt.title("Driver Sleep Frequency by Hour")
        plt.xlabel("Time")
        plt.ylabel("Sleep Occurrences")
        
        # Format x-axis to show hours properly
        from matplotlib.dates import DateFormatter, HourLocator
        plt.gca().xaxis.set_major_locator(HourLocator(interval=1))  # Show every hour
        plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M'))  # Format as HH:MM
        
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()


    # Closes connection to database
    def close_connection(self):
        """
        Closes the connection to the PostgreSQL database

        :return None
        """
        self.cursor.close()
        self.connection.close()