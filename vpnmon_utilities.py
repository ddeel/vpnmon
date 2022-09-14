# Copyright (c) 2021-2022 by Don Deel. All rights reserved.

"""vpnmon utilities

This is a collection of utility methods used by vpnmon:
    get_params()    - Get operational parameters for vpnmon
    get_targets()   - Get a list of targets to test via the VPN
    pinger()        - Ping a URL or IP address
    webping()       - See if a web site is responding
    date_and_tod()  - Return date and time of day as a tuple
    sounder()       - Make one or more sounds to get attention
    datalogger()    - Write test results to a datalog file

Document strings provide more information about each method below.

ddeel 210418
"""

# -------- Standard library imports
import argparse                 # CLI handling
import os                       # CLI and file handling
import time                     # Delay timing
from datetime import datetime   # Date and time

# -------- Third party imports
from pythonping import ping     # Python-based ping
import requests                 # HTTP handling for webping

# -------- Local module function imports
from vpnmon_version import __version__      # vpnmon version
from vpnmon_vpnclient import VPNClient

# -------- Local module shared data imports
import vpnmon_shared_data as sd


# -------- Constants
VPNMON_PARAMS_FILE  = 'vpnmon_params.csv'
VPNMON_TARGETS_FILE_DEFAULT = 'vpnmon_targets.csv'
VPNMON_DATALOG_FILE_DEFAULT = 'vpnmon_datalog.csv'
VPNMON_DATALOG_WRITE_MAX_RETRIES = 5
VPNMON_DATALOG_WRITE_RETRY_DELAY = 15


# -------- Methods

def get_params():
    """Get operational parameters for vpnmon

    The following vpnmon operational parameters can be set:
        vpnname:    VPN site human-readable name.
        vpnurlip:   VPN site URL or IP address.
        username:   VPN username.
        password:   VPN password.
        targets:    CSV file containing system names
                    and URLs or IP addresses to test
                    over the VPN connection.
        cycles:     Number of times to open the VPN, test
                    the list of URLs or IP addresses, and
                    then close the VPN. (-1 means run until
                    stopped by Control-C.)
        delay:      Seconds between VPN test cycles.
        datalog:    CSV file for collected test data.
        quiet:      Do not make sounds for test failures.

    vpnmon operational parameters can be set by an optional
    vpnmon parameters file and/or by optional vpnmon command
    line parameters.

    The vpnmon parameters file is a CSV file kept in the same
    directory or folder as vpnmon. This file is optional
    but convenient for setting parameters that do not change
    frequently. A subset of the vpnmon parameters can be set
    in this file. It does not have to set all the parameters.

    vpnmon command line parameters override the parameters
    in the vpnmon parameters file, allowing the user to make
    changes without editing the parameters file. (This also
    allows the user to purposely leave sensitive information
    out of the parameters file, such as the VPN password.)

    vpnmon operational parameters are returned as a dictionary.

    Note: A fatal error exit will occur if the optional vpnmon
    parameters file is present but cannot be accessed.
    """

    # Set defaults for all parameters. Note that
    # all parameter names must be in lower case.
    params = {'vpnname': 'VPN Gateway',
              'vpnurlip': '',
              'username': '',
              'password': '',
              'targets': VPNMON_TARGETS_FILE_DEFAULT,
              'cycles': 200,
              'delay': 1800,
              'datalog': VPNMON_DATALOG_FILE_DEFAULT,
              'quiet': False}

    # Read in an optional vpnmon parameters file containing one
    # or more parameters. If this file is missing or empty, the
    # default parameters defined above will be used. This file
    # has one parameter entry per line, with each line having
    # the name of the parameter, followed by a comma, followed
    # by the parameter value. Parameter names that are not
    # already defined in the params dictionary are ignored.
    if os.path.exists(VPNMON_PARAMS_FILE):
        try:
            paramsfile = open(VPNMON_PARAMS_FILE, 'r')
            for line in paramsfile:
                # Remove end of line and split into fields
                line = line.replace('\n', '')
                param_entry = line.split(',', 2)
                # Only accept defined parameters
                if param_entry[0].lower() in params:
                    params[param_entry[0].lower()] = param_entry[1]
            # Ensure integer parameters are integers
            params['cycles'] = int(params['cycles'])
            params['delay'] = int(params['delay'])
            paramsfile.close()
        except Exception as error:
            print('Failed to read the vpnmon params file:')
            print(error)
            # Exit with a fatal error
            print('vpnmon fatal error exit.')
            exit(1)
    else:
        print('Running without a vpnmon params file')

    # Handle optional command line parameters. When present,
    # these parameters override the corresponding parameter
    # file values and/or default values.
    # TODO: Add '+ __version__' to the argparse 'description'
    parser = argparse.ArgumentParser(
        description = 'VPN Monitoring Tool',
        epilog = 'Developed by Don Deel' )
    parser.add_argument('-v', '-V', '--version', action='store_true',
        help='Show the vpnmon version and exit')
    parser.add_argument('-vpnname', '--vpnname',
        help='VPN site human-readable name')
    parser.add_argument('-vpnurlip', '--vpnurlip',
        help='VPN site URL or IP address')
    parser.add_argument('-user', '--username',
        help='VPN account username')
    parser.add_argument('-pass', '--password',
        help='VPN account password')
    parser.add_argument('-targets', '--targets',
        help='CSV file for targets to ping via the VPN')
    parser.add_argument('-cycles', '--cycles', type = int,
        help='Number of test cycles to run')
    parser.add_argument('-delay', '--delay', type = int,
        help='Seconds between test cycles')
    parser.add_argument('-datalog', '--datalog',
        help='CSV file for the vpnmon datalog')
    parser.add_argument('-quiet', '--quiet', action='store_true',
        help='Do not make sounds for test failures')
    args = parser.parse_args()
    if args.version:            # Show version and exit
        print('vpnmon version', __version__)
        exit(0)
    if not(args.vpnname==None): params['vpnname'] = args.vpnname
    if not(args.vpnurlip==None): params['vpnurlip'] = args.vpnurlip
    if params['vpnurlip']=='':
        print('Cannot run without a VPN site URL or IP address.')
        exit(0)
    if not(args.username==None): params['username'] = args.username
    if not(args.password==None): params['password'] = args.password
    if not(args.targets==None): params['targets'] = args.targets
    if not(args.cycles==None): params['cycles'] = args.cycles
    if not(args.delay==None): params['delay'] = args.delay
    if not(args.datalog==None): params['datalog'] = args.datalog
    if not(args.quiet==None): params['quiet'] = args.quiet
    return params

    # End of get_params()


