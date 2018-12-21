#!/usr/bin/python
#
# pulls band predictions from hamqsl.com
# va3dxv@gmail.com
############################################################
import requests
import xmltodict
import re
import subprocess
import shlex
import sys

xml_data = requests.get(
    url="http://www.hamqsl.com/solarxml.php"
)
band_data = xmltodict.parse(xml_data.text)

#print(json.dumps(band_data, indent=4, sort_keys=True))

file = open("/tmp/bands.txt", "w")

file.write("Estimated HF band conditions..\r\n")
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
