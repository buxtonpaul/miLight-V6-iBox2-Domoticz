#!/usr/bin/python
import socket, sys, urllib2;


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
live=False
############################################################################################################


#####################	
## Log to Domoticz ##
#####################
def doLog(MSG):
    try:
        if DOMOTICZ_LOG == 1:
            urllib2.urlopen("http://"+DOMOTICZ_IP+":"+DOMOTICZ_PORT+"/json.htm?type=command&param=addlogmessage&message="+MSG.replace(" ", "%20")).read()
        else :
            print "DEBUG ", MSG
    except Exception as ex:
        print "[DEBUG] log error                :", ex 



rawcommands ={
		"COLOR001"       : "31 00 00 08 01 BA BA BA BA", # original
		"COLOR002"       : "31 00 00 08 01 FF FF FF FF", # original
		"COLOR003"       : "31 00 00 08 01 7A 7A 7A 7A", # original
		"COLOR004"       : "31 00 00 08 01 1E 1E 1E 1E", # original
		"ON"             : "31 00 00 08 04 01 00 00 00", # original
		"OFF"            : "31 00 00 08 04 02 00 00 00", # original
		"SPEEDUP"        : "31 00 00 08 04 03 00 00 00", # original
		"SPEEDDOWN"      : "31 00 00 08 04 04 00 00 00", # original
		"RGBNIGHTON"     : "31 00 00 08 04 05 00 00 00", # original
		"RGBWHITEON"     : "31 00 00 08 05 64 00 00 00",# original
		"WW00"           : "31 00 00 08 05 64 00 00 00",# original
		"WW25"           : "31 00 00 08 05 4B 00 00 00",# original
		"WW50"           : "31 00 00 08 05 32 00 00 00",# original
		"WW75"           : "31 00 00 08 05 19 00 00 00",# original
		"WW100"          : "31 00 00 08 05 00 00 00 00",# original
        "RGBWON"         : "31 00 00 07 03 01 00 00 00", # works
        "RGBWOFF"        : "31 00 00 07 03 02 00 00 00", # works
        "LEDON"          : "31 00 00 00 03 03 00 00 00", # works
        "LEDOFF"         : "31 00 00 00 03 04 00 00 00", # works
        "WHITEON"        : "31 00 00 01 01 07 00 00 00", # works
        "WHITEOFF"       : "31 00 00 01 01 08 00 00 00", # works
        "WHITENIGHT"     : "31 00 00 01 01 06 00 00 00", # works
		"RGBWNIGHTON"    : "31 00 00 07 03 06 00 00 00", # works -- light goes off...
		"RGBWWHITEON"    : "31 00 00 07 03 05 00 00 00", # works
        "LEDWIGHTON"     : "31 00 00 03 05 00 00 00 00", #  untested

}


###
# Lets start a tidied way of accessing commands rather than one big list
rgbwcommands= {"ON":    "31 00 00 07 03 01 00 00 00",
    "OFF":   "31 00 00 07 03 02 00 00 00",
    "NIGHT": "31 00 00 07 03 06 00 00 00",
    "WHITE": "31 00 00 07 03 05 00 00 00"
}

rgbwvarcommands = {
    "BRIGHT"   :  "31 00 00 07 02 ",
    "MODE"     :  "31 00 00 07 04 "
}


bridgecommands = {
    "ON":    "31 00 00 00 03 03 00 00 00",
    "OFF":   "31 00 00 00 03 04 00 00 00",
    "WHITE": "31 00 00 00 03 05 00 00 00"
}

bridgevarcommands = {
    "BRIGHT"   :  "31 00 00 00 02 ",
    "MODE"     :  "31 00 00 00 04 "
}

'''
varcommands={
    "RGBBRIGHT"  : "31 00 00 08 03 ", #  untested
    "LEDBRIGHT"  : "31 00 00 00 02 ", # works
    "RGBMODE"    : "31 00 00 08 06 ", # original
    "LEDMODE"    : "31 00 00 00 04 ", # untested
    "RGBSAT"     : "31 00 00 08 02 ", #  untested
}
'''
devices = {
    "BRIDGE" : [bridgecommands,bridgevarcommands], 
    "RGBW" : [rgbwcommands,rgbwvarcommands],
    "RAWCOMMANDS" : [rawcommands]
    } 

######################
## iBox v6 commands ##
######################

def iBoxV6Commands(device, cmd, value):
    if cmd in devices[device][0]:
        return devices[device][0].get(cmd)
    if device=='RAWCOMMANDS':
        print 'COmmand not found'
        return 0
    if cmd in devices[device][1]:
        print "Variable command ", cmd , value
        retval=devices[device][1].get(cmd)+ format(value, "04X")[2:] + " 00 00 00"
        print "Trying ", retval
        return retval
    print 'COmmand not found'
    return 0
    

                                                                                    
##################
## Zone builder ##
##################
def getZone(data):
    Zone = 0
    for x in bytearray.fromhex(data):
        Zone += x
    return format(Zone, "04X")[2:]


######################
## Checksum builder ##
######################
def getChecksum(data):
    checksum = 0
    for x in bytearray.fromhex(data):
        checksum += x
    return format(checksum, "04X")[2:]


