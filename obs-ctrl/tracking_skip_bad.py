#!/usr/bin/env python2.7

################################################################################
## This script is for tracking stuff with the Leuschner dish.
## Copyright (C) 2014  Isaac Domagalski: idomagalski@berkeley.edu
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

import os
import sys
import time
import coords
import getopt
import socket
import numpy as np
import cPickle as pickle

timefmt = '%Y-%m-%d-%H:%M'
latitude = 37.91934
longitude = -122.15385

# Usage function is defined before testing if one is on the ugastro network.
# This scipt will only work on that network, since it interfaces to hardware in
# the lab.
def usage(code):
    """
    Display help options and exit.
    """
    global timefmt
    print 'Usage:', os.path.basename(sys.argv[0]), '[options]'
    print 'Flags:'
    print '    -h: Print this help message and exit.'
    print '    -H: Skip resetting the telescope to the home position.'
    print '    -d: Enable debug mode (do not operate the dish).'
    print '    -g: Grid file to use for the tracking.'
    print '    -l: File containing the altitude limits.'
    print '    -t: Start time for observations (' + timefmt + ').'
    print '    -T: Stop time for observations (' + timefmt + ').'
    print '    -v: Enable verbose mode.'
    sys.exit(code)

# Verify that this script is being run on Leuschner.
if socket.getfqdn() != 'heiles.site':
    print 'ERROR: You cannot control the dish from this computer.'
    usage(1)

import dish

def grid_remaining(grid):
    """
    This function returns the number of points in a grid that still
    need to have data collected for them.
    """
    return sum(map(lambda r: len(filter(lambda b: not b, r[2])), grid))

def line2float(line):
    """
    This function converts a string representing the line of a file to
    a floating point number. The line of the file can either be in unix
    format, dos format, or doesn't have any line ending at all.
    """
    if line[-2:] == '\r\n':
        return float(line[:-2])
    elif line[-1] == '\n':
        return float(line[:-1])
    else:
        return float(line)

def run_tracker(leuschner, stop_time, filenames, verbose=False, debug=False):
    """
    This function loops over the grid and then returns the number of
    grid points that do not have data for them.
    """
    gridfile, trackfile, obsfile, alt_limits = filenames
    with open(gridfile) as pkl:
        grid = pickle.load(pkl)
    with open(trackfile) as pkl:
        status  = pickle.load(pkl)
    with open(obsfile) as pkl:
        obs_status = pickle.load(pkl)

    # Loop through the grid.
    for i in range(len(grid)):
        gal_b = grid[i][0]
        for j in range(len(grid[i][1])):
            # If the time has ran out, then return False (0)
            if stop_time != None and time.time() >= stop_time:
                return False

            # Continue if a spectrum already exists for this gridpoint
            if grid[i][2][j]:
                if debug or verbose:
                    print time.asctime()
                    print 'Spectrum exists. Moving to the next point.\n'
                time.sleep(0.025)
                continue

            # Write the coordinates that are being attempted.
            gal_l = grid[i][1][j]
            if debug or verbose:
                print time.asctime()
                print 'Moving to (l,b):',
                print '(' + str(gal_l) + ',' + str(gal_b) + ')\n'
            status['l'] = gal_l
            status['b'] = gal_b
            status['grid'] = (i,j)
            with open(trackfile, 'w') as pkl:
                pickle.dump(status, pkl)

            # Track each l/b point on the grid. The grid value is set to
            # whether or not a full spectrum was able to have been produced.
            # This function also sets the tracker
            grid[i][2][j] = track_lb(leuschner,
                                     gal_l,
                                     gal_b,
                                     filenames,
                                     verbose,
                                     debug)

            # Reload the status pickle.
            with open(trackfile) as pkl:
                status = pickle.load(pkl)

            # Update the grid
            if verbose and not debug:
                print time.asctime()
                print 'Updating the grid file.\n'

            # Don't edit the grid file when in debug mode
            if debug:
                grid[i][2][j] = False
            else:
                with open(gridfile, 'w') as pkl:
                    pickle.dump(grid, pkl)

            # Update the status to switching.
            status['status'] = 'switching'
            with open(trackfile, 'w') as pkl:
                pickle.dump(status, pkl)

            # Wait until the observer is ready to start collecting
            with open(obsfile) as pkl:
                obs_status = pickle.load(pkl)
            while not obs_status['ready']:
                time.sleep(1)
                with open(obsfile) as pkl:
                    obs_status = pickle.load(pkl)

            if debug or verbose:
                print time.asctime()
                print 'Moving to next coordinate.\n'

    # Return the number of unused items in the grid.
    return grid_remaining(grid)

