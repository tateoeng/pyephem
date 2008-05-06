#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob, os.path, re, traceback, unittest
from datetime import datetime
from time import strptime
import ephem

# Read an ephemeris from the JPL, and confirm that PyEphem returns the
# same measurements to within one arcsecond of accuracy.

angle_fudge = ephem.degrees('0:00:02')
size_fudge = 0.1

def cleanup(s):
    return s.strip().replace(' ', ':')

class JPLDatum(object):
    pass

class JPLTest(unittest.TestCase):

    def runTest(self):
        if not hasattr(self, 'path'):
            return

        in_data = False

        c=0
        for line in open(self.path):

            if line.startswith('Target body name:'):
                name = line.split()[3]
                if not hasattr(ephem, name):
                    raise ValueError('ephem lacks a body named %r' % name)
                body_class = getattr(ephem, name)
                body = body_class()

            elif line.startswith('$$SOE'):
                in_data = True

            elif line.startswith('$$EOE'):
                in_data = False

            elif in_data:
                date = datetime.strptime(line[1:18], '%Y-%b-%d %H:%M')
                body.compute(date)

                jpl = JPLDatum()
                jpl.a_ra = ephem.hours(cleanup(line[23:34]))
                jpl.a_dec = ephem.degrees(cleanup(line[35:46]))
                jpl.size = float(line[71:])

                for attr, fudge in (('a_ra', angle_fudge),
                                    ('a_dec', angle_fudge),
                                    ('size', size_fudge)):
                    try:
                        body_value = getattr(body, attr)
                    except AttributeError: # moons lack "size"
                        continue
                    jpl_value = getattr(jpl, attr)
                    if abs(body_value - jpl_value) > fudge:
                        raise ValueError('at %s, %s returns %s=%s'
                                         ' but JPL insists that %s=%s' %
                                         (date, body.name, attr, body_value,
                                          attr, jpl_value))

re, traceback, datetime, strptime, ephem

def additional_tests():
    suite = unittest.TestSuite()
    for path in glob.glob(os.path.dirname(__file__) + '/jpl/*.txt'):
        case = JPLTest()
        case.path = path
        suite.addTest(case)
    return suite

if __name__ == '__main__':
    unittest.main()