import os
from datetime import datetime, timedelta
from calc import MODE_SUNRISE, MODE_NOON, MODE_SUNSET 

# Define your target path here
TARGET_DIRECTORY='/path/to/your/photos/'
# Define command to be executed
COMMAND = "echo \"raspistill -o {0:s}/{1:%Y}{1:%m}{1:%d}-{2}.jpg -t 1 -n\" | at {1:%H}:{1:%M}"
# Define your coordinates 
LONGITUDE=25.0
LATITUDE=60.0
# Define event to be observed
MODE = MODE_SUNSET
# Define settings for generating commands
START_OFFSET_MINUTES = -10
END_OFFSET_MINUTES = 10
TIME_INTERVAL_MINUTES = 1

def commands(dt:datetime) -> str:
    """
    Generator function to generate commands to be executed.
    Modify this function if you want to run additional commands 
    or to use different logic.
    """
    # As example, add current year to target direcory
    target = os.path.join(TARGET_DIRECTORY, "{:%Y}".format(dt))
    # Generate command for creating directory
    # This is here for example if you want to
    # create separate directory for each day.
    yield "mkdir -p {}".format(target)
    for i, dt in enumerate(intervals(dt)):
        # Generate command for taking picture
        yield COMMAND.format(target, dt, i)

def intervals(dt:datetime) -> datetime:
    """
    Generator function to generate time intervals for commands.
    Modify this function if you want to use different logic for time intervals.
    """
    t = dt + timedelta(minutes=START_OFFSET_MINUTES)       # Start time 
    end = dt + timedelta(minutes=END_OFFSET_MINUTES)       # End time
    while t < end:
        t = t + timedelta(minutes=TIME_INTERVAL_MINUTES)   # Time interval
        yield t
