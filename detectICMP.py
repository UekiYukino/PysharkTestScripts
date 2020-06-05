#!/usr/bin/env python3

##############################################
# This program capture live packet and detect
# ICMP packets
##############################################
import pyshark
import argparse
import subprocess
import re

def receiveInput():
    parser=argparse.ArgumentParser()
    parser.add_argument('-f','--file', dest='fileName', help='Output file name')
    parser.add_argument('-i','--interface', dest='interface', help='Interface use to capture packets')
    parser.add_argument('-c','--count', dest='packetCount', help='Number of packets to capture')
    options=parser.parse_args()
    if not options.interface:
        parser.error('[-] Specify an interface, use --help for more information')
    elif not options.packetCount:
        parser.error('[-] Specify the number of packets to capture, use --help for more information')
    elif not options.fileName:
        print('[+] File name not specify, using the default \"File.txt\"')
        name='File.txt'
    elif options.fileName:
        name= options.fileName
    return name, options.interface,options.packetCount

#Receiving host IP address
def ipCapture(interface):
    try:
        cmdOutput=subprocess.check_output(['ifconfig',interface])
        IpSearch=re.search(r'inet ([0-9]..*) netmask',str(cmdOutput))
        Ip=IpSearch.group(1)
    except:
        Ip=False
    return Ip

#Capturing ICMP packets
def icmpScanning(fileName, inface, host,packets):
    capture= pyshark.LiveCapture(interface=inface)#Live capture on the interface
    newfile=open(fileName,'w')
    
    for packet in capture.sniff_continuously(packet_count=int(packets)):

        try:
            if packet['icmp'].Type=='0': #Capture icmp reply
                if packet['ip'].src == host: #Detect host icmp reply
                    print ('Someone is trying to ping the server from',packet['ip'].dst)
                    newfile.write('ALERT!!! SOMEONE IS TRYING TO PING FROM OUTSIDE\n')
                    newfile.write('Packet coming from host: '+ str(packet['ip'].dst)+'\n')
                    newfile.write(str(packet)+"\n\n")
                else: #Watch for reply from remote machine
                        print('There is a reply from', packet['ip'].dst)
                        newfile.write('This is a ping from the host\n')
                        newfile.write(str(packet)+'\n\n')
                    
            elif packet['icmp'].Type=='8': #Ignore icmp request packet
                continue

        except:
            continue
    print('[+]Finish capture, escaping process')
    newfile.close()
    capture.close()
    exit()


name,interface,packetCount=receiveInput()
host=ipCapture(interface)
if host:
    icmpScanning(name,interface,host,packetCount)
else:
    print('[-] Invalid interface, please try again')
