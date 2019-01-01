# Raspberry Pi - Sunset Photo Scheduler
The intent of this project is to schedule Raspberry Pi to take photos of sunset every day so that sun is always at specific elevation from the horizon. When executed, the script schedules taking photos for today's sunrise, noon or sunset using _at_ command. Actual behavior is defined in settings. The [sample settings](https://github.com/heikkileivo/raspi-sunset-scheduler/blob/master/sample_settings.py) show how to use this script with [raspistill](https://www.raspberrypi.org/documentation/usage/camera/raspicam/raspistill.md), but you can easily modify the settings to use some other tool to take the pictures.
  
By default the resulting images are named so that the file name indicates the time offset in minutes relative to the event. For example, if the event being photographed is sunset, images name `20181229-10.jpg` and `20181229+10.jpg` have been taken 10 minutes before and 10 minutes after calculated sunset, respectively. This makes it easy to list or collect all images with same time offset to the event, eg. `ls /path/to/images/*-10.jpg` to list all images taken 10 minutes before calculated sunset.

## Quick instructions
Read the detailed instructions below to set up the script before using. To show help for command line, run the script with -h parameter: 
```bash
(sunset) ~/raspi-sunset-scheduler $ ./sunset.py -h
```
To show time for today's sunrise, start the script with `show-time` command: 
```bash
(sunset) ~/raspi-sunset-scheduler $ ./sunset.py show-time --event sunrise
Local sunset is at 2018-12-30 15:10:31.239491+02:00
```
Valid values for `--event` argument are `sunrise`, `noon`and `sunset`.

To list commands for scheduling photographs, run the script with `run-commands` argument. By default the commands are not executed, so you can easily verify correct behavior:

```bash

(sunset) ~/raspi-sunset-scheduler $ ./sunset.py run-commands
mkdir -p ~/photos/sunset/2018
echo "raspistill -o ~/photos/sunset/2018/20181229-3.jpg -t 1 -n" | at 14:40
echo "raspistill -o ~/photos/sunset/2018/20181229-2.jpg -t 1 -n" | at 14:41
echo "raspistill -o ~/photos/sunset/2018/20181229-1.jpg -t 1 -n" | at 14:42
echo "raspistill -o ~/photos/sunset/2018/20181229+0.jpg -t 1 -n" | at 14:43
echo "raspistill -o ~/photos/sunset/2018/20181229+1.jpg -t 1 -n" | at 14:44
echo "raspistill -o ~/photos/sunset/2018/20181229+2.jpg -t 1 -n" | at 14:45
```
To actually execute the commands and schedule them to be executed, use the `--execute` parameter: 
```bash
(sunset) ~/sunset $ ./sunset.py run-commands --execute`
```
To schedule taking photos each day, run sunset.py daily using cron.

## Background
We relocated recently to a house which has a nice view to west, so every now and then we see a nice sunset in the evening. It is interesting to see the movement of the sun as time passes: during equinoxes the sun sets directly to west and during winter and summer solstices to southwest and northwest, respectively. It would be nice to take a photo of the sunset whenever it is not cloudy, but unfortunately it is not possible to be at home every sunny evening.

It is quite trivial to setup camera so that you can get a nice picture of [analemma](https://www.google.com/search?q=analemma&source=lnms&tbm=isch): just take picture at fixed time of day and stack the collected photos to show the annual movement of the sun in the sky. But what if you would like to take photo every day when sun is at specific elevation from horizon, such as just before sunset? What would the stacked-up photo look like? Some kind of horizontal analemma? How to schedule taking such pictures eg. using Raspberry Pi? I had find it out and came up with this script.

### Sunrise equation
The code works by utilizing the sunrise equation described in [wikipedia](https://en.m.wikipedia.org/wiki/Sunrise_equation). I do not fully understand how the equation works, but it seems to work as intended, giving credible times for sunrise, noon and sunset. You can compare the [implementation](https://github.com/heikkileivo/raspi-sunset-scheduler/blob/master/calc.py) to the equations in the wikipedia page - please let me know if you find any errors.

### Scheduling commands
Taking pictures is scheduled using _at_ command in linux. To schedule taking photo in an onliner, one can use the following command:

```bash
~/ $ echo "raspistill -o foo.jpg" | at 14:00
```
If you want to take a photo of sunset, one obvious problem arises: you usually want to take photos _before_ actual sunset, otherwise there is nothing much to see in the photos. Therefore the picture should actually be taken at specific offset relative to the observed event, eg. after sunrise or before sunset. To make it easier to find the best time offset, the script can be configured to take multiple photos with specific intervals, by default one minute. You can then look at the resulting images and collect the ones with same time offset, or change the settings to take pictures with narrower time window.

### Create time-lapse video
You can create a time-lapse video from the images using [ffmpg](https://trac.ffmpeg.org/wiki/Slideshow). To make it easier you can copy or rename images with same time offset to sequential filenames in ascending order. I will add a command line argument to help this. 


## Instructions
### Clone repository and create settings file


```bash
~/ $ git clone git@github.com:heikkileivo/raspi-sunset-scheduler.git
~/ $ cd raspi-sunset-scheduler
~/raspi-sunset-scheduler $ cp sample_settings.py settings.py
```

Edit _settings.py_ with your favourite editor and and fill in your local coordinates etc. as commented out in sample values.

### Install pre-requirements
Commands are scheduled using at command in linux, so it needs to be installed first.


```bash

~/raspi-sunset-scheduler $ sudo apt-get install at 
```

I recommend using [virtualenv](https://virtualenv.pypa.io/en/latest/) so you don't need to install dependent python libraries system-wide. 


```bash

~/raspi-sunset-scheduler $ sudo pip install virtualenv
```

Create a new virtual environment for sunset.py using __python 3__ and activate it, for example:


```bash

~/raspi-sunset-scheduler $ virtualenv -p python3 ~/virtualenvs/sunset
~/raspi-sunset-scheduler $ source ~/virtualenvs/sunset/bin/activate
(sunset) ~/raspi-sunset-scheduler $
```

Later, if you need to exit your virtual environment, use `deactivate` command:


```bash

(sunset) ~/raspi-sunset-scheduler $ deactivate
~/sunset $ 
```

Install required libraries:


```bash

(sunset) ~/raspi-sunset-scheduler $ pip install -r requirements.txt 
```

Now you are ready to start taking pictures. To preview commands to be scheduled for today start the script using `run-commands` argument:  
  
  
```bash

(sunset) ~/raspi-sunset-scheduler $ ./sunset.py run-commands
```

To schedule the commands to be actually executed, add `--execute` argument:


```bash
(sunset) ~/sunset $ ./sunset.py run-commands --execute
```

Now your raspbery pi is scheduled to take pictures as specified in settings - for single time. To take pictures every day, you can use [cron](https://linuxconfig.org/linux-crontab-reference-guide) to run _sunset.py_ every day. Run `crontab -e` to edit your crontab, and add following line taking care to get your paths correct:


```
0 8 * * * /home/pi/virtualenvs/sunset/bin/python /home/pi/sunset/sunset.py run-commands --execute
```

Note that the second parameter (here 8) specifies the hour on which the script is executed. If you intend to take pictures of sunrise, make sure you run the script before sunrise, otherwise the pictures will be taken on next day! 
