#!/usr/bin/env python
import logging
import os, sys
from datetime import datetime, timedelta
import julian
from math import degrees, radians, sin, cos, asin, acos
from pytz import timezone
import tzlocal
import argparse

MODE_NOON = 'noon'
MODE_SUNSET = 'sunset'
MODE_SUNRISE = 'sunrise'
MODES = [MODE_SUNRISE, MODE_NOON, MODE_SUNSET]

# Equivalent Julian year of Julian days for 2000, 1, 1.5.
EPOCH = 2451545.0   
#Fractional Julian Day for leap seconds and terrestrial time.
LEAP = 0.0008       

logger = logging.getLogger(__name__)

def _dt_to_utc(dt:datetime) -> datetime:
    """
    Return datetime converted to utc timezone.
    """
    local_tz = tzlocal.get_localzone()
    local_time = local_tz.localize(dt)
    return local_time.astimezone(timezone('UTC'))


def _julian_to_utc_dt(j:float) -> datetime:
    """
    Return julian date as datetime converted to local timezone.
    """
    return timezone('UTC').localize(julian.from_jd(j))

def _utc_to_local_dt(utc:datetime) -> datetime:
    """
    Return utc datetime converted to local timezone.
    """
    local_tz = tzlocal.get_localzone()
    return utc.astimezone(local_tz)


def _to_local(fn):
    def convert(self, local):
        utc = _dt_to_utc(local)
        j = fn(self, utc)
        utc = _julian_to_utc_dt(j)
        return _utc_to_local_dt(utc)
    return convert

class Suncalc(object):
    """
    Calculates time of sunrise and sunset using
    algorithm specified in Wikipedia. When reading the code
    you can follow the description of the algorithm in 
    the Wikipedia page.
    See: https://en.m.wikipedia.org/wiki/Sunrise_equation
    """
    def __init__(self, latitude, longitude, mode):
       """
       Create instance of sunset calculator.
       """
       self._latitude = latitude
       self._longitude = longitude
       self._mode = mode

    def _calculate_current_julian_day(self, dt:datetime) -> float:
        """
        Return current julian day.
        """
        j = round(julian.to_jd(dt)) 
        return j - EPOCH + LEAP 

    def _mean_solar_noon(self, dt:datetime) -> float:
        """
        Return julian day of mean solar noon.
        """
        n = self._calculate_current_julian_day(dt)
        return n - self._longitude / 360.0

    def _solar_mean_anomaly(self, dt:datetime) -> float:
        """
        Return solar mean anomaly in degrees.
        """
        jstar = self._mean_solar_noon(dt)
        return (357.5291 + 0.98560028 * jstar) % 360.0
 
    def _equation_of_center(self, dt:datetime) -> float:
        """
        Return equation of center in degrees.
        """
        m = radians(self._solar_mean_anomaly(dt))
        return 1.9148 * sin(m) + 0.02 * sin(2 * m) + 0.0003 * sin(3 * m)

    def _ecliptic_longitude(self, dt:datetime) -> float:
        """
        Return ecliptic longitude in degrees.
        """
        m = self._solar_mean_anomaly(dt)
        c = self._equation_of_center(dt)
        return (m + c + 180.0 + 102.9372) % 360.0

    def _solar_transit(self, dt:datetime) -> float:
        """
        Return solar transit as julian date.
        """
        jstar = self._mean_solar_noon(dt)
        m = radians(self._solar_mean_anomaly(dt))
        l = radians(self._ecliptic_longitude(dt)) 

        return EPOCH + jstar + 0.0053 * sin(m) - 0.0069 * sin(2 * l)

    def _declination_of_sun(self, dt:datetime) -> float:
        """
        Return declination of sun in degrees.
        """
        l = self._ecliptic_longitude(dt)
        d = sin(radians(l)) * sin(radians(23.44))
        return degrees(asin(d))

    def _hour_angle(self, dt:datetime) -> float:
        """
        Return hour angle in degrees.
        """
        d = radians(self._declination_of_sun(dt))
        phi = radians(self._latitude)
        w = (sin(radians(-0.83)) - sin(phi) * sin(d)) / (cos(phi) * cos(d))    
        return degrees(acos(w))

    def sunrise(self, dt:datetime) -> float:
        """
        Return julian date for sunrise at specific date.
        """
        j = self._solar_transit(dt)
        w = self._hour_angle(dt)
        return j - (w / 360.0)

    def sunset(self, dt:datetime) -> float:
        """
        Return julian date for sunset at specific date.
        """
        j = self._solar_transit(dt)
        w = self._hour_angle(dt)
        return j + (w / 360.0)

    def noon(self, dt:datetime) -> float:
        """
        Return julian date for sunset at specific date.
        """
        j = self._solar_transit(dt)
        return j 

    def local_value(self, dt:datetime) -> datetime:
        if self._mode == MODE_SUNRISE:
            return self.local_sunrise(dt)
        elif self._mode == MODE_SUNSET:
            return self.local_sunset(dt)
        else:
            return self.local_noon(dt)

    local_sunset = _to_local(sunset)
    local_sunrise = _to_local(sunrise)
    local_noon = _to_local(noon)


if __name__=='__main__':
    s = Suncalc(0,0)
    print(s.local_sunset(datetime.now()))
    print(s.local_sunrise(datetime.now()))
