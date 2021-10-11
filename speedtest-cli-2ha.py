# -*- coding: utf-8 -*-


import subprocess
import json
import logging
import logging.handlers #Needed for Syslog
import sys

# Configuration
SPEEDTEST_SERVERID = '7175'
SPEEDTEST_PATH = 'speedtest'

# Setup Logger 
DEBUG   = 0 #set to 1 to get debug information.
CONSOLE = 0 #set to 1 to send output to stdout, 0 to local syslog

_LOGGER = logging.getLogger(__name__)
if CONSOLE:
    formatter = \
        logging.Formatter('%(message)s')
    handler1 = logging.StreamHandler(sys.stdout)
    handler1.setFormatter(formatter)
    handler1.setLevel(logging.NOTSET)
    _LOGGER.addHandler(handler1)
else:
    formatter2 = \
        logging.Formatter('%(levelname)s %(asctime)s %(filename)s - %(message)s')
    handler2 = logging.handlers.SysLogHandler(address = '/dev/log')
    handler2.setFormatter(formatter2)
    handler2.setLevel(logging.NOTSET)
    _LOGGER.addHandler(handler2)

if DEBUG:
  _LOGGER.setLevel(logging.DEBUG)
else:
  _LOGGER.setLevel(logging.NOTSET)




# Run Speedtest
_LOGGER.debug('Running Speedtest')
if SPEEDTEST_SERVERID == '':
  speed_test_server_id=''
else:
  speed_test_server_id = '--server-id=' + SPEEDTEST_SERVERID

process = subprocess.Popen([SPEEDTEST_PATH,
                     '--format=json',
                     '--precision=4',
                     '--accept-license',
                     '--accept-gdpr',
                     speed_test_server_id],
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE,
                     universal_newlines=True)
stdout, stderr = process.communicate()
_LOGGER.debug('Stdout: %s', stdout)
_LOGGER.debug('Stderr: %s', stderr)

# Speed Test Results - (from returned JSON string)
st_results = json.loads(stdout)
down_load_speed = st_results["download"]["bandwidth"]*8/1000000
up_load_speed = st_results["upload"]["bandwidth"]*8/1000000
ping_latency = st_results["ping"]["latency"]
isp = st_results["isp"]
server_name = st_results["server"]["name"]
url_result = st_results["result"]["url"]

dictionary ={
    "ping" : ping_latency,
    "download" : down_load_speed,
    "upload" : up_load_speed,
    "server_name" : server_name,
    "isp" : isp
}

json_result=json.dumps(dictionary, indent = 4)

print(json_result)

_LOGGER.info('Downstream BW: %s',down_load_speed)
_LOGGER.info('Upstram BW: %s',up_load_speed)
_LOGGER.info('Ping Latency: %s', ping_latency)
_LOGGER.info('ISP: %s', isp)
_LOGGER.info('Server name: %s',server_name)
_LOGGER.info('URL results: %s',url_result)
_LOGGER.info('---------------------------------')

# _LOGGER.debug('Posting to HA SpeedTest Sensors')
# ret1 = HAPost("download",down_load_speed,"Mbit/s","Speedtest Download","mdi:speedometer")
# ret2 = HAPost("upload",up_load_speed,"Mbit/s","Speedtest Upload","mdi:speedometer")
# ret3 = HAPost("ping",ping_latency,"ms","Speedtest Ping","mdi:speedometer")
# _LOGGER.debug('Return code from POST Method calls %s %s %s', ret1, ret2, ret3)
