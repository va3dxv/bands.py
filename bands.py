#!/usr/bin/python
#
# pulls band predictions from hamqsl.com
# va3dxv@gmail.com
############################################################
import re
import shlex
import subprocess
import sys

import requests
import xmltodict

xml_data = requests.get(
    url="http://www.hamqsl.com/solarxml.php"
)
band_data = xmltodict.parse(xml_data.text)

file = open("/tmp/bands.txt", "w")

file.write("There are currently %s sunspots, and a solar flux of %s. Noise floor approximately %s... Estimated band conditions follow... \r\n" %
           (
               band_data["solar"]["solardata"]["sunspots"][0:5],
               band_data["solar"]["solardata"]["solarflux"][0:5],
               band_data["solar"]["solardata"]["signalnoise"][0:2],
           )
           )

for bands in band_data["solar"]["solardata"]["calculatedconditions"]["band"]:
    file.write("%s to %s meters.." %
               tuple(re.findall(r"\d+", bands["@name"])))
    file.write(bands["@time"] + " time, ..")
    file.write(bands["#text"] + "\n")

file.write("\rEnd of report.")

file.close()

subprocess.call(shlex.split("/usr/local/sbin/tts_audio.sh /tmp/bands.txt"))
subprocess.call(shlex.split("rm -f /tmp/bands.txt"))
subprocess.call(shlex.split("rm -f /etc/asterisk/custom/bands.ul"))
subprocess.call(shlex.split("mv /tmp/bands.ul /etc/asterisk/custom"))

# print(json.dumps(band_data, indent=4, sort_keys=True))