########################
## V6 command builder ##
########################
def V6CommandBuilder(SessionID1, SessionID2, CycleNR, bulbCommand, Zone, checkSum):
    return "80 00 00 00 11 " + SessionID1 + " " + SessionID2 + " 00 " + CycleNR + " 00 " + bulbCommand + " " + Zone + " 00 " + checkSum


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
"Select the bulb zone       : 00 01 02 03 04\n"
"Bulb on/off                : ON OFF NIGHTON WHITEON RGBWON RGBWOFF LEDON LEDOFF\n"
"Mode Speed up/down         : SPEEDUP SPEEDDOWN\n"
"Kelvin warmwhite           : WW00 WW25 WW50 WW75 WW100\n"
"Brightness                 : LEDBRIGHT xx RGBWBRIGHT xx\n"
"Saturation                 : SATUR00 SATUR25 SATUR50 SATUR75 SATUR100\n"
"Mode (discomode)           : MODE01 MODE02 MODE03 MODE04 MODE05\n"
"                           : MODE06 MODE07 MODE08 MODE09\n"
"Bulb color                 : COLOR001 COLOR002 COLOR003 COLOR004\n"
)

try:
    CMDLINE_DEVICE = sys.argv[1].strip()
    print "[DEBUG] target           :", CMDLINE_DEVICE
    
    CMDLINE_ZONE = sys.argv[2].strip()
    print "[DEBUG] ZONE           :", CMDLINE_ZONE

    CMDLINE_CMD = sys.argv[3].strip()
    print "[DEBUG] CMD           :", CMDLINE_CMD
    
    CMDLINE_VALUE1 = 0
    ## check the device exists
    if CMDLINE_DEVICE in devices:
        print "using device ", CMDLINE_DEVICE
    else:
        print "no device found matching", CMDLINE_DEVICE
        raise # some form of error occurred
  
    if CMDLINE_CMD in devices[CMDLINE_DEVICE][0]:
         print " Static command found ", CMDLINE_CMD
    elif(CMDLINE_CMD in devices[CMDLINE_DEVICE][1]):
        CMDLINE_VALUE1 = int(sys.argv[4].strip())
        print "[DEBUG] variable command vound           :",CMDLINE_CMD, CMDLINE_VALUE1
    
  
except:
    print CMDLINE_INFO
    raise SystemExit()
doLog("Milight Script: Starting... (milight.py " + CMDLINE_ZONE + " " + CMDLINE_CMD + ")")


###################
## Start session ##
###################
Session = False
for iCount in range(0, UDP_MAX_TRY):
    try:
        START_SESSION = "20 00 00 00 16 02 62 3A D5 ED A3 01 AE 08 2D 46 61 41 A7 F6 DC AF D3 E6 00 00 1E"
        doLog("Milight Script: Setting up ibox session...")
        if live==True:
            sockServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sockServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sockServer.bind(('', UDP_PORT_RECEIVE))
            sockServer.settimeout(UDP_TIMEOUT)
            sockServer.sendto(bytearray.fromhex(START_SESSION), (IBOX_IP, UDP_PORT_SEND))
            dataReceived, addr = sockServer.recvfrom(1024)
            dataResponse = str(dataReceived.encode('hex')).upper()
            SessionID1 = dataResponse[38:40]
            SessionID2 = dataResponse[40:42]
        else:
            doLog("Fake it")
            dataResponse= " No server so faking it"
            SessionID1 = "BA"
            SessionID2 = "BE"
        print "[DEBUG] received session message :", dataResponse
        print "[DEBUG] sessionID1               :", SessionID1
        print "[DEBUG] sessionID2               :", SessionID2
        Session = True
        break

    except socket.timeout:
        print "[DEBUG] timeout on session start :", START_SESSION
        doLog("Milight Script: Timeout on command... doing a retry")
        sockServer.close()
        continue

    except Exception as ex:
        print "[DEBUG] something's wrong        :", ex 
        doLog("Milight Script: Something's wrong with the session...")


#######################
## Send bulb command ##
#######################
if Session == True:
    for iCount in range(0, UDP_MAX_TRY):
        try:
            CycleNR = format(iCount, "04X")[2:]
            print "[DEBUG] cycle number             :", CycleNR

            bulbCommand = iBoxV6Commands(CMDLINE_DEVICE ,CMDLINE_CMD , CMDLINE_VALUE1)
            print "[DEBUG] light command            :", bulbCommand

            useZone = getZone(CMDLINE_ZONE)
            print "[DEBUG] zone                     :", useZone

            Checksum = getChecksum(bulbCommand + " " + useZone + " 00")
            print "[DEBUG] checksum                 :", Checksum

            sendCommand = V6CommandBuilder(SessionID1, SessionID2, CycleNR, bulbCommand, useZone, Checksum)                     
            print "[DEBUG] sending command          :", sendCommand
            doLog("Milight Script: Sending command: " + sendCommand)
            if live:
                sockServer.sendto(bytearray.fromhex(sendCommand), (IBOX_IP, UDP_PORT_SEND))
                dataReceived, addr = sockServer.recvfrom(1024)
                dataResponse = str(dataReceived.encode('hex')).upper()
                print "[DEBUG] received message         :", dataResponse
                doLog("Milight Script: Receiving response: " + dataResponse)
            break

        except socket.timeout:
            print "[DEBUG] timeout on command       :", sendCommand
            doLog("Milight Script: Timeout on command... doing a retry")
            continue

        except Exception as ex:
            print "[DEBUG] something's wrong        :", ex
            doLog("Milight Script: Something's wrong with te command...")

        finally:
            if live:
                sockServer.close()
else:
    if live:
        sockServer.close()

doLog("Milight Script: Ready...")

raise SystemExit()
