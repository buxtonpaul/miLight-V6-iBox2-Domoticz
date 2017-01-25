#!/usr/bin/python
import socket, sys, urllib2


###################
## Configuration ##
###################
IBOX_IP = "192.168.0.34"        # iBox IP address
UDP_PORT_SEND = 5987            # Port for sending
UDP_PORT_RECEIVE = 55054        # Port for receiving
UDP_MAX_TRY = 5                 # Max sending max value is 256
UDP_TIMEOUT = 5                 # Wait for data in sec
DOMOTICZ_IP = "192.168.0.35"    # Domoticz IP only needed for logging
DOMOTICZ_PORT = "80"            # Domoticz port only needed for logging
DOMOTICZ_LOG = 0                # Turn logging to Domoticz on/off 0=off and 1=on
live = True
###############################################################################################


def Hexstr(vals, sep=', '):
    ''' Print the provided list as a hex string, using the optional seperator to determine how they are seperated'''
    return'[{}]'.format(sep.join(hex(x) for x in vals))



#####################
## Log to Domoticz ##
#####################
def doLog(MSG):
    ''' Log a message to Domoticz'''
    try:
        if DOMOTICZ_LOG == 1:
            urllib2.urlopen("http://"+DOMOTICZ_IP+":"+DOMOTICZ_PORT+
                            "/json.htm?type=command&param=addlogmessage&message="
                            +MSG.replace(" ", "%20")).read()
        else:
            print "DEBUG: ", MSG
    except Exception as ex:
        print "[DEBUG] log error: ", ex

rawcommands = {
    "COLOR001"       : [0x31, 0x00, 0x00, 0x08, 0x01, 0xBA, 0xBA, 0xBA, 0xBA],
    "COLOR001"       : [0x31, 0x00, 0x00, 0x08, 0x01, 0xBA, 0xBA, 0xBA, 0xBA],
    "COLOR002"       : [0x31, 0x00, 0x00, 0x08, 0x01, 0xFF, 0xFF, 0xFF, 0xFF],
    "COLOR003"       : [0x31, 0x00, 0x00, 0x08, 0x01, 0x7A, 0x7A, 0x7A, 0x7A],
    "COLOR004"       : [0x31, 0x00, 0x00, 0x08, 0x01, 0x1E, 0x1E, 0x1E, 0x1E],
    "SATUR00"        : [0x31, 0x00, 0x00, 0x08, 0x02, 0x64, 0x00, 0x00, 0x00],
    "SATUR25"        : [0x31, 0x00, 0x00, 0x08, 0x02, 0x4B, 0x00, 0x00, 0x00],
    "SATUR50"        : [0x31, 0x00, 0x00, 0x08, 0x02, 0x32, 0x00, 0x00, 0x00],
    "SATUR75"        : [0x31, 0x00, 0x00, 0x08, 0x02, 0x19, 0x00, 0x00, 0x00],
    "SATUR100"       : [0x31, 0x00, 0x00, 0x08, 0x02, 0x00, 0x00, 0x00, 0x00],
    "DIM00"          : [0x31, 0x00, 0x00, 0x08, 0x03, 0x64, 0x00, 0x00, 0x00],
    "DIM25"          : [0x31, 0x00, 0x00, 0x08, 0x03, 0x4B, 0x00, 0x00, 0x00],
    "DIM50"          : [0x31, 0x00, 0x00, 0x08, 0x03, 0x32, 0x00, 0x00, 0x00],
    "DIM75"          : [0x31, 0x00, 0x00, 0x08, 0x03, 0x19, 0x00, 0x00, 0x00],
    "DIM100"         : [0x31, 0x00, 0x00, 0x08, 0x03, 0x00, 0x00, 0x00, 0x00],
    "ON"             : [0x31, 0x00, 0x00, 0x08, 0x04, 0x01, 0x00, 0x00, 0x00],
    "OFF"            : [0x31, 0x00, 0x00, 0x08, 0x04, 0x02, 0x00, 0x00, 0x00],
    "SPEEDUP"        : [0x31, 0x00, 0x00, 0x08, 0x04, 0x03, 0x00, 0x00, 0x00],
    "SPEEDDOWN"      : [0x31, 0x00, 0x00, 0x08, 0x04, 0x04, 0x00, 0x00, 0x00],
    "NIGHTON"        : [0x31, 0x00, 0x00, 0x08, 0x04, 0x05, 0x00, 0x00, 0x00],
    "WHITEON"        : [0x31, 0x00, 0x00, 0x08, 0x05, 0x64, 0x00, 0x00, 0x00],
    "WW00"           : [0x31, 0x00, 0x00, 0x08, 0x05, 0x64, 0x00, 0x00, 0x00],
    "WW25"           : [0x31, 0x00, 0x00, 0x08, 0x05, 0x4B, 0x00, 0x00, 0x00],
    "WW50"           : [0x31, 0x00, 0x00, 0x08, 0x05, 0x32, 0x00, 0x00, 0x00],
    "WW75"           : [0x31, 0x00, 0x00, 0x08, 0x05, 0x19, 0x00, 0x00, 0x00],
    "WW100"          : [0x31, 0x00, 0x00, 0x08, 0x05, 0x00, 0x00, 0x00, 0x00],
    "MODE01"         : [0x31, 0x00, 0x00, 0x08, 0x06, 0x01, 0x00, 0x00, 0x00],
    "MODE02"         : [0x31, 0x00, 0x00, 0x08, 0x06, 0x02, 0x00, 0x00, 0x00],
    "MODE03"         : [0x31, 0x00, 0x00, 0x08, 0x06, 0x03, 0x00, 0x00, 0x00],
    "MODE04"         : [0x31, 0x00, 0x00, 0x08, 0x06, 0x04, 0x00, 0x00, 0x00],
    "MODE05"         : [0x31, 0x00, 0x00, 0x08, 0x06, 0x05, 0x00, 0x00, 0x00],
    "MODE06"         : [0x31, 0x00, 0x00, 0x08, 0x06, 0x06, 0x00, 0x00, 0x00],
    "MODE07"         : [0x31, 0x00, 0x00, 0x08, 0x06, 0x07, 0x00, 0x00, 0x00],
    "MODE08"         : [0x31, 0x00, 0x00, 0x08, 0x06, 0x08, 0x00, 0x00, 0x00],
    "MODE09"         : [0x31, 0x00, 0x00, 0x08, 0x06, 0x09, 0x00, 0x00, 0x00]
}


