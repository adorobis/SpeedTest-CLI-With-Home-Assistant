It is a simplified way of implementing a wrapper around the official speedtest-cli, originally developed in this repo:
https://github.com/tommyjlong/SpeedTest-CLI-With-Home-Assistant

# SpeedTest To Home Assistant
This project provides a way for Home Assistant to run the OKLA official `speedtest.net` binary (binary running on Linux) using an automation.  It consists of the following:
* OKLA [Speedtest-cli binary](https://www.speedtest.net/apps/cli)
* Python Code to launch the Speedtest-cli binary, receive the results, parse them, and print the result in flat json format.
* A Home Assistant command_line sensor and two template sensors to represent the results.

Background - Home Assistant provides a native SpeedTest integration which uses a [third party Python code](https://github.com/sivel/speedtest-cli) to run the actual tests.  The third party code attempts to mimic the official speedtest-cli but the test results of the third party code does not always reflect that of the official speedtest-cli.  

Note: There are other ways for HA to run the Speedtest-CLI binary such as the one provided by the Home Assistant Community Forum [here](https://community.home-assistant.io/t/add-the-official-speedtest-cli/161915/15).

# Instructions

## Setup Your Downloaded Github Files
* Create a directory in you Home Assistant configuration directory, for example named `shell_commands` (which is the default for this project) and copy the `speedtest-cli-2ha.py` to this directory.  Use a text editor and edit the `speedtest-cli-2ha.py` and fill out the information according to the instructions within this file.

* Goto the OOKLA site mentioned above and get one of the Linux binaries that will run on your system.  You can usually find out by typing in your linux shell: `$uname -m`  which should return something like `x86_64`.  Download that tar file and extract its binary and put it into this same directory (ex. `shell_commands`).  Rename the binary `speedtest.bin`.  If you are running Home Assistant with HassOS, you can do some of this with combinations of the Terminal and SSH add-on and the Samba add-on.

* Accept the Speedtest-CLI EULA. 
  * Method I - Accept the EULA by executing the binary by typing `$ ./speedtest.bin`.  You will get prompted to accept the EULA.  Once accepted, it will store a file away that will allow it to remember this so that next time you won't be prompted again.  It will continue to run and automatically pick a nearby OOKLA server and provide textual results.  The binary is now useable by the python code.
  * Method II - There can be however a problem with this. The file that speedtest.bin writes to after accepting the EULA gets written to the user's home direcotry and  this file may get removed on the next HA upgrade (if using containers) causing the user to have to re-run speedtest.bin by hand in order to accept the EULA.  A preferred alternative is to read the [EULA on-line](https://www.speedtest.net/about/eula) and if the EULA is acceptable, then change the following lines inside the `speedtest-cli-2ha.py` <br/>

From:
```
process = subprocess.Popen([SPEEDTEST_PATH,'--format=json','--precision=4',speed_test_server_id],
```
To:
```
process = subprocess.Popen([SPEEDTEST_PATH,'--format=json','--precision=4', '--accept-license', '--accept-gdpr', speed_test_server_id],
```

## HA Configuration and Automation
* Configure a command_line sensor e.g.: Adjust path and name of the python script to your situation.
```
command_line:
  - sensor:
      name: Speedtest Ping
      command: "python3.8 /root/speedtest-cli-2ha.py"
      value_template: "{{ value_json.ping | round(1) }}"
      command_timeout: 30
      scan_interval: 1800
      unit_of_measurement: ms
      json_attributes:
        - 'download'
        - 'upload'
        - 'server_name'
        - 'isp'
```
Configure two template sensors to get download and upload speeds from the command_line sensor:
```
template:
  - sensor:
    - name: Speedtest Download
      state: '{{ state_attr("sensor.speedtest_ping", "download") | round(2) }}'
      unit_of_measurement: Mbit/s
    - name: Speedtest Upload
      state: '{{ state_attr("sensor.speedtest_ping", "upload") | round(2) }}'
      unit_of_measurement: Mbit/s
```

## Testing and Debugging
Test in the HA command line that the python script executes properly end returns the proper json output.

Go into the python file and set the `DEBUG` to 1, and `CONSOLE` to 1, then type `$ ./speedtest-cli-2ha.py`.  This will run the speedtest and provide debug information to get ideas of what the problem is.  
