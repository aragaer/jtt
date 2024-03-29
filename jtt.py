#!/usr/bin/python
import urllib2
import re
import ephem
import math
import datetime

day_hours = ['Hare', 'Dragon', 'Serpent', 'Horse', 'Ram', 'Monkey']
night_hours = ['Cock', 'Dog', 'Boar', 'Rat', 'Ox', 'Tiger']

hours = {}
for count in range(0,6):
    hours[day_hours[count]] = (count, 0)
for count in range(0,6):
    hours[night_hours[count]] = (count, 1)

def hour_to_strike(hour):
    if hour < 3:
        return 6 - hour
    else:
        return 12 - hour

def calc_jtt(start, end, now):
    now = now.datetime()
    end = end.datetime()
    start = start.datetime()
    hlen = (end - start).seconds/6.0
    tnow = (now - start).seconds

    return tnow/hlen

def calc_rev_jtt(start, end, num, frac):
    start = start.datetime()
    end = end.datetime()
    hlen = (end - start).seconds/6.0
    tnow = int(hlen*(num + frac))

    return ephem.Date(start + datetime.timedelta(seconds=tnow))

def time_to_jtt(time = None, obs = None):
    if obs is None:
        obs = l_obs
    if time is None:
        time = datetime.datetime.utcnow()
    t_obs = ephem.Observer()
    t_obs.lat = obs.lat
    t_obs.lon = obs.lon
    t_obs.horizon = obs.horizon
    t_obs.date = ephem.Date(time)
    sun = ephem.Sun()
    prev_rise = t_obs.previous_rising(sun)
    prev_set = t_obs.previous_setting(sun)
    is_night = prev_set > prev_rise
    if is_night: # night
        print "It is night now"
        next_rise = t_obs.next_rising(sun)
        hour = calc_jtt(prev_set, next_rise, t_obs.date)
    else:
        print "It is day now"
        next_set = t_obs.next_setting(sun)
        hour = calc_jtt(prev_rise, next_set, t_obs.date)
    (frac, hour) = math.modf(hour)
    return (frac, int(hour), is_night)

def jtt_to_time(hour_str, frac = 0, date = None, obs = None):
    if obs is None:
        obs = l_obs
    if date is None:
        date = datetime.datetime.now().date()
    else:
        date = date.date()
    t_obs = ephem.Observer()
    t_obs.lat = obs.lat
    t_obs.lon = obs.lon
    t_obs.horizon = obs.horizon
    t_obs.date = ephem.Date(date)
    sun = ephem.Sun()

#    print "jtt to time for hour %s (%f) date %s " % (hour_str, frac, date.strftime("%d %h %Y"))
#    print "We're dancing from time %s" % date.strftime("%H:%M:%S") # should be 00:00:00
    (hour, is_night) = hours[hour_str]
    if is_night:
        if hour < 3: # evening, move to next midnight
            t_obs.date = ephem.Date(date + datetime.timedelta(days=1))
        next_rise = t_obs.next_rising(sun)
        prev_set = t_obs.previous_setting(sun)
        result = calc_rev_jtt(prev_set, next_rise, hour, frac)
    else:
        prev_rise = t_obs.next_rising(sun)
        next_set = t_obs.next_setting(sun)
        result = calc_rev_jtt(prev_rise, next_set, hour, frac)

    return ephem.localtime(result)

def latlong():
    data = urllib2.urlopen("http://j.maxmind.com/app/geoip.js").readlines()
    for line in data:
        m = re.search("latitude.*'(.*)'", line)
        if (m):
            latitude = m.group(1)
        m = re.search("longitude.*'(.*)'", line)
        if (m):
            longitude = m.group(1)
    return (latitude, longitude);

def init_local():
    global l_obs
    l_obs = ephem.Observer()
    (lat, lon) = latlong()
    l_obs.lat = lat
    l_obs.lon = lon
    l_obs.horizon = '-0.8333'

(alarm_hour, alarm_frac) = ("Tiger", 0)
def alarm():
    now = datetime.datetime.now()
    tomorrow = now + datetime.timedelta(days=1)
    sunrise = jtt_to_time("Hare", 0, now)
    if now < sunrise:
        day = now
    else:
        day = tomorrow
    alarm = jtt_to_time(alarm_hour, alarm_frac, day)
    print "On day %s in hour of %s the time is %s" % (day.strftime("%d %h %Y"), alarm_hour, alarm.strftime("%H:%M:%S"))

def main():
    (frac, hour, is_night) = time_to_jtt()
    hnames = night_hours if is_night else day_hours
    print "It is hour of %s (%d strikes, %d%%) now" % (hnames[hour],
        hour_to_strike(hour), frac*100)

    alarm()

init_local()
if __name__ == "__main__":
    main()

