"""
Script for Leuschner data taking
Astro 121, Spring 2014
CIA (Caleb Isaac Aaron)

Scripting flow:
    telescope tracking / slewing (change pointings) -- Isaac
    [*] data taking, LO and noise diode settings -- Aaron
    data reduction and processing? -- Caleb

Tracking (Isaac):
    2405 pointings @ 2 deg. spacing
        (naive oversampling gives 3825)
        (most are too far south: must get as many as possible)
    Tracking: beamwidth = 4 deg., objects move (at most) 0.125 deg./30s
        For same target, repoint every minute (maybe 30s to be safe?)

    how/when to track (minimize noise/interference, maybe a particular
    range of az/alt is best?  Or (in some perfect world) multiple pointings
    at varying az-alt, but same l-b, to remove pointing-dependent noise.

T_B sets integration time:
    T_B ~ 1 to 10 K [Sofue and Reich, 1979 A&AS]
        [cf. Reich and Reich, 1985 Bull. ICDS]
    For comparison [HI1.pdf]
    ~0.1 K needs ~10 min./pt
    ~1 K needs ~ few min./pt

Timing for spectra collection (mm:ss):
    n=10    00:06.92
    n=25    00:17.17
    n=50    00:34.42
    n=100   01:09.61
    n=150   01:44.74

    Time/spectrum is ~0.692 seconds
    (but, I don't know the amt of dead time?)
    (super conservative assumption is ~0.33 s/spectrum)

Aaron Tran
Last modified: 2014 April 23
"""

import os
import time
import cPickle as pickle

import dish
import dish_synth
import takespec

def main():
    """Control Leuschner data collection.

    BEWARE -- if tracking.py fails, THIS WILL HANG FOREVER!!!
    Need to build in a failure mechanism (stoptime)

    tracking.pkl key:value pairs
        'status': 'starting'/'switching'/'tracking'/'finished'
        'l', 'b': galactic coordinates in degrees (floats)
        'grid': 2-tuple of grid indices (ints)
        'diode': diode status (boolean)
    observing.pkl key:value pairs
        'want-diode': (boolean)
        'ready': (boolean)
    """

    # Get tracking pickle strings
    trackstr = '../data/tracking.pkl'  # TODO get this as argument
    datadir = os.path.dirname(trackstr)  # Directory for all data output
    obsrvstr = os.path.join(datadir,
                            'observing.pkl')

    # Setup LO, initialize observing.pkl
    synth = dish_synth.Synth(verbose=True)
    synth.set_amp(10)  # TODO set LO amplitude
    make_pkl(obsrvstr, {'want-diode': False,
                        'ready': True})
    print 'Initial observing.pkl generated'

    # Check if waiting for observations to start
    # OPTIONAL: can just let poll_pkl do blocking
    # tracking = get_pkl(trackstr)
    # if tracking['status'] == 'starting':
    #     time.sleep(amt_time_wait)

    # Wait until Leuschner is pointing -- i.e., tracking fixed l,b
    while poll_tracking_status(trackstr, 'tracking'):
        # Ready and tracking, so start collecting data
        execute_pnt(trackstr, obsrvstr, synth, datadir)
        update_pkl(obsrvstr, 'ready', False)
        # Wait for confirmation that Leuschner knows we're done/switching
        if poll_tracking_status(trackstr, 'switching'):
            update_pkl(obsrvstr, 'ready', True)
        else:
            break

    # Done -- poll_tracking_status(...) == False throws us out of while loop
    print 'Finished collecting data (cleanly from finished status)'


def poll_tracking_status(trackstr, value, wtime=1):
    """Poll until tracking.pkl status == value, or alert if finished.
    Output:
        True if value matches
        False if finished
        Else, wait until either case occurs (don't let it hang here)
    """
    while not check_pkl(trackstr, 'status', value):
        if check_pkl(trackstr, 'status', 'finished'):
            return False
        if check_pkl(trackstr, 'status', 'idle'):
            break
        time.sleep(wtime)
    return True


def execute_pnt(trackstr, obsrvstr, dsynth, datadir):
    """Perform all actions associated with a single pointing"""
    # Tracking, time to start getting data!
    # Start w/ info about current (l,b)
    tracker = get_pkl(trackstr)
    l, b = tracker['l'], tracker['b']  # Degrees
    grid = tracker['grid']  # Grid indices, 2 element tuple
    # Will have _left, _right, _cal, _meta appended
    pnt_fname = ('data_l_%06.2f_b_%06.2f_grid_%03d_%03d' %
                 ((l, b) + grid))  # Need better filenames, don't use equals
    pnt_fname = os.path.join(datadir, pnt_fname)

    # Using default settings (integration time, LO freqs) for now
    n_obs  = 87 * 2
    n_cal  = 9 * 2
    f_low  = 1268.9
    f_high = 1271.9
    okay, pklname = record_pnt_data(pnt_fname, trackstr, obsrvstr, dsynth,
                                    n_obs, n_cal, f_low, f_high)
    if not okay:
        print 'ERROR: data collection failed!'

    # Write pickle file of metadata
    pkldict = {}
    pkldict['rec-success'] = okay
    pkldict['l'] = l
    pkldict['b'] = b
    pkldict['grid'] = grid
    pkldict['n_obs'] = n_obs
    pkldict['n_cal'] = n_cal
    pkldict['f_low'] = f_low
    pkldict['f_high'] = f_high
    pkldict['fname'] = os.path.basename(pnt_fname)
    make_pkl(pklname, pkldict)


###################################
# Data collection for each pointing
###################################

