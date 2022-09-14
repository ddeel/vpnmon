# vpnmon -- VPN Monitor

vpnmon is a monitoring tool that periodically checks the availability of computer systems within a facility that is connected to the Internet by a VPN gateway running Cisco AnyConnect. It runs on a Windows computer system located outside the facility, so it can provide a warning when the VPN gateway or some of the computer systems within the facility fail or stop responding.

vpnmon works by periodically running test cycles, where each test cycle performs the following sequence of operations:

- Verify that the facility VPN is available via the Internet.

- If the VPN is available, attempt to open a VPN connection.

- If the VPN connection opens, verify the availability of selected
  computer systems within the facility via the VPN connection, and
  then close the VPN connection.

- Report summary results for all attempted operations to the
  command line interface used to start vpnmon.

- Record results for all attempted operations in a datalog file.

- If more test cycles have been requested, wait for a specified
  period of time before running the next test cycle.

----


## Current Status

### Version: 1.0.0

Initial version placed on GitHub.

### Functionality supported:

- Checks the availability of a specified VPN site.

- Checks the availability of connections with the facility VPN site by opening a VPN connection.

- Checks the availability of selected computer systems within the facility after a VPN connection with the facility has been established.

- Uses sound to alert the user whenever availability errors occur. This provides the user with immediate alerts about availability errors, and it  also helps to minimize the attention needed from the user while the program is running and availability issues are not being found.

- Uses multiple network ping operations to check availability. This helps indicate the nature of the availability when the test is done, by providing one of three results: A "Good" result means the target responded to all of the network pings; a "Warn" result means it did not respond to some of the network pings; and a "Fail" result means it did not respond to any of the network pings.

- Includes support for adding additional functionality via other programs that accept vpnmon's datalog file as input. An example would be a program that periodically analyzes vpnmon datalog file updates and sends email notifications whenever predefined error situations are detected.

### Functionality that may be added in a future release:

- An ability to send email notifications.

- An ability to limit datalog file size.

----


## Installing vpnmon

### Required environment

vpnmon requires the following environment:

- Windows 10 or later.

- Python 3.6 or later.

- Internet access.

- Cisco AnyConnect Secure Mobility Client v4.7 or later.

- Valid credentials for opening VPN connections with the facility.

### Installation steps

These installation steps assume that Python and the Cisco AnyConnect Secure Mobility Client software have already been installed on the Windows system where vpnmon will be running:

- Copy the vpnmon project files into a directory on the Windows system.

- Open a command line session, 'cd' to the directory where the
  vpnmon project files are kept, and install the required Python
  packages with this command:

    **pip install -r requirements.txt**

    Note that vpnmon is currently not compatible with the Python
    virtual environments virtualenv or venv, so it is necessary
    to install the required Python packages in the global Python
    environment.

- Set up the vpnmon targets file, which contains the URLs or IP addresses and human-readable names of the computer systems that are to be checked within the facility via the VPN connection. The default name of this file is *vpnmon_targets.csv*, but this name can be overridden by a command line argument or by an entry in the vpnmon parameters file. This is a CSV (comma separated values) file, so it can be updated with a text editor or any spreadsheet program that handles CSV files.

    The vpnmon targets file has a simple format. It specifies one target computer system per line, with each line having the URL or IP address of the target computer system, followed by a comma character, followed by the human-readable computer system name. There should not be any spaces on either side of the comma character on each line. The human-readable computer system name can include spaces and does not need to be enclosed in double-quote characters. 

    If the vpnmon targets file is empty or cannot be found, no target computer systems will be tested via the VPN gateway. An empty version of the default *vpnmon\_targets.csv* file is included as part of the vpnmon distribution, and it can easily be modified as needed for a specific facility.

- Optional: Set up the vpnmon parameters file called *vpnmon_params.csv*. This file is optional but convenient for setting vpnmon parameters that do not change very often. This is a CSV (comma separated values) file, so it can be updated with a text editor or any spreadsheet program that handles CSV files. (See the "vpnmon parameters file" section below for information about the vpnmon parameters that can be set.)

