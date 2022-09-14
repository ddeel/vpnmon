# Copyright (c) 2021-2022 by Don Deel. All rights reserved.

"""VPNClient Class

This VPNClient class provides open() and close() methods for
using the Windows Cisco AnyConnect Secure Mobility Client CLI.

After creating an instance of the VPNClient class, programs are
expected to call open(), use the VPN connection, and then call
close(). The open()/close() sequence can be done multiple times.
Failure to call close() can result in the VPN connection being
left open when the calling program ends.

The user should not attempt to use another AnyConnect application
at the same time that an instance of this class is active on the
same system. Only one AnyConnect application can be run at a time.

This module only runs on Windows. The 'wexpect' import and the
behavior of the Windows Cisco AnyConnect CLI are both specific to
Windows. A similar solution can be created for Linux by using the
'pexpect' import and accommodating any behavioral changes found
in the Cisco AnyConnect CLI on Linux. Documentation for 'pexpect'
can be used to understand 'wexpect'.

Note: The 'wexpect' import does not work with venv or virtualenv,
so this module is not compatible with these virtual envronments.

ddeel 210418
"""

# Imports
import wexpect                  # App interaction handling
import time                     # Delay timing

# Constants
VPNCLI_CMD_DELAY = 0.5          # vpncli command delay in seconds
WEXPECT_TIMEOUT = 120           # wexpect timeout in seconds


