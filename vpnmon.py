# Copyright (c) 2021-2022 by Don Deel. All rights reserved.

"""vpnmon

vpnmon does low-level monitoring of a VPN site and zero or more
of the systems available through connections with the VPN site.

See the get_params() document string for information about the
vpnmon operational parameters, which can be set by a parameters
file, command line parameters, or a combination of both.

vpnmon currently only runs on Windows, because the 'wexpect' import
is specific to Windows. A similar solution can be created for Linux
by using the 'pexpect' import instead. 'wexpect' is currently not
well documented, but documentation for 'pexpect' can be used to
understand 'wexpect'. The 'wexpect' import is used in the files
vpnmon_vpnclient.py and vpnmon_utilities.py.

ddeel 210418
"""

# -------- Standard library imports
import os                       # CLI and file handling
import signal                   # Control-C handling
import sys                      # Control-C handling
import time                     # Delay timing

# -------- Third party imports
# None

# -------- Local module function imports
from vpnmon_utilities import get_params
from vpnmon_utilities import get_targets
from vpnmon_utilities import pinger
from vpnmon_utilities import webping
from vpnmon_utilities import date_and_tod
from vpnmon_utilities import sounder
from vpnmon_utilities import datalogger

# -------- Local module class imports
from vpnmon_vpnclient import VPNClient

# -------- Local module shared data imports
import vpnmon_shared_data as sd

# -------- Constants
# None


# -------- Methods

def signal_handler(sig, frame):
    """Catch Control-C and do final cleanup before exiting

    Note: The 'wexpect' import will prevent the catching of
    Control-C if the wexpect-specific Windows environment
    variable 'WEXPECT_SPAWN_CLASS' is set to anything other
    than 'SpawnPipe', which is the default setting.
    """

    print('\n---- vpnmon stopped with Control-C ----')

    # Close the VPN connection, if it is open
    try:
        if sd.vpnclient != '': sd.vpnclient.close()
    except:
        pass
    print('VPN connection closed')

    # Close the vpnmon datalog file, if it is open
    try:
        if sd.datalogfile != '': sd.datalogfile.close()
    except:
        pass
    print('Datalog file closed')

    # End program
    sys.exit(0)                 # Control-C exit


# -------- Initializations
signal.signal(signal.SIGINT, signal_handler)    # Catch Control-C


# -------- Main