vpnmon should now be ready to run in a basic configuration where its input arguments come from the command line that starts vpnmon.

----


## Running vpnmon

vpnmon runs from the command line and accepts several arguments that
establish inputs, outputs, and various aspects of vpnmon behavior.
These arguments can come from the command line, from a parameters
file (more about this below), or from a combination of the command
line and the parameters file.

In cases where an argument is present in both the command line and
the parameters file, the command line argument always overrides
the parameters file argument.

To run vpnmon, open a command line session, 'cd' to the directory where the vpnmon project files are kept, and enter this command:

**python vpnmon.py *arguments***

The vpnmon command line *arguments* are all optional, and zero or more of them can be used in any combination in the command that starts vpnmon. Most of the arguments support both a long form (begins with "--") and a short form (begins with "-"):

**--help** or **-h**

Show the vpnmon help message and immediately exit.

**--version** or **-v** or   **-V**

Show the vpnmon version and immediately exit.

**--vpnname VPNNAME** or **-vpnname VPNNAME**

VPNNAME is a human-readable name for the facility VPN. VPN names that include spaces should be enclosed in double-quote (") characters. The default value for VPNNAME is "VPN Gateway", but this can be changed by this command line argument or by an entry in the vpnmon parameters file.

**--vpnurlip VPNADDRESS** or **-vpnurlip VPNADDRESS**

VPNADDRESS is the URL or IP address for where the facility VPN can be found on the Internet. The default value for VPNADDRESS is an empty string, so it **must** be set to its correct value by this command line argument or by an entry in the vpnmon parameters file.

**--username USERNAME** or **-user USERNAME**

USERNAME is the VPN account username. The default value for USERNAME is an empty string, so it **must** be set to its correct value by this command line argument or by an entry in the vpnmon parameters file.

**--password PASSWORD** or **-pass PASSWORD**

PASSWORD is the VPN account password. The default value for PASSWORD is an empty string, so it **must** be set to its correct value by this command line argument or by an entry in the vpnmon parameters file.

**--targets TARGETSFILE** or **-targets TARGETSFILE**

TARGETSFILE is the file name of a CSV (comma separated values) file that specifies the URL or IP addresses and human-readable names of the computer systems that need to be checked within the facility via the VPN connection. The default value for TARGETSFILE is *vpnmon_targets.csv*, but this can be overridden by this command line argument or by an entry in the vpnmon parameters file. If this CSV file is missing or empty, no computer systems within the facility will be checked via the VPN.

**--cycles CYCLES** or **-cycles CYCLES**

CYCLES is an integer value for the number of test cycles to run. The default value for CYCLES is 200, but this can be overridden by this command line argument or by an entry in the vpnmon parameters file. Values between 1 and 200 are strongly recommended for CYCLES.

**--delay SECONDS** or **-delay SECONDS**

SECONDS is an integer value for the number of seconds to wait between test cycles. The default value for CYCLES is 1800 (30 minutes), but this can be overridden by this command line argument or by an entry in the vpnmon parameters file.

**--datalog DATALOGFILE** or **-datalog DATALOGFILE**

DATALOGFILE is the file name for a CSV (comma separated values) file where the vpnmon datalog is to be kept. The default value for DATALOGFILE is *vpnmon_datalog.csv*, but this can be overridden by this command line argument or by an entry in the  vpnmon parameters file. vpnmon will create this file if it does not exist. If the file already exists, then vpnmon will append datalog information to the existing file.

**--quiet** or **-quiet**

Prevent the computer system that is running vpnmon from playing a sound whenever a test failure occurs. The default is to play a sound, but this can be overridden by this command line argument or by an entry in the vpnmon parameters file.

----


## vpnmon parameters file

Most of the vpnmon command line arguments can also be set by an optional CSV parameters file named *vpnmon\_params.csv* in the directory where *vpnmon.py* is kept. This file is optional but convenient for setting vpnmon parameters that do not change frequently.

The vpnmon parameters file is a CSV (comma separated values) file, where each entry is on a separate line, and a comma character separates the parameter name from the parameter value, with no space characters adjacent to the comma character. Space characters can be used within parameter values that are strings.

Zero or more of the following supported parameters file entries can be used in any order:

**vpnname,VPNNAME**

VPNNAME is a human-readable name for the facility VPN. In the vpnmon parameters file, VPN names that include spaces should NOT be enclosed in double-quote (") characters. The default value for VPNNAME is "VPN Gateway", but this can be changed by a command line argument or by this entry in the vpnmon parameters file.

**vpnurlip,VPNADDRESS**

VPNADDRESS is the URL or IP address for where the facility VPN can be found on the Internet. The default value for VPNADDRESS is an empty string, so it **must** be set to its correct value by a command line argument or by this entry in the vpnmon parameters file.

**username,USERNAME**

USERNAME is the VPN account username. The default value for USERNAME is an empty string, so it **must** be set to its correct value by a command line argument or by this entry in the vpnmon parameters file.

**password,PASSWORD**

PASSWORD is the VPN account password. The default value for PASSWORD is an empty string, so it **must** be set to its correct value by a command line argument or by this entry in the vpnmon parameters file.

**targets,TARGETSFILE**

TARGETSFILE is the file name of a CSV (comma separated values) file that specifies the URL or IP addresses and human-readable names of the computer systems that need to be checked within the facility via the VPN connection. The default value for TARGETSFILE is *vpnmon_targets.csv*, but this can be overridden by a command line argument or by this entry in the vpnmon parameters file. If this CSV file is missing or empty, no computer systems within the facility will be checked via the VPN.

**cycles,CYCLES**

CYCLES is an integer value for the number of test cycles to run. The default value for CYCLES is 200, but this can be overridden by a command line argument or by this entry in the vpnmon parameters file. Values between 1 and 200 are strongly recommended for CYCLES.

**delay,SECONDS**

SECONDS is an integer value for the number of seconds to wait between test cycles. The default value for CYCLES is 1800 (30 minutes), but this can be overridden by a command line argument or by this entry in the vpnmon parameters file.

**datalog,DATALOGFILE**

DATALOGFILE is the file name of a CSV (comma separated values) file where the vpnmon datalog is to be kept. The default value for DATALOGFILE is *vpnmon_datalog.csv*, but this can be overridden by a command line argument or by this entry in the vpnmon parameters file. vpnmon will create this file if it does not exist. If the file already exists, then vpnmon will append datalog information to the existing file.

**quiet,QUIET**

Prevent (or allow) the computer system that is running vpnmon from playing a sound whenever a test failure occurs. The only valid values for QUIET are True and False. The default value for QUIET is False, but this can be overridden by a command line argument or by this entry in the vpnmon parameters file.

### Basic parameters file for vpnmon

The vpnmon parameters file is optional and does not need to exist for vpnmon to work, but a basic parameters file named *vpnmon\_params.csv* is included as part of the vpnmon distribution. It sets all the parameters to the same default values that vpnmon uses when it cannot find the optional vpnmon parameters file.

Command line arguments always override parameters file arguments, so the basic parameters file effectively only serves as a ready-to-use template that can be easily customized to fit the needs of specific situations.

NOTE: vpnmon will not run if it is started with no arguments set by the command line and no arguments set by the parameters file. This is because three VPN-specific parameters (vpurlip, username, and password) default to empty strings, and they **must** be set to their proper values by the user before vpnmon can be run successfully.

----


## Example commands for running vpnmon

Three example commands for running vpnmon are shown below. The first is for a command that does not rely upon the vpnmon parameters file (*vpnmon\_params.csv*), the second is for a command that works in conjunction with the vpnmon parameters file, and the third shows a command with an argument that overrides a parameters file argument.

### Example command that does not rely upon the parameters file

The basic parameters file distributed with vpnmon contains default vpnmon parameter values. If this file is deleted or unchanged, then the command that starts vpnmon must set all the necessary vpnmon parameters to their non-default values, and a minimal command to start vpnmon can look like this:

**python vpnmon.py -vpnurlip VADDRESS -user VUSER -pass VPASS**

This command only sets values for these necessary parameters:

- vpnurlip = VADDRESS
- VPN username = VUSER
- VPN password = VPASS

The command assumes that all other vpnmon parameters remain at their default values. For this to be the case, the vpnmon parameters file must either not exist or still be unchanged from the distributed version that only contains the default vpnmon parameter values. When this is true, the remaining vpnmon parameters will have these values:

- vpnname = VPN Gateway
- targets = vpnmon_targets.csv
- cycles = 200
- delay = 1800
- datalog = vpnmon_datalog.csv
- quiet = FALSE

This command will make vpnmon run for 200 test cycles, with a delay of 30 minutes (1,800 seconds) between test cycles.

### Example command that uses the parameters file

The basic parameters file distributed with vpnmon can be edited to contain parameter values that are appropriate for a specific facility. Once this is done, the command to start vpnmon can become very straightforward:

**python vpnmon.py**

This command assumes that the vpnmon parameters file (*vpnmon\_params.csv*) sets the vpnmon parameters to appropriate values, such as these:

- vpnname = VPN Gateway
- vpnurlip = VADDRESS
- VPN username = VUSER
- VPN password = VPASS
- targets = vpnmon_targets.csv
- cycles = 200
- delay = 1800
- datalog = vpnmon_datalog.csv
- quiet = FALSE

(This list shows the parameters file values, not the file contents.)

This command will make vpnmon run for 200 test cycles, with a delay of 30 minutes (1,800 seconds) between test cycles.

### Example command that overrides a parameters file value

The command that starts vpnmon can include arguments that override the values set by the parameters file:

**python vpnmon -delay 600**

This command assumes that the vpnmon parameters file (*vpnmon\_params.csv*) sets the vpnmon parameters to appropriate values, such as these:

- vpnname = VPN Gateway
- vpnurlip = VADDRESS
- VPN username = VUSER
- VPN password = VPASS
- targets = vpnmon_targets.csv
- cycles = 200
- delay = 1800
- datalog = vpnmon_datalog.csv
- quiet = FALSE

(This list shows the parameters file values, not the file contents.)

This command will make vpnmon run for 200 test cycles, with a delay of 10 minutes (600 seconds) between test cycles. This is because the command line argument for *delay* overrides the parameters file value for *delay*.

----


## Stopping vpnmon

vpnmon stops by itself after it has performed the requested number of test cycles.

The user can also stop vpnmon at any time, by entering Control-C in the command line session used to start vpnmon.

In both cases, vpnmon ensures that the VPN connection and the vpnmon datalog file are closed before the program ends.

----


## Technical Overview

This section provides an overview of the vpnmon component parts and
briefly explains how they work together to periodically check the availability of computer systems within a facility that is connected to the Internet by a VPN gateway running Cisco AnyConnect.

vpnmon is written in Python, and the code is commented to provide more information than is given in this overview.


### vpnmon components

The files found in the vpnmon directory are as follows.

##### Datalog file (default name is *vpnmon\_datalog.csv*)

This CSV (comma separated values) file contains output data from vpnmon.

*vpnmon\_datalog.csv* is the default name for the datalog file, but this file name can be overridden by a command line argument or by an entry in the vpnmon parameters file.

If the datalog file does not exist or cannot be found when vpnmon runs, vpnmon will create a new datalog file and output data to it. If the datalog file already exists when vpnmon runs, then vpnmon will append output data to it.

A datalog file is not included as part of the vpnmon distribution, since a new datalog file will be created when vpnmon runs.

##### Parameters file (name is always *vpnmon\_params.csv*)

This CSV (comma separated values) file sets values for zero or more of the parameters that determine inputs, outputs, and various aspects of vpnmon behavior. It is kept in the directory where *vpnmon.py* is kept, and it can be updated with a text editor or any spreadsheet program that handles CSV files.

If the parameters file does not exist or cannot be found when vpnmon runs, vpnmon sends a message to the command line session saying it is running without a parameters file, and then uses default values for any arguments that are not set by command line arguments.

The parameters file is optional but convenient for setting vpnmon parameters that do not change frequently, such as the URL or IP address of the VPN gateway, the VPN login name, and the VPN login password.

A basic parameters file named *vpnmon\_params.csv* is included as part of the vpnmon distribution. It sets all the parameters to the same default values that vpnmon uses when it cannot find the optional vpnmon parameters file.

##### Targets file (default name is *vpnmon\_targets.csv*)

This CSV (comma separated values) file specifies the URL or IP addresses and human-readable names of the computer systems that need to be checked within the facility via the VPN connection. It can be updated with a text editor or any spreadsheet program that handles CSV files.

*vpnmon\_targets.csv* is the default name for the targets file, but this file name can be overridden by a command line argument or by an entry in the vpnmon parameters file.

The targets file is optional but required for checking computer systems within a facility via the VPN connection. If this file is empty or cannot be found, no target computer systems will be tested via the VPN gateway.

This CSV file specifies one target computer system per line, with each line having the URL or IP address of the target computer system, followed by a comma character, followed by the human-readable computer system name. There should not be any spaces on either side of the comma character on each line. The human-readable computer system name can include spaces and does not need to be enclosed in double-quote characters. 

An empty targets file named *vpnmon\_targets.csv* is included as part of the vpnmon distribution.

##### \_\_init\_\_.py

The presence of this file makes the vpnmon directory a Python package.

##### LICENSE.txt

This text file contains the BSD 3-Clause License that covers the vpnmon source code.

##### README.md

This Markdown file contains the README source for vpnmon. (This is the file you are currently reading.)

##### requirements.txt

This text file lists the Python packages needed by vpnmon. It is used by the Python "pip" command to set up the environment for running vpnmon.

##### vpnmon.py

This module contains the vpnmon main() method, and is directly invoked by the user to start vpnmon.

##### vpnmon\_shared\_data.py

This module handles data that is shared between vpnmon modules.

##### vpnmon\_utilities.py

This module contains several utility methods used by vpnmon:

- get\_params()    - Get operational parameters for vpnmon
- get\_targets()   - Get a list of targets to test via the VPN
- pinger()        - Ping a URL or IP address multiple times
- webping()       - See if a web site is responding
- date\_and\_tod()  - Return date and time of day as a tuple
- sounder()       - Make one or more sounds to get attention
- datalogger()    - Write test results to a datalog file

##### vpnmon\_version.py

This module sets the vpnmon version number.

##### vpnmon\_vpnclient.py

This module contains the vpnmon VPNClient class that interacts with VPN gateways running Cisco AnyConnect. It provides open() and close() methods that use the Windows Cisco AnyConnect Secure Mobility Client CLI software to open and close VPN connections.

The VPNClient class imposes several restrictions on the computer system that runs vpnmon:

- It only runs on Windows, because it uses the Windows Cisco AnyConnect Secure Mobility Client CLI software, and it also uses the Python "wexpect" import, which is specific to Windows.

- It requires the user to only run one Cisco AnyConnect application at a time, because this is a requirement for using the Windows Cisco AnyConnect Secure Mobility Client CLI software.

- It does not work with Python virtual environments like virtualenv or venv, because the Python "wexpect" import is not compatible with these virtual environments.

##### Run25.bat

This is a Windows batch file that runs a command 25 times in a row during a Windows command line session.


### How vpnmon works

This section provides an overview of how the vpnmon components work together to to periodically check the availability of computer systems within a facility that is connected to the Internet by a VPN gateway running Cisco AnyConnect. The overview covers what happens when vpnmon starts up and runs test cycles, and it also covers what happens when vpnmon stops.

##### vpnmon startup

The *vpnmon.py* module coordinates vpnmon startup by working with other
modules to implement the following sequence:

- Enable the catching of Control-C
- Determine operational parameters
- Initialize and run test cycle loop operations

###### Enable the catching of Control-C

*vpnmon.py* defines and initializes a *signal\_handler()* method that will be called if the user enters Control-C in the Windows command line session that started vpnmon.

*signal\_handler()* ensures that the VPN connection and the vpnmon datalog file are closed before vpnmon stops as a result of the user entering Control-C.

###### Determine operational parameters

*vpnmon.py* calls *getparams()* in *vpnmon\_utilities.py* to establish values for the operational parameters that can be set by the user.

*getparams()* establishes the operational parameter values by taking values from three sources, in order. First, default values are used. Second, values from the *vpnmon\_params.csv* file are used. Third, values from the command line are used. This ordering enables the following:

- Default values are always set for all parameters 
- The *vpnmon\_params.csv* file is optional
- The *vpnmon\_params.csv* file entries are individually optional
- The *vpnmon\_params.csv* file entries override default values
- Command line arguments are individually optional
- Command line arguments override *vpnmon\_params.csv* file entries

###### Initialize and run test cycle loop operations

After determining its operational parameters, *vpnmon.py* initializes and executes a test cycle loop that repeatedly does the following:

- Verify that the facility VPN is available via the Internet, using the *pinger()* method in *vpnmon\_utilities.py*.

- If the VPN is available, attempt to open a VPN connection, using the *open()* method in *vpnmon\_vpnclient.py*. Note that successfully opening a VPN connection with a Cisco AnyConnect gateway typically takes up to about 15 seconds, and failures can take up to about 2 minutes.

- If the VPN connection opens, do the following:
  - Verify the availability of selected computer systems within the facility via the VPN connection, using the *pinger()* method in *vpnmon\_utilities.py*.

  - Close the VPN connection, using the *close()* method in *vpnmon\_vpnclient.py*. Note that successfully closing a VPN connection with a Cisco AnyConnect gateway typically takes up to about 10 seconds.

- Report summary results for all attempted operations to the command line interface used to start vpnmon.

- Record dated and timestamped results for all attempted operations in the datalog file, using the *datalogger()* method in *vpnmon\_utilities.py*.

- If more test cycles have been requested, wait for a specified period of time before running the next test cycle.

##### vpnmon shutdown

When the number of requested test cycles has been completed, vpnmon will exit. This is the normal way for vpnmon to stop running.

The user can also stop vpnmon at any time by entering Control-C in the command line session that started vpnmon. This will send control to the *signal\_handler()* method in *vpnmon.py*, which does two things before allowing vpnmon to exit:

- Ensures that the VPN connection is closed, by calling the *close()* method in *vpnmon\_vpnclient.py*.

- Ensures that the vpnmon datalog file is closed, by calling the *close()* method for the datalog file object.

----


## Developer notes

This section provides some additional information about the vpnmon code.

### Cisco AnyConnect Secure Mobility Client software

If the Windows Cisco AnyConnect Secure Mobility Client is not already installed on the Windows system that will be running vpnmon, contact the people who manage the VPN gateway and the facility. They should be able to provide information about how to install the necessary software on a Windows system, and they should also be able to provide login credentials (username and password information) for users who have been authorized to access the facility via the VPN gateway.

### Only one Cisco AnyConnect application can run at a time

Only one Cisco AnyConnect application can be running at a time on a Windows system, so the *open()* method in *vpnmon_vpnclient.py* starts by forcing the termination of all other Cisco AnyConnect applications that may be running on the Windows system. This includes terminating the Cisco AnyConnect user interface that allows users to manually open VPN connections. The other Cisco AnyConnect applications can be manually restarted, but only when vpnmon is no longer running.

### Cisco AnyConnect software updates

When the *open()* method in *vpnmon_vpnclient.py* attempts to open a VPN connection with a Cisco AnyConnect gateway, the Cisco software can decide that it needs to update itself on the Windows system. This update does get done, but it causes vpnmon to fail to open the VPN connection. When this happens, it can take up to roughly 2 minutes for vpnmon to stop with an error, and the user may see a Cisco dialog that must be responded to before vpnmon can be successfully restarted.

### Control-C behavior

Control-C always causes vpnmon to stop when it is entered in the command  line session that started vpnmon, and it usually works very quickly, but there is a rare case where it can take up to roughly 2 minutes for vpnmon to stop. This can happen if the user enters Control-C when vpnmon has just started to open a VPN connection. When it happens, vpnmon will finally stop as expected, but only after a timeout of roughly 2 minutes has occurred.

### Handling the *cycles* argument

vpnmon was designed to run with for an infinite number of test cycles by setting the *cycles* argument to -1, but the current recommendation is to only run vpnmon with the *cycles* argument set to values between 1 and 200.

This is because there is an as-yet-undebugged problem that results in a failure after running too many test cycles in a single vpnmon run. When the problem happens, the Windows system hangs, and then it crashes during the necessary reboot to clear the problem. A memory leak is suspected, probably within the Python "wexpect" package or the AnyConnect software, but this is TBD.

Limiting the vpnmon *cycles* argument to values between 1 and 200 avoids the problem, but this limits the vpnmon time coverage to roughly (200 x *delay* / 3600) hours. With the default value of 1,800 seconds for the *delay* between test cycles, this is roughly 100 hours.

The vpnmon distribution includes a Windows batch file called *Run25.bat* that can help extend the number of vpnmon test cycles by simply running the same vpnmon command 25 times in succession.

To use *Run25.bat*, open a command line session, 'cd' to the directory where the vpnmon project files are kept, and enter this command:

**Run25 python vpnmon.py *arguments***

The *arguments* are the same as the ones used for individual vpnmon commands. Running with default values for both *cycles* and *delay*, *Run25.bat* can increase the possible vpnmon time coverage to roughly 2,500 hours.

(Run25 is a hack, but it successfully extends the VPN monitoring time coverage while avoiding the Windows system hang and reboot problem.)

### Internet connection failures

vpnmon fails with a "socket.gaierror" error when these situations occur:

- An invalid URL is used for the vpnmon *vpnurlip* argument.

- The Windows system Internet connection fails or is disabled.

### Fatal errors detected in *vpnmon\_utilities.py*

The following fatal error situations are detected in *vpnmon\_utilities.py*. They all cause vpnmon to terminate immediately, after sending an error message to the command line session that started vpnmon:

- The vpnmon parameters file (*vpnmon\_params.csv*) exists but could not be read. This is detected by *get\_params()*, and causes the error message "Failed to read the vpnmon params file".

- The vpnmon targets file (default name *vpnmon\_targets.csv*) exists but could not be read. This is detected by *get\_targets()*, and causes the error message "Failed to read the vpnmon params file".

- The vpnmon datalog file (default name *vpnmon\_datalog.csv*) cannot be accessed. This is detected by *datalogger()*, and causes the error message "Failed to access the vpnmon data file".

### Fatal errors detected in *vpnmon\_vpnclient.py*

The following fatal error situations are detected in *vpnmon\_vpnclient.py*. They all cause vpnmon to terminate immediately, after sending an error message to the command line session that started vpnmon: 

- Unable to terminate all other Cisco AnyConnect applications. This is detected by *open()*, and causes the error message "Unable to end an existing AnyConnect UI or CLI".

- Unable to spawn a child process required by the Python "wexpect" package. This is detected by *open()*, and causes the error message "Unable to spawn child process".

- Unable to use the Cisco AnyConnect CLI. This is detected by *open()*, and causes the error message "Unable to use the Cisco AnyConnect CLI".

- Unable to disconnect a VPN connection that was already open when *open()* was called. This is detected by *open(_)*, and causes the error message "Unable to disconnect the VPN for open()".

----
----