def record_pnt_data(fname, trackstr, obsvrstr, dsynth, n_obs=87, n_cal=9,
                    f_low=1268.9, f_high=1271.9):
    """Collect spectra for a single pointing (right, right+cal, left, left+cal)
    Writes five files: left spectra, right spectra, cal spectra, metadata

    Defaults: 87, 9, 87 spectra (total time: ~02:06 (mm:ss))
    n_obs   = 87 (1 min. @ 0.692 s/spectrum)
    n_cal   = 9 (6 sec. @ 0.692 s/spectrum)
    f_low  = (1270.4 - 1.5) MHz
    f_high = (1270.4 + 1.5) MHz

    N.B. neglecting dead time!  Integration time may be < 1 min.

    Inputs:
        fname (str): filename for output data (3 .log binary files)
        trackstr (str): filename of tracking pickle
        obsvrstr (str): filename of observing pickle
        n_obs (int): number of spectra for each data integration
                     gives 2*n_obs total data spectra
        n_cal (int): number of spectra for noise integration
        f_low (float): LO freq of RIGHT band measurement (shifts signal right)
        f_high (float): LO freq of LEFT band measurement (shifts signal left)
    Output:
        True if successful (no exceptions raised), else False
        Also returns filename of metadata .pkl, for subsequent editing
    """
    success = True
    pklname = fname + '_meta.pkl'
    try:
        # Take spectrum at f_high
        print 'Recording %s' % (fname+'_left')
        check_idle(dsynth.set_freq, trackstr, (f_high,), {})
        check_idle(takespec.takeSpec,
                   trackstr,
                   (fname+'_left',),
                   {'numSpec':n_obs})
        # Take noise at f_high, request on/off
        check_idle(set_want_diode, trackstr, (True, obsvrstr, trackstr), {})
        check_idle(takespec.takeSpec,
                   trackstr,
                   (fname+'_left_cal',),
                   {'numSpec':n_cal})
        check_idle(set_want_diode, trackstr, (False, obsvrstr, trackstr), {})

        # Take spectrum at f_low
        print 'Recording %s' % (fname+'_right')
        check_idle(dsynth.set_freq, trackstr, (f_low,), {})
        check_idle(takespec.takeSpec,
                   trackstr,
                   (fname+'_right',),
                   {'numSpec':n_obs})
        # Take noise at f_low, request on/off
        check_idle(set_want_diode, trackstr, (True, obsvrstr, trackstr), {})
        check_idle(takespec.takeSpec,
                   trackstr,
                   (fname+'_right_cal',),
                   {'numSpec':n_cal})
        check_idle(set_want_diode, trackstr, (False, obsvrstr, trackstr), {})

    # check_idle raises exceptions if the dish isn't pointing
    except Exception as e:  # This won't catch KeyboardInterrupt etc.
        success = False
        print 'Error in data collection: %s' % e

    return success, pklname

def set_want_diode(set_on, obsvrstr, trackstr):
    """value must be True/False"""
    if set_on:
        print 'Requesting noise on'
    else:
        print 'Requesting noise off'
    update_pkl(obsvrstr, 'want-diode', set_on)
    poll_pkl(trackstr, 'diode', set_on)  # Warning, may hang
    print 'Noise set'


def time2nspec(t):
    """Number of spectra for desired integration time.
    Does NOT account for dead time -- maybe add more spectra to be safe?
    If Aaron/Karto/Baylee tweak stuff, may need to change..."""
    return int(float(t) / 0.692) + 1  # 0.692 sec. / spectrum

# EDIT: Domagalski (04/26/2014 10:15PM)
# This function is for making sure that the dish is actually tracking an object
# before performing any of the functions in record_pnt_data. If the object is
# not being tracked, then raise an error to go to the failure state of the run.
def check_idle(function, trackstr, fargs, fkargs):
    """
    This function checks to see if the dish is idle because it can't be
    pointed. If it is idle, raise an error to trigger an unsuccessful
    data collection. If the dish is pointing, then run some function.
    """
    if check_pkl(trackstr, 'status', 'idle'):
        raise IOError('Tracker cannot point to coordinates.')
    return function(*fargs, **fkargs)


################
# Pickle methods
################
# Pickle file for poll/check/update_pkl must be dictionary!

# poll_pkl(fname, key, value, wtime=1)
# check_pkl(fname, key, value
# update_pkl(fname, key, value)

# make_pkl(fname, thing)
# get_pkl(fname)

def poll_pkl(fname, key, value, wtime=1):
    """Poll pkl at interval wtime sec., block until pkl[key] == value
    Output:
        True if the value matches, else wait (no other possible output!)
    """
    while not check_pkl(fname, key, value):
        time.sleep(wtime)
    return True

def check_pkl(fname, key, value):
    """Return true/false if pkl[key] == value (no blocking)"""
    pkl = get_pkl(fname)
    return pkl[key] == value

def update_pkl(fname, key, value):
    """Load pickled dictionary, update key-value, repickle"""
    pkl = get_pkl(fname)
    pkl[key] = value
    make_pkl(fname, pkl)

################################################################################
# EDIT: Domagalski (04/26/2014, 8:45 PM)
# Our first run got killed by an EOFError occurring in one of the pickle
# routines, so I've decided to modify them to prevent that from happening.
################################################################################

errtime = 0.25

def make_pkl(fname, thing):
    """Pickle Python thing, given pkl filename (string)"""
    global errtime
    while True:
        try:
            with open(fname, 'wb') as pkl_file:
                pickle.dump(thing, pkl_file)
            return
        except EOFError:
            time.sleep(errtime)

def get_pkl(fname):
    """Extract object from pkl file, given pkl filename (string)"""
    global errtime
    while True:
        try:
            with open(fname, 'rb') as pkl_file:
                pkl_dict = pickle.load(pkl_file)
            return pkl_dict
        except EOFError:
            time.sleep(errtime)

if __name__ == "__main__":
    main()
