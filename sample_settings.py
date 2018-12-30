import os
from datetime import datetime, timedelta
from calc import EVENT_SUNRISE, EVENT_NOON, EVENT_SUNSET 

# Define your target path here
TARGET_DIRECTORY = '/path/to/your/photos/'
# Define command to be executed
COMMAND = "echo \"raspistill -o {0:s}/{1:%Y}{1:%m}{1:%d}{2:+d}.jpg -t 1 -n\" | at {1:%H}:{1:%M}"
# Define your coordinates 
LONGITUDE = 25.0
LATITUDE = 60.0
# Define event to be observed
EVENT = EVENT_SUNSET
# Define settings for generating commands
START_OFFSET_MINUTES = -10
END_OFFSET_MINUTES = 10
TIME_INTERVAL_MINUTES = 1

def commands(event_time:datetime) -> str:
    """
    Generator function to generate commands to be executed.
    Modify this function if you want to run additional commands 
    or to use different logic.
    """
    # As example, add current year to target direcory
    target = os.path.join(TARGET_DIRECTORY, "{:%Y}".format(event_time))
    # Generate command for creating directory
    # This is here for example if you want to
    # create separate directory for each day.
    yield "mkdir -p {}".format(target)
    # Generate command for each time interval
    for t in intervals(event_time):
        # Calculate time offset in seconds
        offset = int((t-event_time).total_seconds()/60)
        # Generate command for taking picture
        yield COMMAND.format(target, t, offset)

def intervals(event_time:datetime) -> datetime:
    """
    Generator function to generate time intervals for commands.
    Modify this function if you want to use different logic for time intervals.
    """
    # Start time 
    t = event_time + timedelta(minutes=START_OFFSET_MINUTES)
    # End time
    end_time = event_time + timedelta(minutes=END_OFFSET_MINUTES)
    while t < end_time:
        # Time interval
        t = t + timedelta(minutes=TIME_INTERVAL_MINUTES)
        yield t