def get_targets(targets_file):
    """Get a list of targets to test via the VPN connection

    Reads in an optional vpnmon targets file containing the
    names and URLs or IP addresses of target systems to test
    with 'ping' through the VPN. If this CSV file is missing
    or empty, no targets will be tested. This CSV file has
    one target system entry per line, with each line having
    the URL or IP address of the target system, followed by
    a comma, followed by the target system name.

    A list of targets is returned as a dictionary that can
    be empty.

    Note: A fatal error exit will occur if the optional vpnmon
    targets file is present but cannot be accessed.
    """

    targets = {}
    if os.path.exists(targets_file):
        try:
            targets_file = open(targets_file, 'r')
            for line in targets_file:
                # Remove end of line and split into fields
                line = line.replace('\n', '')
                ip_and_name = line.split(',', 2)
                # Only use the first two fields on a line
                targets[ip_and_name[0]] = ip_and_name[1]
            targets_file.close()
        except Exception as error:
            print('Failed to read the vpnmon targets file:')
            print(error)
            # Exit with a fatal error
            print('vpnmon fatal error exit.')
            exit(1)
    else:
        print('Running without a vpnmon targets file')
    return targets

    # End of get_targets()


def pinger(siteurlip, p_count=1, p_timeout=1.000):
    """Run ping on a URL or IP address

    Provides a generic version of the ping command. Uses one
    or more ping commands to see if a target is responding.

    Arguments:
        siteurlip:  URL or IP address of the ping target.
        p_count:    Number of times to ping the target
                    (default is 1).
        p_timeout:  Maximum time to wait for ping responses
                    (default is 1.000 seconds).

    Returns 'Good' if all ping responses are received without
    error. Returns 'Fail' if all ping responses time out.
    Returns 'Warn' if some but not all ping responses time out.
    """

    good = 0
    for i in range(0, p_count):
        ping_list = ping(siteurlip,
                         count = p_count, \
                         timeout = p_timeout)
        if ping_list._responses[0].success:
            good += 1

    if good == p_count:
        return 'Good'           # All pings succeeded
    elif good == 0:
        return 'Fail'           # All pings failed
    else:
        return 'Warn'           # Some but not all pings failed

    # End of pinger()


