#!/usr/bin/python
import urllib2
import re
import ephem
import datetime
import math

day_hours = ['Hare', 'Dragon', 'Serpent', 'Horse', 'Ram', 'Monkey']
night_hours = ['Cock', 'Dog', 'Boar', 'Rat', 'Ox', 'Tiger']

def hour_to_strike(hour):
    if hour < 3:
        return 6 - hour
    else:
        return 12 - hour

def calc_jtt(start, end):
    now = datetime.datetime.now()
    l_end = ephem.localtime(end)
    l_start = ephem.localtime(start)
    hlen = ((l_end - l_start)/6).total_seconds()
    tnow = (now - l_start).total_seconds()
    return tnow/hlen

if 0:
    print "Start at %s, end at %s" % (l_start.ctime(), l_end.ctime())
    print "It is %s now" % now.ctime()
    print "It is %f of time of day now" % ((now - l_start).total_seconds()/hlen.total_seconds())

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

def main():
    obs = ephem.Observer()
    (lat, lng) = latlong()
    obs.lat = lat
    obs.long = lng
    obs.horizon = '-6' # civilian
    sun = ephem.Sun()
    prev_rise = obs.previous_rising(sun)
    prev_set = obs.previous_setting(sun)
    if prev_set > prev_rise: # night
        print "It is night now"
        is_night = 1 
        next_rise = obs.next_rising(sun)
        hour = calc_jtt(prev_set, next_rise)
        hnames = night_hours
    else:
        print "It is day now"
        is_night = 0
        next_set = obs.next_setting(sun)
        hour = calc_jtt(prev_rise, next_set)
        hnames = day_hours
    (frac, hour) = math.modf(hour)
    hour = int(hour)
    print "It is hour of %s (%d strikes, %d%%) now" % (hnames[hour+1],
        hour_to_strike(hour), frac*100)

if __name__ == "__main__":
    main()

