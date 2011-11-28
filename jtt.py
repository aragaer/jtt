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
    now = ephem.localtime(now)
    l_end = ephem.localtime(end)
    l_start = ephem.localtime(start)
    hlen = (l_end - l_start).seconds/6.0
    tnow = (now - l_start).seconds

#    print "Start at %s, end at %s" % (l_start.ctime(), l_end.ctime())
#    print "It is %s now" % now.ctime()
#    print "It is %f of time of day now" % ((now - l_start).seconds/hlen)

    return tnow/hlen

def calc_rev_jtt(start, end, num, frac):
    l_start = start.datetime()
    l_end = end.datetime()
    hlen = (l_end - l_start).seconds/6.0
    print "Hour length is", hlen, "seconds"
    for i in range (0,6):
        print "Hour %d - %s" % (i, ephem.Date(l_start + datetime.timedelta(seconds=int(hlen*i))))
    return l_start + datetime.timedelta(seconds=int(hlen*(num + frac)))

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

    print "jtt to time for hour %s (%f) date %s " % (hour_str, frac, date.strftime("%d %h %Y"))
#    print "We're dancing from time %s" % date.strftime("%H:%M:%S") # should be 00:00:00
    (hour, is_night) = hours[hour_str]
    if is_night and hour >= 3:      # it's in the morning
        next_rise = t_obs.next_rising(sun)
        prev_set = t_obs.previous_setting(sun)
        result = calc_rev_jtt(prev_set, next_rise, hour, frac)

    print result
    print "The result is %s" % result
    return result

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
    l_obs.horizon = '-6'

def main():
    (frac, hour, is_night) = time_to_jtt()
    hnames = night_hours if is_night else day_hours
    print "It is hour of %s (%d strikes, %d%%) now" % (hnames[hour],
        hour_to_strike(hour), frac*100)

    time = jtt_to_time("Tiger")
    print "On day %s in hour %s the time is %s" % (datetime.datetime.now().date(), "Tiger", time.strftime("%H:%M:%S"))

init_local()
if __name__ == "__main__":
    main()

