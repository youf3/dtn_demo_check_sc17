#!/usr/bin/env python3
### readme
### run the script in sudoer priviledge ! ( or get exception)

#
# json_str = json.dumps(data)
#
# print(json_str)
#
# with open('data.json', 'w') as f :
#    json.dump(data,f)
#
# with open('data.json', 'r') as f :
#    data1 = json.load(f)
#
# from pprint import pprint
# pprint(data1)

import json
import multiprocessing
import pprint
# import queue
import os
import queue
import subprocess
import re
import shutil
import socket

### Using os.system(..) to execute cmd and return 0 or 1
### Using subprocess.Popen(..) to get the execution result
import threading

import time


def return_command(cmd):
    #  return execution result as output -> str
    process = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=1)
    return process.stdout.read().decode('utf8')


def check_command_old(cmd):
    #  return 0 if success, or return > 0 -> int
    return os.system(cmd)


def check_command(cmd):
    #  return 0 if success, or return > 0 -> int
    process = subprocess.run(cmd)
    return process.returncode


def checkFirewall():
    # check iptables is existed, if without iptables, pass the check
    if shutil.which("iptables") is None:
        return 1

    ret = return_command("head -n 1 /etc/os-release")
    # check Centos or Ubuntu, only Centos iptables filter 8000 ..
    # if re.search("CentOS Linux", ret) == None: # easily failed
    if "CentOS" in ret:
        # if Centos , check the rule for opening 8000 port for jupyter
        ret = return_command("iptables -nvL |grep 8000 |wc -l")
        if int(ret) < 1:
            return 0
    return 1


def checkVlan():
    vlan63 = "192.168.63.59"
    vlan61 = "192.168.61.57"
    # check vlan 61 and 63

    if int(check_command("ping -c 1 " + vlan63 + ">/dev/null")) != 0:
        # vlan 63 can't connect, check 61
        if int(check_command("ping -c 1 " + vlan61 + ">/dev/null")) != 0:
            # neither 61 nor 63 is failed to ping, return 0
            return 0
        else:
            return 61
    else:
        # vlan 63 ok , check 61
        if int(check_command("ping -c 1 " + vlan61 + ">/dev/null")) != 0:
            # vlan 63 ok, check 61 failed
            return 63
        else:
            # both 61 nor 63 is ok to ping
            return 6163


def checkJupyter():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # check the jupyter port is open, because system reboot will reset iptables rules
    ret = sock.connect_ex(('0.0.0.0', 8000))
    if ret != 0:
        return 0
    return 1


def checkNvme():
    ret = int(return_command("df |grep nvme |wc -l "))
    if type(ret) == int:
        return int(ret)
    else:
        return 0


def checkFileExist():
    ### this will occur file not found exection
    #   ret = return_command("ls /data/disk*/sc17/fftest | wc -l ")
    #   if int(ret) < 8:
    #       return 0
    #   return 1
    count = 0
    dirlist = [
        "/data/disk0/sc17/fftest",
        "/data/disk1/sc17/fftest",
        "/data/disk2/sc17/fftest",
        "/data/disk3/sc17/fftest",
        "/data/disk4/sc17/fftest",
        "/data/disk5/sc17/fftest",
        "/data/disk6/sc17/fftest",
        "/data/disk7/sc17/fftest",
    ]
    for fd in dirlist:
        if os.access(fd, os.R_OK) is False:
            continue
        count += 1
    return count


def checkDirPermission():
    count = 0
    dirlist = [
        "/data/disk0/sc17/",
        "/data/disk1/sc17/",
        "/data/disk2/sc17/",
        "/data/disk3/sc17/",
        "/data/disk4/sc17/",
        "/data/disk5/sc17/",
        "/data/disk6/sc17/",
        "/data/disk7/sc17/",
    ]
    for fd in dirlist:
        if os.access(fd, os.W_OK) is False:
            continue
        count += 1
    return count


checklist = {}


# checklist = {
#    'firewall_check': 1,
#    'vlan_check': 1,
#    'jupyter_check': 1,
#    'nvme_check': 1,
#    'directory_check': 1,
#    'permission_check': 1,
# }


def checkSudoer():
    if os.getuid() != 0:
        return False
    else:
        return True


def pingServer(server, qu):
    vlan_name = server[0]
    server_name = server[1]
    if int(check_command(["ping", "-c 1", server_name + " >/dev/null"])) == 0:

        # result = subprocess.run(["/sbin/ping", "-c 1", server])
        # if result.returncode == 0 :

        # success
        qu.put((vlan_name, 1))
    else:
        # failed
        qu.put((vlan_name, 0))


'''
    result = subprocess.run(["/sbin/ping" , "-c 1", server])

    if result.returncode == 0:
        qu.put((server, True))
    else:
        qu.put((server, False))
'''


def checkIndVlan():
    serverlist = [
        (3060, "192.168.60.57"),
        (3061, "192.168.61.57"),
        (3062, "192.168.62.59"),
        (3063, "192.168.63.59"),
        (1038, "10.250.38.50"),
    ]
    ret = {}
    qu = queue.Queue()

    # threads = [None,None,None,None,None]
    threads = []

    for i in range(len(serverlist)):
        server = serverlist[i]
        # threads[i] = threading.Thread(target=pingServer, args=(server,qu))
        # threads[i].start()
        th = threading.Thread(target=pingServer, args=(server, qu))
        th.start()
        threads.append(th)

    # for i in range(len(serverlist)):
    #     threads[i].join()
    while (len(threads) != 0):
        th = threads.pop()
        th.join()

    while (qu.empty() is False):
        vlan_ret = qu.get()
        # vlan_ret[0] = 3060, ...
        # vlan_ret[1] = 1 or 0
        ret[vlan_ret[0]] = vlan_ret[1]

    return ret


def main():
    checklist["firewall_check"] = checkFirewall()

    ## checklist["vlan_check"] = checkVlan() ## deprecated
    checklist["vlan_check"] = checkIndVlan()

    checklist["jupyter_check"] = checkJupyter()
    checklist["nvme_check"] = checkNvme()
    checklist["testfile_check"] = checkFileExist()
    checklist["permission_check"] = checkDirPermission()
    json_str = json.dumps(checklist, indent=4)
    print(json_str)
    with open("./dtn_demo_check_sc17.json", "w") as f:
        f.write(json_str)


def usage():
    print("{msg=\"You should run this in sudo priviledge !\"}")
    exit(1)


if __name__ == "__main__":
    #main()
    usage() if checkSudoer() is False else main()