###
# Lets start a tidied way of accessing commands rather than one big list
rgbwcommands = {
    "ON" :   [0x31, 0x00, 0x00, 0x07, 0x03, 0x01, 0x00, 0x00, 0x00],
    "OFF":   [0x31, 0x00, 0x00, 0x07, 0x03, 0x02, 0x00, 0x00, 0x00],
    "NIGHT": [0x31, 0x00, 0x00, 0x07, 0x03, 0x06, 0x00, 0x00, 0x00],
    "WHITE": [0x31, 0x00, 0x00, 0x07, 0x03, 0x05, 0x00, 0x00, 0x00]
}
#
whitecommands = {
    "ON"        : [0x31, 0x00, 0x00, 0x01, 0x01, 0x07, 0x00, 0x00, 0x00],
    "OFF"       : [0x31, 0x00, 0x00, 0x01, 0x01, 0x08, 0x00, 0x00, 0x00],
    "NIGHT"     : [0x31, 0x00, 0x00, 0x01, 0x01, 0x06, 0x00, 0x00, 0x00],
    "BRIGHTUP"  : [0x31, 0x00, 0x00, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00],
    "BRIGHTDOWN": [0x31, 0x00, 0x00, 0x01, 0x01, 0x02, 0x00, 0x00, 0x00],
    "TEMPUP"    : [0x31, 0x00, 0x00, 0x01, 0x01, 0x03, 0x00, 0x00, 0x00],
    "TEMPDOWN"  : [0x31, 0x00, 0x00, 0x01, 0x01, 0x04, 0x00, 0x00, 0x00],
}
rgbwvarcommands = {
    "BRIGHT"   : [0x31, 0x00, 0x00, 0x07, 0x02],
    "MODE"     : [0x31, 0x00, 0x00, 0x07, 0x04]
}
### COLOUR commands
###<- CMD--------------------->  <---------- Colour--->  Zone  Pad   Chksum
###0x31, 0x00, 0x00, 0x07, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x03, 0x00, 0xFF
###