def track_lb(leuschner, l, b, filenames, verbose=False, debug=False):
    """
    This moves the dish to track a certain l/b and returns whether or
    not the tracking completed.
    """
    global latitude
    global longitude

    # This uses the same filenames variable that was passed to the run_tracker
    # function. The grid file can be ignored.
    _, trackfile, obsfile, limitfile = filenames

    # Open the status files.
    with open(trackfile) as pkl:
        tr_status = pickle.load(pkl)
    with open(obsfile) as pkl:
        obs_status = pickle.load(pkl)

    # Get the altitude limits.
    with open(limitfile) as f:
        alt_limits = map(line2float, f.readlines())

    # Collect data while the observer
    first_attempt = True
    while obs_status['ready']:
        # Point the dish
        az, alt = coords.lb_to_azalt(l, b, latitude, longitude)
        try:
            # Check that the altitude is above the limits
            if alt <= alt_limits[int(round(az))]:
                raise ValueError

            if not debug:
                # dish.Dish.point will raise a ValueError if
                leuschner.point(alt, az)

            # Print a quick status update.
            if debug or verbose:
                print time.asctime()
                print 'Pointed to (az,alt): ('+ str(az) + ',' + str(alt) + ')\n'

        except ValueError:
            # Wait until the observation is done, then return failure.
            print time.asctime()
            print 'Cannot track this position.',
            # EDIT 2014 April 24 01:30 AARON
            # IF POINT IS NEVER UP, GETS STUCK HERE --
            # status is fixed on 'switching'
            # observe.py never sees 'tracking', to trigger data collection.
            # Solution, don't even wait.  Just return false, and keep moving.
            # BUT, WHAT IF POINT WAS ONCE UP THEN SETS?
            # ...
            # Solution: run while loop only if not first_attempt
            # If first attempt, we haven't started getting data yet
            if first_attempt:
                print 'Moving to next position.\n'
                time.sleep(0.025)
            else:
                print 'Waiting...\n'
                tr_status['status'] = 'idle'
                with open(trackfile, 'w') as pkl:
                    pickle.dump(tr_status, pkl)

                while obs_status['ready']:
                    # Fool observe.py by thinking that the diode has been set.
                    # This is because observe.py will just wait until it sees
                    # that tracking.py has updated the diode before and
                    # observe.py will wait indefinitely until it sees the diode
                    # has been set to the state that it wants.
                    tr_status['diode'] = obs_status['want-diode']
                    with open(trackfile, 'w') as pkl:
                        pickle.dump(tr_status, pkl)

                    # Check the observe.py status every second.
                    time.sleep(1)
                    with open(obsfile) as pkl:
                        obs_status = pickle.load(pkl)

            # Exit with failure.
            return False

        # Set the diode.
        if obs_status['want-diode']:
            if debug or verbose:
                print time.asctime()
                print 'Noise: ON\n'
            if not debug:  # EDIT 2014 April 24, 03:59 same issue as before
                leuschner.noise_on()
        else:
            if debug or verbose:
                print time.asctime()
                print 'Noise: OFF\n'
            if not debug: # EDIT 2014 April 24, 04:00 same issue
                leuschner.noise_off()

        # Update the diode status
        tr_status['diode'] = obs_status['want-diode']
        with open(trackfile, 'w') as pkl:
            pickle.dump(tr_status, pkl)

        # Sleep for a minute, then check the status
        if first_attempt:
            tr_status['status'] = 'tracking'
            with open(trackfile, 'w') as pkl:
                pickle.dump(tr_status, pkl)
            first_attempt = False

        # We don't need to wait a minute to switch the dish when in debug mode.
        if debug:
            time.sleep(1)
        else:
            time.sleep(30)

        # Load the next status to get the loop conditions
        with open(obsfile) as pkl:
            obs_status = pickle.load(pkl)

    # Exit with success
    return True

