#!/usr/bin/env python3
# coding: utf-8

import re
import time
import yaml
import os
import sys
import subprocess

print("Install python packages")
print(100 * "=")
subprocess.call(["sudo", "apt-get", "install", "python3-pip"])
print(100 * "=")
subprocess.call(["pip3", "install", "python-crontab"])
print(100 * "=")
subprocess.call(["pip3", "install", "websocket-client"])
print(100 * "=")
subprocess.call(["pip3", "install", "dnspython"])
print(100 * "=")

from crontab import CronTab

regex_email = "^[a-z0-9]+[.|_|-]?[a-z0-9]+[@]\w+[-]?\w+[.]\w{2,3}$"
regex_ip = "^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$"
d = {}
irr = input("Please input the name of IRR (RIPE or RADB): ").lower()
asns = input("Please input your ASN/ASNs with comma separated: ").split(", ")
main_asn = input("Please input your main ASN/ASNs with comma separated: ").split(", ")
upl = input(
    "Please input all your Uplinks with comma separated in format Upl1: ASN, Upl2: ASN: "
)
uplinks = {}
u = upl.split(",")
for k in u:
    f = k.split(":")
    uplinks.update({f[0].strip(" "): f[1].strip(" ")})
min_hosts = input(
    "Please input the min RIPE hosts for check BGP hijack or control of announcing the new prefixes: "
)
debug = input("Please input True or False if you want to enable debugging (stdout): ")
email = input("Please input your email if you want to receive the notifications: ")
while True:
    if re.search(regex_email, email):
        break
    else:
        email = input("Your email is incorrect. Please try again: ")
cltr = input("Please input True or False for send data to your logstash collector: ")
collector = {}
while True:
    if cltr.capitalize() == "True":
        enable = (True,)
        host = input("Please specify the IP adddress for your collector: ")
        while True:
            if re.search(regex_ip, host):
                break
            else:
                host = input("Your IP address is incorrect. Please try again: ")
        port = input("Please specify the UDP port for your collector: ")
        collector.update({"enable": True, "host": host, "port": int(port)})
    break

slack = {"enable": False, "url": None}
telegram = {"enable": False, "token": None, "chat_id": None}

d.update(
    {
        "min_hosts": int(min_hosts),
        "debug": bool(debug),
        "uplinks": uplinks,
        "email": email,
        "asns": asns,
        "main_asn": main_asn,
        "logstash": collector,
        "slack": slack,
        "telegram": telegram,
        "irr": irr,
    }
)

print("Writing data to config.yaml file")
with open("config.yaml", "w") as file:
    yaml.dump(d, file)

time.sleep(2)

print("Creating the list of prefixes. Please wait, it can take a few minutes")
subprocess.Popen([sys.executable, "get_irr.py"])
time.sleep(300)
print("List of prefixes was created")

d = os.getcwd()
print(d)
t = os.popen("which python3").readlines()
j = CronTab(user="root")
# cmd = t[0].rstrip('\n') + ' ' + d + '/parse_ripe_asn.py'
cmd = "cd " + d + "/ && $(which python3) " + "get_irr.py " + ">> ~/cron.log 2>&1"
cron_job = j.new(cmd)
cron_job.minute.on(0)
cron_job.hour.on(23, 11)
# writes content to crontab
j.write()
print(
    "All your prefixes will be updated twice per day (at 11:00 and 23:00) by task in crontab"
)
print(j.render())
