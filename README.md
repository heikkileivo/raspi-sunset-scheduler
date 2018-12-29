# Sunset Calculator
The intent of this project is to schedule Raspberry Pi to take photos of sunset every day so that sun is always at specific elevation from the horizon. When executed, the script schedules taking photos for today's sunrise, noon or sunset using _at_ command. Actual behavior is defined in settings. The [sample settings](https://github.com/heikkileivo/sunset/blob/master/sample_settings.py) show how to use this script with [raspistill](https://www.raspberrypi.org/documentation/usage/camera/raspicam/raspistill.md), but you can easily modify the settings to use some other tool to take the pictures.
## Quick instructions
Read the detailed instructions below to set up the script before using. To show help for command line, run the script with -h parameter: `./sunset.py -h`. To show time for today's sunrise, start the script with `show-time` command: `./sunset.py show-time --event sunrise`. Valid values for `--event` argument are `sunrise`, `noon`and `sunset`.

To list commands for scheduling photographs, run the script with `run-commands` argument: `./sunset.py run-commands`. By default the commands are not executed, so you can easily verify correct behavior:


```bash

(sunset) pi@vadelma:~/sunsetcalculator $ ./sunset.py run-commands
mkdir -p ~/sunset/2018
echo "raspistill -o ~/sunset/2018/20181229-0.jpg -t 1 -n" | at 14:40
echo "raspistill -o ~/sunset/2018/20181229-1.jpg -t 1 -n" | at 14:41
echo "raspistill -o ~/sunset/2018/20181229-2.jpg -t 1 -n" | at 14:42
echo "raspistill -o ~/sunset/2018/20181229-3.jpg -t 1 -n" | at 14:43
echo "raspistill -o ~/sunset/2018/20181229-4.jpg -t 1 -n" | at 14:44
echo "raspistill -o ~/sunset/2018/20181229-5.jpg -t 1 -n" | at 14:45
```
To actually execute the commands and schedule them to be executed, use the `--execute` parameter: `./sunset.py run-commands --execute True`. To schedule taking photos each day, run sunset.py daily using cron.

## Background
We relocated recently to a house which has a nice view to west, so every now and then we see a nice sunset in the evening. It is interesting to see the movement of the sun as time passes: during equinoxes the sun sets directly to west and during winter and summer solstices to southwest and northwest, respectively. It would be nice to take a photo of the sunset whenever it is not cloudy, but unfortunately it is not possible to be at home every sunny evening.

It is quite trivial to setup camera so that you can get a nice picture of [analemma](https://www.google.com/search?q=analemma&source=lnms&tbm=isch): just take picture at fixed time of day and stack the collected photos to show the annual movement of the sun in the sky. But what if you would like to take photo every day when sun is at specific elevation from horizon, such as just before sunset? What would the stacked-up photo look like? Some kind of horizontal analemma? How to schedule taking such pictures eg. using Raspberry Pi? I had find it out and came up with this script.

### Sunrise equation
The code works by utilizing the sunrise equation described in [wikipedia](https://en.m.wikipedia.org/wiki/Sunrise_equation). I do not fully understand how the equation works, but it seems to work as intended, giving credible times for sunrise, noon and sunset. You can compare the [implementation](https://github.com/heikkileivo/sunset/blob/master/calc.py) to the equations in the wikipedia page - please let me know if you find any errors.


## Instructions
### Clone repository and create settings file


```bash

~/ $ git clone git@github.com:heikkileivo/sunset.git
~/ $ cd sunsetcalculator
~/sunsetcalculator $ cp sample_settings.py settings.py
```

Edit _settings.py_ with your favourite editor and and fill in your local coordinates etc. as commented out in sample values.

### Install pre-requirements
Commands are scheduled using at command in linux, so it needs to be installed first.


```bash

~/sunsetcalculator $ sudo apt-get install at 
```

I recommend using [virtualenv](https://virtualenv.pypa.io/en/latest/) so you don't need to install dependent python libraries systm-wide. 


```bash

~/sunsetcalculator $ sudo pip install virtualenv
```

Create a new virtual environment for sunset.py using __python 3__ and activate it, for example:


```bash

~/sunsetcalculator $ virtualenv -p python3 ~/virtualenvs/sunset
~/sunsetcalculator $ source ~/virtualenvs/sunset/bin/activate
(sunset) ~/sunsetcalculator $
```

Later, if you need to exit your virtual environment, use `deactivate` command:


```bash

(sunset) ~/sunsetcalculator $ deactivate
~/sunsetcalculator $ 
```

Install required libraries:


```bash

(sunset) ~/sunsetcalculator $ pip install -r requirements.txt 
```

Now you are ready to start taking pictures. To preview commands to be scheduled for today start the script using `run-commands` argument:  
  
  
```bash

(sunset) ~/sunsetcalculator $ ./sunset.py run-commands
```

To schedule the commands to be actually executed, add `--execute` argument:


```bash

(sunset) ~/sunsetcalculator $ ./sunset.py run-commands --execute True
```

Now your raspbery pi is scheduled to take pictures as specified in settings - for single time. To take pictures every day, you can use [cron](https://linuxconfig.org/linux-crontab-reference-guide) to run _sunset.py_ every day. Run `crontab -e` to edit your crontab, and add following line taking care to get your paths correct:


```

0 8 * * * /home/pi/virtualenvs/sunset/bin/python /home/pi/sunsetcalculator/sunset.py run-commands --execute True
```

Note that the second parameter (here 8) specifies the hour on which the script is executed. If you intend to take pictures of sunrise, make sure you run the script before sunrise, otherwise the pictures will be taken on next day! 