def webping(siteurlip, wp_timeout=5.0):
    """Check a web site at a URL or IP address

    Provides a simple test to see if a web site is responding.

    Arguments:
        siteurlip:  URL or IP address of the web site.
        wp_timeout: Maximum time to wait for a web site response
                    (default is 5.00 seconds).

    Returns 'Good' if the web site responds with an HTTP "OK"
    Code (200). Returns 'Fail' if any other response is received.
    """

    try:
        response = requests.get(siteurlip, timeout=wp_timeout)
        result = response.status_code
    except:
        result = 0

    if result == 200:
        return 'Good'           # Web site responded with "OK"
    else:
        return 'Fail'           # Web site did not respond "OK"

    # End of webping()


def date_and_tod():
    """Return date and time of day as a tuple

    Returns the current date and time as a tuple of two strings.
    The first string is the current date, and the second string
    is the current time.
    """

    now = datetime.now()
    date = now.strftime('%Y/%m/%d')
    tod = now.strftime('%H:%M:%S')
    return date, tod

    # End of date_and_tod()


def sounder(s_count=1, s_quiet=False):
    """Make one or more sounds to get attention

    Makes a sound 'count' times in rapid succession, but
    only when 's_quiet' is False.
    """

    if not(s_quiet):
        for x in range(s_count):
            print('\a', end='', flush=True)
            time.sleep(0.30)
    return

    # End of sounder()


def datalogger(datalog_file, test_data):
    """Write test results to a datalog file

    Creates 'datalog_file' if it does not already exist, and
    then appends 'test_data' to the contents of 'datalog_file'.
    'test_data' is expected to be a dictionary of any size in
    CSV format, with one line per test result entry.

    Includes a limited tolerance for the possibility that
    another program (such as an datalog analysis program)
    might be accessing the datalog file when datalogger()
    needs to write more data into the datalog file.

    Returns 'Good' when 'test_data' is successfully written
    into 'datalog_file'. Returns 'Fail' when 'test_data'
    cannot be written into 'datalog_file' because another
    program is accessing 'datalog_file'.

    Note: A fatal error exit will occur if 'datalog_file'
    cannot be accessed for any reason other than the
    situation where another program is using the file.

    Note: The datalog file handle is kept as a shared data
    item (sd.datalogfile), so that it can be used to close
    the datalog file whenever the program is ended with
    Control-C.
    """

    return_value = 'Fail'       # Beginning assumption
    write_retry = VPNMON_DATALOG_WRITE_MAX_RETRIES
    while write_retry > 0:
        try:
            sd.datalogfile = open(datalog_file, 'a')
            for entry in test_data:
                sd.datalogfile.write(test_data[entry])
            sd.datalogfile.close()
        except PermissionError as error:
            # Inadequate file access rights. This can occur if
            # another program is accessing the datalog file when
            # the write is attempted. The write will be retried
            # a limited number of times, waiting a few seconds
            # between each attempt. If it still cannot succeed,
            # the write attempt is aborted.
            write_retry -= 1
            if write_retry > 0:
                print('Cannot open the vpnmon datalog file;', \
                      'retrying')
                time.sleep(VPNMON_DATALOG_WRITE_RETRY_DELAY)
            else:
                print('Unable to open the vpnmon datalog file')
                print('Aborting this attempt to record results')
                print('Skipping forward to the next test cycle')
            continue
        except Exception as error:
            print('Failed to access the vpnmon datalog file:')
            print(error)
            # Shut down the VPN Client instance (shared data item)
            try:
                sd.vpnclient.close()
            except:
                pass
            # Exit with a fatal error
            print('vpnmon fatal error exit.')
            exit(1)
        else:
            # If a 'retrying' message was printed because of a
            # PermissionError above, print a message here that
            # says the file finally did get updated
            if write_retry < VPNMON_DATALOG_WRITE_MAX_RETRIES:
                print('The vpnmon datalog file has been updated')
            write_retry = 0         # No retry needed
            return_value = 'Good'   # Success case
    return return_value

    # End of datalogger()