def main():
    """main()

    Determines operational parameters, then periodically monitors
    the low-level availability of a VPN site and zero or more of
    the systems that can be reached through connections with the
    VPN site.

    The monitoring of a VPN site is done using test cycles. Each
    test cycle starts with a ping to see if the VPN site responds.
    If it does, then a VPN connection is attempted. If that works,
    ping is used to see if zero or more systems behind the VPN
    connection respond, and then the VPN connection is closed.
    Success/fail information is collected in a datalog file for
    all attempted test operations during each test cycle.

    Successive test cycles are separated by specified delays.
    Test cycles can be run either a specified number of times or
    continuously until the program is terminated with Control-C.

    See the get_params() document string for information about
    the vpnmon operational parameters, which can be set by a
    parameters file, command line parameters, or a combination
    of both.

    Note: The VPN Client instance is kept as a shared data
    item (sd.vpnclient), so that it can be used to shut down
    the VPN Client instance cleanly when the program is ended
    with Control-C or a fatal error occurs in any function that
    is not defined in this module.
    """

    # Get vpnmon operational parameters
    params = get_params()

    # Create a VPN Client instance (shared data item)
    sd.vpnclient = VPNClient()

    # Run the requested number of vpnmon test cycles
    count = params['cycles']
    if count < 0: cycles_target_str = 'of Infinite'
    else: cycles_target_str = 'of ' + str(count)
    test_cycle = 1
    while not count == 0:

        # Get vpnmon targets to test via the VPN connection
        targets = get_targets(params['targets'])

        # Output the number, date, and time of the test cycle start
        date, tod = date_and_tod()
        print(str(test_cycle).rjust(3), date, tod, \
                'Start vpnmon test cycle', \
                test_cycle, cycles_target_str)

        # Gather results obtained during the test cycle
        test_results = {}

        # Initialize target ping result counters
        tgood = twarn = tfail = 0

        # =========================================================
        # -------- Test cycle activities are below --------

        # TEST: ping the VPN site
        date, tod = date_and_tod()
        vpn_ping_result = pinger(params['vpnurlip'], p_count = 2)
        if vpn_ping_result != 'Good':
            sounder(s_count = 3, s_quiet = params['quiet'])
        print(str(test_cycle).rjust(3), date, tod, \
                '-- VPN ping -----------', \
                vpn_ping_result, params['vpnname'])
        test_results['VPN ping'] = \
            str(test_cycle) + ',' \
            + date + ',' \
            + tod + ',' \
            + 'VPN ping' + ',' \
            + vpn_ping_result + ',' \
            + params['vpnurlip'] + ',' \
            + params['vpnname'] \
            + '\n'

        # TEST: If the VPN ping was OK, open the VPN connection
        vpn_open_result = 'Fail'    # Beginning assumption
        if vpn_ping_result == 'Good':
            date, tod = date_and_tod()
            vpn_open_result = \
                sd.vpnclient.open(params['vpnurlip'], \
                params['username'], \
                params['password'] )
        if vpn_open_result != 'Good':
            sounder(s_count = 3, s_quiet = params['quiet'])
        print(str(test_cycle).rjust(3), date, tod, \
                '-- VPN open() ---------', \
                vpn_open_result, params['vpnname'])
        test_results['VPN open'] = \
            str(test_cycle) + ',' \
            + date + ',' \
            + tod + ',' \
            + 'VPN open' + ',' \
            + vpn_open_result + ',' \
            + params['vpnurlip'] + ',' \
            + params['vpnname'] \
            + '\n'

        # TEST: If the VPN is open, ping target systems through it
        if vpn_open_result == 'Good':
            for target in targets:
                date, tod = date_and_tod()
                target_ping_result = pinger(target, p_count = 2)
                if target_ping_result != 'Good':
                    sounder(s_count = 1, s_quiet = params['quiet'])
                if target_ping_result == 'Good': tgood += 1
                if target_ping_result == 'Warn': twarn += 1
                if target_ping_result == 'Fail': tfail += 1
                print(str(test_cycle).rjust(3), date, tod, \
                        '-- ping', target.ljust(15), \
                        target_ping_result, targets[target])
                test_results[target] = \
                    str(test_cycle) + ',' \
                    + date + ',' \
                    + tod + ',' \
                    + 'Target ping' + ',' \
                    + target_ping_result + ',' \
                    + target + ',' \
                    + targets[target] \
                    + '\n'

        # TEST: If the VPN is open, close it
        if vpn_open_result == 'Good':
            date, tod = date_and_tod()
            vpn_close_result = sd.vpnclient.close()
            if vpn_close_result != 'Good':
                sounder(s_count = 3, s_quiet = params['quiet'])
            print(str(test_cycle).rjust(3), date, tod, \
                    '-- VPN close() --------', \
                    vpn_close_result, params['vpnname'])
            test_results['VPN close'] = \
                str(test_cycle) + ',' \
                + date + ',' \
                + tod + ',' \
                + 'VPN close' + ',' \
                + vpn_close_result + ',' \
                + params['vpnurlip'] + ',' \
                + params['vpnname'] \
                + '\n'

        # -------- Test cycle activities are above --------
        # =========================================================

        # Write test cycle results to the vpnmon datalog file
        datalogger_result = datalogger(params['datalog'], test_results)
        if datalogger_result != 'Good':
            print('Unable to record test results')

        # Output the number, date, and time of the test cycle end
        date, tod = date_and_tod()
        print(str(test_cycle).rjust(3), date, tod, \
                'End vpnmon test cycle', \
                test_cycle, cycles_target_str)

        # Output test cycle ping summary for target systems
        print(str(test_cycle).rjust(3), ' ', date, ' ', tod, ' ', \
            'vpnmon test cycle ping results:', '  Good: ', tgood, \
            ',  Warn: ', twarn, ',  Fail: ', tfail, sep='')

        # Determine if another test cycle is expected,
        # where a negative count means run continuously
        if count > 0: count -= 1        # Decrement only if positve
        if count == 0: continue         # Stop if done
        date, tod = date_and_tod()
        print(str(test_cycle).rjust(3), date, tod, \
                'Waiting to run next test cycle.\n')
        test_cycle += 1                 # More to do
        time.sleep(params['delay'])     # Wait between test cycles

    # Announce the completion of the requested number of test cycles
    date, tod = date_and_tod()
    print(str(test_cycle).rjust(3), date, tod, \
            test_cycle, 'vpnmon test cycles completed.')

    # End program
    exit(0)                     # Normal exit

    # End of main()


if __name__ == '__main__':
    main()      # If this is the main module, run main()
else:
    pass        # If this module is imported, do nothing