bridgecommands = {
    "ON":    [0x31, 0x00, 0x00, 0x00, 0x03, 0x03, 0x00, 0x00, 0x00],
    "OFF":   [0x31, 0x00, 0x00, 0x00, 0x03, 0x04, 0x00, 0x00, 0x00],
    "WHITE": [0x31, 0x00, 0x00, 0x00, 0x03, 0x05, 0x00, 0x00, 0x00]
}

bridgevarcommands = {
    "BRIGHT"   :  [0x31, 0x00, 0x00, 0x00, 0x02],
    "MODE"     :  [0x31, 0x00, 0x00, 0x00, 0x04]
}


devices = {
    "BRIDGE" : [bridgecommands, bridgevarcommands],
    "RGBW" : [rgbwcommands, rgbwvarcommands],
    "RAWCOMMANDS" : [rawcommands],
    "WHITE" : [whitecommands],
    }

######################
## iBox v6 commands ##
######################

def iBoxV6Commands(device, cmd, value):
    if cmd in devices[device][0]:
        return devices[device][0].get(cmd)
    if device == 'RAWCOMMANDS':
        doLog('Command not found:{cmd}'.format(cmd=cmd))
        return 0
    if cmd in devices[device][1]:
        doLog("Variable command: {cmd} {value}".format(cmd=cmd, value=value))
        retval = devices[device][1].get(cmd)+ [value] + [0x00, 0x00, 0x00]
        doLog("Trying: {command}".format(command=Hexstr(retval)))
        return retval
    doLog('Command not found')
    return 0




########################
## V6 command builder ##
########################
def V6CommandBuilder(SessionID1, SessionID2, CycleNR, bulbCommand, Zone, checkSum):
    preamble = [0x80, 0x00, 0x00, 0x00, 0x11]
    return (preamble + [SessionID1, SessionID2, 0x00, CycleNR, 0x00] +
            bulbCommand + [Zone, 0x00, checkSum])


##########################
## Commandline commands ##
##########################
CMDLINE_INFO = (
    "##########################\n"
    "## Command line options ##\n"
    "##########################\n"
    "Use command line as follow : milight.py DEVICE ZONE CMD <param>\n"
    "                           : CMD1 Bulb zone\n"
    "                           : CMD2 Bulb command\n"
    "-------------------------------------------------------------------------------\n"
    " Select the Bulb device    : RAWCOMMANDS RGBW BRIDGE"
    "Select the bulb zone       : 00 01 02 03 04\n"
    "RAWCOMMANDS"
    "Bulb on/off                : ON OFF NIGHTON WHITEON\n"
    "Mode Speed up/down         : SPEEDUP SPEEDDOWN\n"
    "Kelvin warmwhite           : WW00 WW25 WW50 WW75 WW100\n"
    "Saturation                 : SATUR00 SATUR25 SATUR50 SATUR75 SATUR100\n"
    "Mode (discomode)           : MODE01 MODE02 MODE03 MODE04 MODE05\n"
    "                           : MODE06 MODE07 MODE08 MODE09\n"
    "Bulb color                 : COLOR001 COLOR002 COLOR003 COLOR004\n"
    "BRIDGE and RGBW            : ON OFF WHITEON MODE X BRIGHT X\n"
    "WHITE commands             : ON OFF WHITEON NIGHTON TEMPUP TEMPDOWN BRIGHTUP BRIGHTDOWN\n"
)

try:
    CMDLINE_DEVICE = sys.argv[1].strip()
    doLog("Target: {target}".format(target=CMDLINE_DEVICE))
    CMDLINE_ZONE = int(sys.argv[2].strip())
    doLog("ZONE: {zone}".format(zone=CMDLINE_ZONE))

    CMDLINE_CMD = sys.argv[3].strip()
    doLog("CMD : {cmd}".format(cmd=CMDLINE_CMD))
    CMDLINE_VALUE1 = 0
    ## check the device exists
    if CMDLINE_DEVICE in devices:
        doLog("Using device: {device}".format(device=CMDLINE_DEVICE))
    else:
        doLog("No device found matching: {device}".format(device=CMDLINE_DEVICE))
        raise SystemExit()
    if CMDLINE_CMD in devices[CMDLINE_DEVICE][0]:
        doLog("Static command found: {cmd}".format(cmd=CMDLINE_CMD))
    elif CMDLINE_CMD in devices[CMDLINE_DEVICE][1]:
        doLog("Checking variable command {cmd}".format(cmd=CMDLINE_CMD))
        CMDLINE_VALUE1 = int(sys.argv[4].strip())
        doLog("Variable command found: {cmd} {var}".format(cmd=CMDLINE_CMD, var=CMDLINE_VALUE1))
    else:
        raise SystemExit()