class VPNClient:

    def __init__(self):
        """Constructor for a VPNClient instance
        """

        # End of __init__()


    def open(self, vpnsitename, vpnusername, vpnpassword):
        """Open the VPN connection

        Opens a VPN connection using the Cisco AnyConnect CLI.

        Spawns a child process, starts the Cisco Anyconnect CLI,
        and then opens a VPN connection. The Cisco AnyConnect CLI
        started by open() is also be used by close() to close the
        VPN connection.

        Returns 'Good' for success and 'Fail' for failure.
        Failures also result in error messages being sent to the
        console. Failure situations where no recovery is possible
        result in a hard exit for both this method and the caller.

        Terminates all other Cisco AnyConnect applications, because
        only one Cisco AnyConnect application can run at a time.

        wexpect note: Each major step provides its own stimulus
        and verifies the response with one or more 'expect' items
        before the control flow moves on to the next step. Note
        that a log file can be used with wexpect for debugging,
        but it will record and reveal VPN usernames and passwords.

        vpncli note: Short delays are needed between CLI commands,
        otherwise one or more commands can be ignored by the CLI.
        The approach for working with vpncli states and behaviors
        comes from empirical evidence, which may be incomplete.
        """

        # Cisco AnyConnect CLI location on Windows
        cisco_dir = 'c:\\"Program Files (x86)"\\Cisco'
        cisco_cli = '\\"Cisco AnyConnect Secure Mobility Client"'
        vpncli = cisco_dir + cisco_cli + '\\vpncli'

        # Log file for debug; should normally be set to None,
        # because the log file will show VPN login credentials
        # Debug only:   vpn_log_file = open('vpnmon_log.txt', 'w')
        # Normal use:   vpn_log_file = None
        vpn_log_file = None

        # Globals
        global vpn_proc         # Spawned process ID


        # Terminate all other Cisco AnyConnect applications, because
        # only one Cisco AnyConnect application can run at a time
        try:
            wexpect.host.run('taskkill /f /im vpnui.exe')
            wexpect.host.run('taskkill /f /im vpncli.exe')
        except Exception as error:
            print('Unable to end an existing AnyConnect UI or CLI.')
            # There is no way to recover; do a hard exit
            exit(1)

        # Spawn a child process to run the Cisco AnyConnect CLI
        try:
            vpn_proc = wexpect.spawn('cmd.exe', \
                                     timeout = WEXPECT_TIMEOUT, \
                                     logfile = vpn_log_file)
            vpn_proc.expect('>')
        except Exception as error:
            print('Unable to spawn child process', \
                  'to run the Cisco AnyConnect CLI.')
            print('---- Start diagnostic information ----')
            print(vpn_proc.before)
            print('----  End diagnostic information  ----')
            # There is no way to recover; do a hard exit
            exit(1)

        # Start vpncli, which is the Cisco AnyConnect CLI
        try:
            time.sleep(VPNCLI_CMD_DELAY)
            vpn_proc.sendline(vpncli)
            vpn_proc.expect('VPN>')
        except Exception as error:
            print('Unable to use the Cisco AnyConnect CLI.')
            print('---- Start diagnostic information ----')
            print(vpn_proc.before)
            print('----  End diagnostic information  ----')
            # There is no way to recover; attempt to shut down the
            # Cisco AnyConnect CLI instance (in case it got started)
            # and do a hard exit
            try:
                vpn_proc.terminate(force=True)
                wexpect.host.run('taskkill /f /im vpncli.exe')
            except Exception as error:
                print('Unable to terminate child process (136).')
            exit(1)

        # Make sure the VPN is disconnected
        try:
            time.sleep(VPNCLI_CMD_DELAY)
            vpn_proc.sendline('disconnect')
            vpn_proc.expect('VPN>')
        except Exception as error:
            print('Unable to disconnect the VPN for open().')
            print('---- Start diagnostic information ----')
            print(vpn_proc.before)
            print('----  End diagnostic information  ----')
            # There is no way to recover; attempt to shut down the
            # Cisco AnyConnect CLI instance and do a hard exit
            try:
                vpn_proc.terminate(force=True)
                wexpect.host.run('taskkill /f /im vpncli.exe')
            except Exception as error:
                print('Unable to terminate child process (155)')
            exit(1)

        # Initiate a connection with the VPN site
        try:
            time.sleep(VPNCLI_CMD_DELAY)
            vpn_proc.sendline('connect ' + vpnsitename)
            index = vpn_proc.expect(['Username:', \
                                     'unsuccessful domain name', \
                                     'Connect not available.', \
                                     'cannot verify server', \
                                     wexpect.TIMEOUT])
            if index == 1:
                # Unable to contact the VPN site
                print('Unable to contact', vpnsitename)
                print('---- Start diagnostic information ----')
                print(vpn_proc.before)
                print('----  End diagnostic information  ----')
                # This could be a temporary situation, so recovery
                # might still be possible; attempt to shut down the
                # Cisco AnyConnect CLI instance and return with a
                # failure
                try:
                    vpn_proc.terminate(force=True)
                    wexpect.host.run('taskkill /f /im vpncli.exe')
                except Exception as error:
                    print('Unable to terminate child process (181).')
                return 'Fail'
            if index == 2:
                # Another Cisco AnyConnect application is running
                print('Another AnyConnect UI or CLI is running.')
                print('---- Start diagnostic information ----')
                print(vpn_proc.before)
                print('----  End diagnostic information  ----')
                # There is no way to recover; attempt to shut down
                # the Cisco AnyConnect CLI instance and return with
                # a failure
                try:
                    vpn_proc.terminate(force=True)
                    wexpect.host.run('taskkill /f /im vpncli.exe')
                except Exception as error:
                    print('Unable to terminate child process (196).')
                return 'Fail'
            if index == 3:
                # Cisco AnyConnect cannot verify the VPN server
                print('AnyConnect cannot verify the VPN server.')
                print('There may be a server certificate issue.')
                print('---- Start diagnostic information ----')
                print(vpn_proc.before)
                print('----  End diagnostic information  ----')
                # There is no way to recover; attempt to shut down
                # the Cisco AnyConnect CLI instance and return with
                # a failure
                try:
                    vpn_proc.terminate(force=True)
                    wexpect.host.run('taskkill /f /im vpncli.exe')
                except Exception as error:
                    print('Unable to terminate child process (212).')
                return 'Fail'
            if index == 4:
                # Timeout waiting for VPN connection response
                print(vpnsitename,'is not responding.')
                print('---- Start diagnostic information ----')
                print(vpn_proc.before)
                print('----  End diagnostic information  ----')
                # This could be a temporary situation, so recovery
                # might still be possible; attempt to shut down the
                # Cisco AnyConnect CLI instance and return with a
                # failure
                try:
                    vpn_proc.terminate(force=True)
                    wexpect.host.run('taskkill /f /im vpncli.exe')
                except Exception as error:
                    print('Unable to terminate child process (228).')
                return 'Fail'
        except Exception as error:
            # An unanticipated VPN connection error occurred
            print('Got an unexpected VPN connection error.')
            print('Unable to complete VPN connection setup.')
            print('---- Start diagnostic information ----')
            print(vpn_proc.before)
            print('----  End diagnostic information  ----')
            # This could be a temporary situation, so recovery
            # might still be possible; attempt to shut down the
            # Cisco AnyConnect CLI instance and return with a
            # failure
            try:
                vpn_proc.terminate(force=True)
                wexpect.host.run('taskkill /f /im vpncli.exe')
            except Exception as error:
                print('Unable to terminate child process (245).')
            return 'Fail'

        # Enter the VPN login credentials
        try:
            time.sleep(VPNCLI_CMD_DELAY)
            vpn_proc.sendline(vpnusername)
            vpn_proc.expect('Password:')
            time.sleep(VPNCLI_CMD_DELAY)
            vpn_proc.sendline(vpnpassword)
            index = vpn_proc.expect(['accept?', \
                                     'Login failed', \
                                     wexpect.TIMEOUT])
            if index == 1:
                # Username and/or Password was not accepted
                print('VPN Username/Password was not accepted.')
                print('---- Start diagnostic information ----')
                print(vpn_proc.before)
                print('----  End diagnostic information  ----')
                # The Cisco AnyConnect CLI is now only listening
                # for Username/Password entry, and there is no
                # way to recover; attempt to shut down the Cisco
                # AnyConnect CLI instance and return 'Fail'
                try:
                    vpn_proc.terminate(force=True)
                    wexpect.host.run('taskkill /f /im vpncli.exe')
                except Exception as error:
                    print('Unable to terminate child process (272).')
                return 'Fail'
            if index == 2:
                # Timeout waiting for VPN credential entry response
                print('VPN credentials response timeout.')
                print('---- Start diagnostic information ----')
                print(vpn_proc.before)
                print('----  End diagnostic information  ----')
                # This could be a temporary situation, so recovery
                # might still be possible; attempt to shut down the
                # Cisco AnyConnect CLI instance and return with a
                # failure
                try:
                    vpn_proc.terminate(force=True)
                    wexpect.host.run('taskkill /f /im vpncli.exe')
                except Exception as error:
                    print('Unable to terminate child process (288).')
                return 'Fail'
        except Exception as error:
            # An unanticipated VPN credentials error occurred
            print('Got an unexpected VPN credentials error.')
            print('Unable to accept VPN connection credentials.')
            print('---- Start diagnostic information ----')
            print(vpn_proc.before)
            print('----  End diagnostic information  ----')
            # This could be a temporary situation, so recovery
            # might still be possible; attempt to shut down the
            # Cisco AnyConnect CLI instance and return with a
            # failure
            try:
                vpn_proc.terminate(force=True)
                wexpect.host.run('taskkill /f /im vpncli.exe')
            except Exception as error:
                print('Unable to terminate child process (305).')
            return 'Fail'

        # Accept the VPN banner
        try:
            time.sleep(VPNCLI_CMD_DELAY)
            vpn_proc.sendline('y')
            index = vpn_proc.expect(['state: Connected', \
                                     'Please try connecting again', \
                                     'driver encountered an error', \
                                     wexpect.TIMEOUT])
            if index == 1:
                # Unable to establish a connection this time
                print('Unable to establish a connection this time')
                print('---- Start diagnostic information ----')
                print(vpn_proc.before)
                print('----  End diagnostic information  ----')
                # This could be a temporary situation, so recovery
                # might still be possible; attempt to shut down the
                # Cisco AnyConnect CLI instance and return with a
                # failure
                try:
                    vpn_proc.terminate(force=True)
                    wexpect.host.run('taskkill /f /im vpncli.exe')
                except Exception as error:
                    print('Unable to terminate child process (330).')
                return 'Fail'
            if index == 2:
                # The Cisco VPN client driver needs a system reboot
                print('The VPN client driver encountered an error.')
                print('Please restart your system, then try again.')
                print('---- Start diagnostic information ----')
                print(vpn_proc.before)
                print('----  End diagnostic information  ----')
                # The Cisco AnyConnect CLI has requested a system
                # reboot, and there is no way to recover; attempt
                # to shut down the Cisco AnyConnect CLI instance
                # and return with a failure
                try:
                    vpn_proc.terminate(force=True)
                    wexpect.host.run('taskkill /f /im vpncli.exe')
                except Exception as error:
                    print('Unable to terminate child process (347).')
                return 'Fail'
            if index == 3:
                # Timeout waiting for the VPN banner accept response
                print('Banner accept response timeout.')
                print('---- Start diagnostic information ----')
                print(vpn_proc.before)
                print('----  End diagnostic information  ----')
                # This could be a temporary situation, so recovery
                # might still be possible; attempt to shut down the
                # Cisco AnyConnect CLI instance and return with a
                # failure
                try:
                    vpn_proc.terminate(force=True)
                    wexpect.host.run('taskkill /f /im vpncli.exe')
                except Exception as error:
                    print('Unable to terminate child process (363).')
                return 'Fail'
            # Success case, if two final checks are satisfied
            vpn_proc.expect('Connected to ' + vpnsitename)
            vpn_proc.expect('VPN>')
        except Exception as error:
            # An unanticipated error occurred
            print('Got an unexpected VPN banner accept error.')
            print('Unable to successfully accept the VPN banner.')
            print('---- Start diagnostic information ----')
            print(vpn_proc.before)
            print('----  End diagnostic information  ----')
            # This could be a temporary situation, so recovery
            # might still be possible; attempt to shut down the
            # Cisco AnyConnect CLI instance and return with a
            # failure
            try:
                vpn_proc.terminate(force=True)
                wexpect.host.run('taskkill /f /im vpncli.exe')
            except Exception as error:
                print('Unable to terminate child process (383).')
            return 'Fail'

        # The VPN connection is now established, and the
        # Cisco AnyConnect CLI is waiting for a command
        return 'Good'

        # End of open()


    def close(self):
        """Close the VPN connection

        Closes a VPN connection that was opened using the Cisco
        AnyConnect CLI instance.

        Returns 'Good' for success and 'Fail' for failure.
        Failures also result in error messages being sent to the
        console.

        wexpect note: Each major step provides its own stimulus
        and verifies the response with one or more 'expect' items
        before the control flow moves on to the next step. Note
        that a log file can be used with wexpect for debugging,
        but it will record and reveal VPN usernames and passwords.

        vpncli note: Short delays are needed between CLI commands,
        otherwise one or more commands might be ignored by the CLI.
        The approach for working with vpncli states and behaviors
        comes from empirical evidence, which may be incomplete.
        """

        # Globals
        global vpn_proc         # Spawned process ID

        # Return 'Good' if the child process is not running,
        # because this means the VPN is already closed; this
        # allows close() to be called at any time, such as when
        # the calling program is being stopped with Control-C
        if not vpn_proc.isalive():
            return 'Good'

        # Close the VPN connection
        try:
            time.sleep(VPNCLI_CMD_DELAY)
            vpn_proc.sendline('disconnect')
            vpn_proc.expect('VPN>')
        except Exception as error:
            print('Unable to disconnect the VPN for close().')
            print('---- Start diagnostic information ----')
            print(vpn_proc.before)
            print('----  End diagnostic information  ----')
            # There is no way to recover; attempt to shut down
            # the Cisco AnyConnect CLI instance and return with
            # a failure
            try:
                vpn_proc.terminate(force=True)
                wexpect.host.run('taskkill /f /im vpncli.exe')
            except Exception as error:
                print('Unable to terminate child process (442).')
            return 'Fail'

        # Exit the Cisco AnyConnect CLI
        try:
            time.sleep(VPNCLI_CMD_DELAY)
            vpn_proc.sendline('exit')
            vpn_proc.expect('>')
        except Exception as error:
            print('Unable to exit Cisco AnyConnect CLI for close().')
            print('---- Start diagnostic information ----')
            print(vpn_proc.before)
            print('----  End diagnostic information  ----')
            # There is no way to recover; attempt to shut down
            # the Cisco AnyConnect CLI instance and return with
            # a failure
            try:
                vpn_proc.terminate(force=True)
                wexpect.host.run('taskkill /f /im vpncli.exe')
            except Exception as error:
                print('Unable to terminate child process (462).')
            return 'Fail'

        # Terminate the child process that was spawned by open()
        # and ensure the Cisco AnyConnect CLI instance is shut down
        try:
            vpn_proc.terminate(force=True)
            wexpect.host.run('taskkill /f /im vpncli.exe')
        except Exception as error:
            print('Unable to terminate child process (471).')
            return 'Fail'

        # Return 'Good' for sucessfully closing the VPN connection
        return 'Good'

        # End of close()