if __name__ == '__main__':
    # Parse options from the command line
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hHdg:l:t:T:v')
    except getopt.GetoptError as err:
        print 'ERROR:', str(err)
        usage(1)

    # Read options
    debug = False
    verbose = False
    gridfile = None
    limitfile = None
    start_home = True
    start_time = None
    stop_time = None
    for opt, arg in opts:
        if opt == '-h':
            usage(0)
        elif opt == '-H':
            start_home = False
        elif opt == '-d':
            debug = True
        elif opt == '-g':
            gridfile = os.path.abspath(arg)
        elif opt == '-l':
            limitfile = os.path.abspath(arg)
        elif opt == '-t':
            start_time = time.mktime(time.strptime(arg, timefmt))
        elif opt == '-T':
            stop_time = time.mktime(time.strptime(arg, timefmt)) - 900
        elif opt == '-v':
            verbose = True

    # Check that all of the files are necessary.
    if gridfile == None:
        print 'ERROR: No grid file supplied.'
        usage(1)
    else:
        datadir = os.path.dirname(gridfile)
        trackfile = datadir + '/tracking.pkl'
        obsfile   = datadir + '/observing.pkl'
    if limitfile == None:
        print 'ERROR: No altitude limit file supplied.'
        usage(1)

    # Check the validity of the timing.
    if start_time != None and stop_time != None:
        if stop_time <= start_time:
            print 'ERROR: Stop time is before start time!'
            usage(1)
    if stop_time != None and stop_time <= time.time():
        print 'ERROR: Stopping time occured before running this script!'
        usage(1)

    # Print a nice message
    print 'WELCOME TO THE LEUSCHNER 21CM DISH!'
    print '-----------------------------------'
    print

    # Read in the grid file
    print time.asctime()
    print 'Reading grid from', gridfile + '.\n'
    with open(gridfile) as pkl:
        grid = pickle.load(pkl)

    # Create a status file with some default values.
    status = {'status': 'starting', # Status of the observing script.
              'l': 0.0,             # Galactic longitude
              'b': 0.0,             # Galactic latitude
              'diode': (0,0),       # Noise diode status
              'grid': None}         # Indices on the grid.

    # If there are no gridpoints left, then there is nothing to do.
    exit_early = False
    if not grid_remaining(grid):
        status['status'] = 'finished'
        exit_early = True

    # Write the default status to a pickle
    with open(trackfile, 'w') as pkl:
        pickle.dump(status, pkl)

    # Kill the program if there are no grid points.
    if exit_early:
        print time.asctime()
        print 'No grid point remaining. Data collection has been completed!'
        sys.exit()

    # Create a default observation pickle
    obs_status = {'ready': True, 'want-diode': False}
    with open(obsfile, 'w') as pkl:
        pickle.dump(obs_status, pkl)

    # Sleep until it is time to wake up.
    if start_time != None:
        print time.asctime()
        print 'Waiting until', time.ctime(start_time), 'to start operations.\n'
        while time.time() < start_time:
            time.sleep(1)

    # Create a dish object. If debugging, the actual dish shall not be touched.
    if debug:
        leuschner = None
    else:
        leuschner = dish.Dish()

    # Set the dish to the default configuration.
    if start_home:
        if not debug:
            print time.asctime()
            print 'Sending the dish to the home position.'
            dish_move = time.time()
            leuschner.home()
            dish_move = time.time() - dish_move
            print 'Done (' + str(dish_move/60.0) + ' min).\n'
    else:
        print time.asctime()
        print 'WARNING: Not starting from home position.\n'

    # The diode should be off by default
    if not debug:
        leuschner.noise_off()

    # Loop over the grid points:
    print time.asctime()
    print 'Observing the grid...\n'
    status['status'] = 'switching'

    filenames = [gridfile, trackfile, obsfile, limitfile]
    num_iter = 0
    while run_tracker(leuschner, stop_time, filenames, verbose, debug):
        num_iter += 1
        if debug or verbose:
            print time.asctime()
            print 'Iterations complete:', num_iter, '\n'
        time.sleep(1)

    # This is the song that never ends
    # It just goes on and on my friends
    # Some people started singing it not knowing what it was,
    # And they'll continue singing it forever just because...
    print time.asctime()
    print 'Data collection complete!'
    status['status'] = 'finished'
    with open(trackfile, 'w') as pkl:
        pickle.dump(status, pkl)