except:
    doLog("Valid command not found")
    print CMDLINE_INFO
    raise SystemExit()



###################
## Start session ##
###################
lightSession = False
for iCount in range(0, UDP_MAX_TRY):
    try:
        START_SESSION = bytearray([0x20, 0x00, 0x00, 0x00, 0x16, 0x02, 0x62,
                                   0x3A, 0xD5, 0xED, 0xA3, 0x01, 0xAE, 0x08,
                                   0x2D, 0x46, 0x61, 0x41, 0xA7, 0xF6, 0xDC,
                                   0xAF, 0xD3, 0xE6, 0x00, 0x00, 0x1E])
        doLog("Milight Script: Setting up ibox session...")
        if live:
            sockServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sockServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sockServer.bind(('', UDP_PORT_RECEIVE))
            sockServer.settimeout(UDP_TIMEOUT)
            sockServer.sendto(bytearray.fromhex(START_SESSION), (IBOX_IP, UDP_PORT_SEND))
            dataReceived, addr = sockServer.recvfrom(1024)
        else:
            doLog("Fake it")
            dataReceived = [0x28, 0x00, 0x00, 0x00, 0x11, 0x00, 0x02, 0xAC, 0xCF,
                            0x23, 0xF5, 0x7A, 0xD4, 0x69, 0xF0, 0x3C, 0x23, 0x00,
                            0x01, 0x05, 0x00, 0x00]
        SessionID1 = dataReceived[19]
        SessionID2 = dataReceived[20]
        doLog("Received session message: {message}".format(message=Hexstr(dataReceived, ' ')))
        doLog("SessionID1: {session1}".format(session1=SessionID1))
        doLog("SessionID2: {session1}".format(session1=SessionID2))
        lightSession = True
        break

    except socket.timeout:
        print "Timeout on session start: ", START_SESSION
        doLog("Milight Script: Timeout on command... doing a retry")
        sockServer.close()
        continue

    except Exception as ex:
        doLog("Milight Script: Something's wrong with the session...{}".format(ex))


#######################
## Send bulb command ##
#######################
if lightSession == True:
    for iCount in range(0, UDP_MAX_TRY):
        try:
            CycleNR = iCount
            doLog("Cycle number: {cycle}".format(cycle=CycleNR))
            bulbCommand = iBoxV6Commands(CMDLINE_DEVICE, CMDLINE_CMD, CMDLINE_VALUE1)
            doLog("Light command: {Command}".format(Command=Hexstr(bulbCommand, ' ')))
            useZone = CMDLINE_ZONE
            doLog("Zone: {Zone}".format(Zone=useZone))

            Checksum = sum(bulbCommand) & 0xff
            doLog("Checksum: {checksum}".format(checksum=Checksum))

            sendCommand = V6CommandBuilder(SessionID1, SessionID2,
                                           CycleNR, bulbCommand, useZone, Checksum)
            doLog("Sending command: {command}".format(command=Hexstr(sendCommand, ' ')))

            if live:
                sockServer.sendto(bytearray.fromhex(sendCommand), (IBOX_IP, UDP_PORT_SEND))
                dataReceived, addr = sockServer.recvfrom(1024)
                doLog("Receiving response: {response}".format(response=Hexstr(dataResponse, ' ')))
            break

        except socket.timeout:
            doLog("Timeout on command: {command}".format(command=Hexstr(sendCommand, ' ')))
            continue

        except Exception as ex:
            doLog("Milight Script: Something's wrong with the command...{}".format(ex))

        finally:
            if live:
                sockServer.close()
else:
    if live:
        sockServer.close()

doLog("Milight Script: Ready...")

raise SystemExit()
