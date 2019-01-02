#!/usr/bin/python
#
# bands.py
#
# 01/01/2019
#
# Brian Graves - VA3DXV
#
# va3dxv@gmail.com
#
# https://github.com/va3dxv
#
# pulls band predictions from hamqsl.com
#
# This script requires access to http://api.voicerss.org (it's free)
# as well as lame and sox to create the .ul file for asterisk
#
# Run this file from roots crontab to create the audio file every hour
# 0 */1 * * * /usr/local/sbin/bands.py >/dev/null 2>&1
#
# Add this to /etc/asterisk/rpt.conf under [functions]
# 85=cmd,asterisk -rx "rpt localplay 99999 /etc/asterisk/custom/bands"
#
# (where 99999 is your node number)
#
#################################
import re
import shlex
import subprocess
import sys
import requests
import xmltodict
#
# configuration
#
# set your voicerss API key here
voicersskey = "someapikeygoeshere"
# set your desired voice language here
voicersslang = "en-us"
# set speed of speech here
voicerssspeed = "-1"
# set format of initial audio before converting to ulaw
voicerssformat = "44khz_16bit_mono"
#
# end configuration
#
xml_data = requests.get(
    url="http://www.hamqsl.com/solarxml.php"
)
band_data = xmltodict.parse(xml_data.text)

textfile = open("/tmp/bands.txt", "w")

textfile.write("There are currently %s sunspots, and a solar flux of %s. Noise floor approximately %s... Estimated band conditions follow... \r\n" %
           (
               band_data["solar"]["solardata"]["sunspots"][0:5],
               band_data["solar"]["solardata"]["solarflux"][0:5],
               band_data["solar"]["solardata"]["signalnoise"][0:2],
           )
           )

for bands in band_data["solar"]["solardata"]["calculatedconditions"]["band"]:
    textfile.write("%s to %s meters.." %
               tuple(re.findall(r"\d+", bands["@name"])))
    textfile.write(bands["@time"] + " time, ..")
    textfile.write(bands["#text"] + "\n")

textfile.write("\rEnd of report.")

textfile.close()

bandreport = open("/tmp/bands.txt", "r")
getmp3 = requests.get("http://api.voicerss.org/",
                      data={"key": voicersskey, "r": voicerssspeed,
                            "src": bands, "hl": voicersslang, "f": voicerssformat}
                      )
bandreport.close()
mp3file = open("/tmp/bands.mp3", "wb")
mp3file.write(getmp3.content)
mp3file.close()
# convert to wav with lame (apt-get install lame) then to ulaw with sox (apt-get install sox)
subprocess.call(shlex.split("lame --decode /tmp/bands.mp3 /tmp/bands.wav"))
subprocess.call(shlex.split("sox -V /tmp/bands.wav -r 8000 -c 1 -t ul /etc/asterisk/custom/bands.ul"))
# cleanup
subprocess.call(shlex.split("rm -f /tmp/bands.txt"))
subprocess.call(shlex.split("rm -f /tmp/bands.mp3"))
subprocess.call(shlex.split("rm -f /tmp/bands.wav"))

