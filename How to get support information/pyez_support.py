import os
import datetime
from jnpr.junos.utils.start_shell import StartShell
from jnpr.junos import Device
from jnpr.junos.utils.scp import SCP
from jnpr.junos.utils.fs import FS

# Get actuall date/time
now = datetime.datetime.now()

# Method for humanreadable size-output
def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

#--------------GET RSI START--------------

# connect to the device with IP-address, login user and passwort
dev = Device(host="vSRX1", user="sbehrens", password="secretPW", gather_facts=False)
dev.open()
print("Connection successfully...")

print("\n------ FILE CREATION")
print("Starting shell for creating RSI...")
ss = StartShell(dev)
ss.open()
ss.run('cli -c "request support information | save /var/tmp/pyez_rsi.txt"')
print("RSI done...")
ss.close()

# Compress /var/log/ to /var/tmp/pyez_varlog.tgz
fileSystem = FS(dev)
fileSystem.tgz("/var/log/*","/var/tmp/pyez_varlog.tgz")
print("/var/log-compressed...")

# Get file system information
statRsi = fileSystem.stat("/var/tmp/pyez_rsi.txt")
statLogs = fileSystem.stat("/var/tmp/pyez_varlog.tgz")

# Transfering files via SCP
print("\n------ Transfering files")

# Get RSI
if statRsi['size'] is not None:
    print("File: /var/tmp/pyez_rsi.txt - Size: "+(str(sizeof_fmt(statRsi['size']))))
    askForTransferRsi = input("Do you want to transfer the RSI? (Yes, No)")
    if askForTransferRsi in ["Yes"]:
        with SCP(dev, progress=True) as scp:
            scp.get("/var/tmp/pyez_rsi.txt", now.strftime("%Y-%m-%d_%H:%M:%S")+"_"+dev.hostname+"_rsi.txt")
else:
    print("Error: file /var/tmp/pyez_rsi.txt does not exist")

# Get /var/log
if statLogs['size'] is not None:
    print("File: /var/tmp/pyez_varlog.tgz - Size: "+(str(sizeof_fmt(statLogs['size']))))
    askForTransferLogs = input("Do you want to transfer the /var/log? (Yes, No)")
    if askForTransferLogs in ["Yes"]:
        with SCP(dev, progress=True) as scp:
            scp.get("/var/tmp/pyez_varlog.tgz", now.strftime("%Y-%m-%d_%H:%M:%S")+"_"+dev.hostname+"_varlog.tgz")
else:
    print("Error: file /var/tmp/pyez_varlog.tgz does not exist")

dev.close()
print("Connection closed...")

#--------------GET RSI END--------------
