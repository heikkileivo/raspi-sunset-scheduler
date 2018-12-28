#!/usr/bin/env python
import logging
from datetime import datetime, timedelta
import julian
from math import floor, degrees, radians, sin, cos, asin, acos
from pytz import timezone
import tzlocal

LOG_FORMAT="%(message)s"
# Equivalent Julian year of Julian days for 2000, 1, 1.5.
EPOCH = 2451545.0   
#Fractional Julian Day for leap seconds and terrestrial time.
LEAP = 0.0008       
from settings import LONGITUDE
from settings import LATITUDE
logger = logging.getLogger(__name__)

def julian_day(dt:datetime) -> float:
    """
    Return current julian day.
    """
    j = julian.to_jd(dt, fmt='jd')

    return floor(j) - EPOCH + LEAP 

def mean_solar_noon(dt:datetime) -> float:
    """
    Return julian day of mean solar noon.
    """
    n = julian_day(dt)
    return n - LONGITUDE/360.0

def solar_mean_anomaly(dt:datetime) -> float:
    """
    Return solar mean anomaly in degrees.
    """
    jstar = mean_solar_noon(dt)
    return (357.5291 + 0.98560028 * jstar) % 360.0
 
def equation_of_center(dt:datetime) -> float:
    """
    Return equation of center in degrees.
    """
    m = radians(solar_mean_anomaly(dt))
    return 1.9148*sin(m) + 0.02*sin(2*m) + 0.0003*sin(3*m)

def ecliptic_longitude(dt:datetime) -> float:
    """
    Return ecliptic longitude in degrees.
    """
    m = solar_mean_anomaly(dt)
    c = equation_of_center(dt)
    return (m + c + 180.0 + 102.9372) % 360.0

def solar_transit(dt:datetime) -> float:
    """
    Return solar transit as julian date.
    """
    jstar = mean_solar_noon(dt)
    m = radians(solar_mean_anomaly(dt))
    l = radians(ecliptic_longitude(dt)) 

    return EPOCH + jstar + 0.0053*sin(m) - 0.0069*sin(2*l)

def declination_of_sun(dt:datetime) -> float:
    """
    Return declination of sun in degrees.
    """
    l = ecliptic_longitude(dt)
    d = sin(radians(l)) * sin(radians(23.44))
    return degrees(asin(d))

def hour_angle(dt:datetime) -> float:
    """
    Return hour angle in degrees.
    """
    d = radians(declination_of_sun(dt))
    phi = radians(LATITUDE)
    w = (sin(radians(-0.83))-sin(phi)*sin(d))/(cos(phi)*cos(d))    
    return degrees(acos(w))

def sunset(dt:datetime) -> float:
    """
    Return julian date for sunset at specific date.
    """
    j = solar_transit(dt)
    return j + (hour_angle(dt) / 360.0)

def main():
    local_tz = tzlocal.get_localzone()
    dt = datetime.now()
    local = local_tz.localize(dt)
    utc = local.astimezone(timezone('UTC'))
    logger.info("Local={}, utc={}".format(local,utc))
    s = sunset(utc)
    utc = timezone('UTC').localize(julian.from_jd(s))
    local = utc.astimezone(local_tz)

    logger.info("Utc={}, Local={}".format(utc,local))


if __name__=='__main__':
    logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG)
    main()
