#!/usr/local/bin/python3

import os
import sys
import datetime
import yaml
from jinja2 import Template
from jnpr.junos import Device
from jnpr.junos.factory.factory_loader import FactoryLoader
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *

# Get actuall date/time
now = datetime.datetime.now()

#--------------GENERATING CONFIG START--------------

print("#------------------ INITIALIZING ------------------")

print("Loading YAML + Jinja files...")

# Load YAML file with your prefix lists
with open("prefix-lists/prefix-lists.yml") as fP:
    prefixLists = yaml.load_all(fP.read())

# Load the Jinja2-template
with open("prefix-lists/prefix-list-template.j2") as fT:
    cfgTemplate = fT.read()

# Render configuration with YAML (data) + Jinja (template)
config = ''
for data in prefixLists:
    config += Template(cfgTemplate).render(data)+"\n"

print("Configuration snippet generated...")

# Save configuration as history to folder configs
with open("configs"+"/"+now.strftime("%Y-%m-%d_%H:%M:%S")+"-prefix-lists.cfg", "w") as file_:
    file_.write(config)

#--------------GENERATING CONFIG END--------------


#--------------CHECK PREFIX-LIST START--------------

with open('routers.yml') as f:
    routers = (yaml.load(f))['routers']

print("#------------------ CHECK ROUTERS ------------------")

# Loop: Check every router stored in routers.yml
for router_name, host_ip in routers.items():

    # connect to the device with IP-address, login user and passwort
    print("#--- Connecting to "+router_name+" / "+host_ip+"...")
    dev = Device(host=host_ip, user="sbehrens", password="secretPW", gather_facts=False)
    dev.open()
    print("Connection successfully...")

    # Bind config to dev
    dev.bind(cu=Config)

    # Lock configuration
    dev.cu.lock()
    print("Configuration locked...")

    # Merge our configuration
    print("Loading configuration...")
    dev.cu.load(config, format="text", merge=False)

    # Check if prefix-list is up-to-date
    print("Checking difference...")
    if dev.cu.diff() is None:
        print("Prefix-list configuration is up-to-date!")
    else:
        print("Prefix-list configuration is --NOT-- up-to-date!")

        print("----")
        print("Do you want to do the following changes:")
        print(dev.cu.diff())
        print("----")

        askForCommit = input("Commit changes? (Yes, No)")
        if askForCommit in ["Yes"]:
            print("Committing configuration...")
            # Commit changes
            dev.cu.commit()
        else:
            print("Commit cancelled...")

    # Unlock configuration
    dev.cu.unlock()
    print("Configuration unlocked...")

    dev.close()
    print("Connection closed...")

#--------------CHECK PREFIX-LIST END--------------
