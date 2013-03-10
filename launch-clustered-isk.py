#!/usr/bin/env python
#
# Launch-Clustered-ISK.py
# By Brandon Smith (brandon.smith@studiobebop.net)
# -----------------------
# A small script for launching (and maintaining) multiple instances of iskdaemon.py
# for the purproses of running them in parallel.
#
import os
import ConfigParser
import subprocess
import threading
import time

###
# Global Config
###

instance_count = 13 # Number of instances iskdaemon.py to start
start_port     = 1336 # Port to start launching instances from (incroments with each instance)
exec_path      = "/usr/bin/iskdaemon.py" # Path to iskdaemon.py
isk_root       = os.path.join(os.path.abspath("."), "isk-cluster")
isk_db_path    = os.path.join(os.path.abspath("."), "isk-db")

### End Global Config ###

def get_config(i):
    config = ConfigParser.RawConfigParser()

    # Daemon config
    config.add_section("daemon")
    config.set("daemon", "startAsDaemon", "no") # Daemon mode doesn't seem to work 
                                                # for me anymore, so we'll disable it :/
    config.set("daemon", "writerPort", start_port)
    config.set("daemon", "basePort", start_port + i)
    config.set("daemon", "debug", "no")
    if i == 0:
        config.set("daemon", "saveAllOnShutdown", "yes")
    else:
        config.set("daemon", "saveAllOnShutdown", "no")
    config.set("daemon", "logPath", "isk-daemon.log")
    config.set("daemon", "logDebug", "no")

    # database config
    config.add_section("database")
    config.set("database", "databasePath", isk_db_path)
    config.set("database", "saveInterval", "120")
    if i == 0:
        config.set("database", "automaticSave", "yes")
    else:
        config.set("database", "automaticSave", "no")

    # cluster config (not the same thing as this)
    # This is mostly here because it's in the original isk-daemon config and 
    # I'd rather not tempt fate.
    config.add_section("cluster")
    config.set("cluster", "isClustered", "no")
    config.set("cluster", "seedPeers", "isk2host:31128")
    config.set("cluster", "bindHostname", "isk1host")

    return config

def run_instance(isk_path):
    while True:
        print "[+] Launching daemon! @ %s" % isk_path
        c = subprocess.Popen([exec_path], cwd=isk_path)
        c.wait()
        print "[!] Process @ %s died!" % isk_path
        print "[!] Relaunching it!"


if __name__ == "__main__":
    for i in range(instance_count):
        print "-" * 80

        # Create working directory for instance
        print "[+] Creating ISK instance directory."
        isk_path = os.path.join(isk_root, "isk-%d" % i)
        if not os.path.exists(isk_path): os.makedirs(isk_path)

        # Build and write config file
        print "[+] Building config file for instance #%d" % i
        config = get_config(i)
        config_path = os.path.join(isk_path, "isk-daemon.conf")
        with open(config_path, "wb") as f: config.write(f)

        # Launch the daemon
        threading.Thread(target=run_instance, args=(isk_path, )).start()

while threading.activeCount() > 1:
    time.sleep(0.3)
