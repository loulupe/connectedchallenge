# -*- coding: utf-8 -*-
'''
Copyright (c) 2016, Virginia Tech
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
 following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
The views and conclusions contained in the software and documentation are those of the authors and should not be
interpreted as representing official policies, either expressed or implied, of the FreeBSD Project.
This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the
United States Government nor the United States Department of Energy, nor Virginia Tech, nor any of their employees,
nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty,
express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or
any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe
privately owned rights.
Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or
otherwise does not necessarily constitute or imply its endorsement, recommendation, favoring by the United States
Government or any agency thereof, or Virginia Tech - Advanced Research Institute. The views and opinions of authors
expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.
VIRGINIA TECH – ADVANCED RESEARCH INSTITUTE
under Contract DE-EE0006352
#__author__ = "BEMOSS Team"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"
'''

import os
import json
import socket
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Defaults


def parseJSONresponse(data,key):
    theJSON = json.loads(data)
    return theJSON[key]

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def discover(type):
    responses=list()
    result = []

    valid_iphead = False
    try:
        infile = None
        # infile = open(os.path.expanduser("~")+"/workspace/bemoss_os/machine_ip.txt","r")  ####
        infile = open("machine_ip.txt", "r")        ####
        for line in infile:
            # line= "192.168.1.2"                   ####
            own_ip = line.rstrip()
            own_ip_parts = own_ip.split('.')
            if len(own_ip_parts) == 4:
                print( "Found own IP: "+own_ip)
                iphead = own_ip_parts[0]+'.'+own_ip_parts[1]+'.'+own_ip_parts[2]+'.'
                valid_iphead = True
                break
            infile.close()
    except:
        if infile is not None:
            infile.close()
        valid_iphead = False

    # print("reached half way ")

    if valid_iphead:
        # print("inside ip head")
        start_ip=2
        end_ip=254
        print ("Looking for Modbus Devices in the IP range: "+iphead+str(start_ip)+" to "+iphead+str(end_ip))
        _Timeout=0.2

        ip_index=start_ip
        iprange=list()
        # print("start ip index")
        while ip_index<=end_ip:
            iprange.append(iphead+str(ip_index))
            # print("ipindex: ",ip_index)
            ip_index=ip_index+1

        print("********************")
        #print iprange
        counter = 1                                 ####
        for ip in iprange:
            counter += 1                            ####
            if (counter != 99):                     ####
                continue                            ####
            print("checking in the ip range: ",ip)
            try:
                #print ip
                _socket = None                      ####
                # _socket = socket.socket()
                try:
                    _socket = socket.create_connection((ip, 502), _Timeout)
                    print("Connection successful: ",ip, "socket: ",_socket)
                except socket.error:
                    if _socket:                     ####
                        _socket.close()             ####
                    print("socket error")           ####
                    _socket = None
                if _socket is not None:
                    _socket.close()                 ####
                    Defaults.Timeout = 10           ####

                    client = ModbusTcpClient(ip)
                    print("ModbusTcpClient: ", client)
                    # client.bind(("192.168.1.2",0))
                    print(client.connect())
                    if type == 'Prolon_VAV':
                        possible_subordinate_ids = [1, 2, 7, 16]
                    elif type == 'Prolon_RTU':
                        possible_subordinate_ids = [15, 20]
                    else:
                        possible_subordinate_ids = []
                    print("possible subordinate ids: ",possible_subordinate_ids)
                    for subordinate_id in possible_subordinate_ids:
                            print("subordinate: ",subordinate_id)
                            print("result b4: ",result)
                            result = client.read_input_registers(0,unit=subordinate_id)
                            print("subordinate_id: ",subordinate_id," result: ",result)
                            if result is not None:
                                responses.append(ip+':'+str(subordinate_id))
                            print("end of loop ",subordinate_id)

                    client.close()
                    print("client closed")
                    break                           ####
            except Exception as e:
                print("error: ",e)
                pass
            if (ip == 99):
                    break
            print("End of outer for loop.")


    else:
        print ("Modbus discovery failed: Couldn't find IP subnet of network!")
    print("responses: ",responses)
    return responses

def getMACaddress(type,ipaddress):
    if type == "Prolon_VAV":
        if ipaddress.split(':')[1] == '7':
            # macaddress = '30168D000388'
            macaddress = '30168D000129'
        # 30:16:8D:00:03:88
        elif ipaddress.split(':')[1] == '1':
            macaddress = '30168D000262'
        elif ipaddress.split(':')[1] == '16':
            macaddress = '30168D000388'
        elif ipaddress.split(':')[1] == '2':
            macaddress = '30168D000263'
        else:
            macaddress = None
    elif type == "Prolon_RTU":
        if ipaddress.split(':')[1] == '15':
            macaddress = '30168D000130'
        elif ipaddress.split(':')[1] == '20':
            macaddress = '30168D000264'
        else:
            macaddress = None
    else:
        macaddress = None
    return macaddress


def getmodelvendor(type,ipaddress):
    if type == "Prolon_VAV":
        modelinfo = {'model':'VC1000','vendor':'Prolon'}
    elif type == "Prolon_RTU":
        modelinfo = {'model':'M1000','vendor':'Prolon'}
    else:
        modelinfo = None

    return modelinfo

##############################################################################
def testing():
    print("getmodelvendor: ",getmodelvendor("Prolon_VAV","192.168.1.99"))
    # print("getmacaddress: ", getMACaddress("Prolon_VAV","192.168.1.99"))
    print("discover(): ", discover("Prolon_VAV"))


testing()
###############################################################################
# print discover('Prolon_RTU')
