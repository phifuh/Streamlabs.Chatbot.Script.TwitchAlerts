#!/usr/bin/python
# -*- coding: utf-8 -*-


#---------------------------------------
# Script Import Libraries
#---------------------------------------
import sys
import json
import os
import codecs
import datetime
import operator
import clr
import time

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

import sqlite3

clr.AddReferenceToFileAndPath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "StreamlabsEventReceiver.dll"))
from StreamlabsEventReceiver import StreamlabsEventClient

clr.AddReferenceToFileAndPath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../globalFiles/Moduls/basicFunctionality/bin/Debug/netstandard2.0/basicFunctionality.dll"))
from basicFunctions import *

from datetime import datetime
#---------------------------------------
# Script Information
#---------------------------------------
ScriptName = "Notifications"
Website = "twitch.tv/kobiqq"
Description = "Alert Notifications"
Creator = "Global | KobiQQ"
Version = "1.2"

#---------------------------------------
# Variables
#---------------------------------------

m_ConfigFile = os.path.join(os.path.dirname(__file__), "Settings/settings.json")
m_ConfigFileJs = os.path.join(os.path.dirname(__file__), "Settings/settings.js")

PrestigeFile = os.path.join(os.path.dirname(__file__), "testFile.txt")

EventReceiver = None
#---------------------------------------
# Classes Tries to load settings from file if given The 'default' variable names need to match UI_Config
#---------------------------------------
class Settings:
    """" Loads settings from file if file is found if not uses default values"""

    # The 'default' variable names need to match UI_Config
    def __init__(self, settingsFile=None):
        if settingsFile and os.path.isfile(settingsFile):
            with codecs.open(settingsFile, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig')
         
        else: #set variables if no settings file
            self.socket_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6IkRFMDhFOTQ4QjdFRTFBNzcwRjBBIiwicmVhZF9vbmx5Ijp0cnVlLCJwcmV2ZW50X21hc3RlciI6dHJ1ZSwidHdpdGNoX2lkIjoiMjYxOTc5NTkifQ.0kJX4Rd8USk_UYizxrAXRurFOeGCBgU8Q7C_z5Ccb9I"
            self.activateFollowMessage = True
            self.followMessage = "@{0} Thank you for the Follow!"
            self.activateSubscribeMessage = True
            self.newSubMessage = "We got a new Squirrel in the Family. Thank You {0} for your support!"
            self.reSubMessage = "Resub!"
            self.wbSubMessage = "Welcome Back Sub!"
            self.activateBitMessage = True
            self.bitsMessage = "Thanks a lot for Bits {0}"
            self.activateHostMessage = True
            self.hostMessage = "Thanks a lot for the Host {0}"
            self.activateRaidMessage = True
            self.raidMessage = "Raid Test"
            self.activateDonationMessage = True
            self.donation = "donation test"
            self.banChampWithBits = False


    # Reload settings on save through UI
    def ReloadSettings(self, data):
        """Reload settings on save through UI"""
        self.__dict__ = json.loads(data, encoding='utf-8-sig')
        return

    # Save settings to files (json and js)
    def SaveSettings(self, settingsFile):
        """Save settings to files (json and js)"""
        with codecs.open(settingsFile, encoding='utf-8-sig', mode='w+') as f:
            json.dump(self.__dict__, f, encoding='utf-8-sig')
        with codecs.open(settingsFile.replace("json", "js"), encoding='utf-8-sig', mode='w+') as f:
            f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8-sig', ensure_ascii=False)))
        return

MySettings = Settings()
ReadMeFile = os.path.join(os.path.dirname(__file__), "ReadMe.txt")
CopyrightFile = os.path.join(os.path.dirname(__file__), "Copyright.txt")

#---------------------------------------
# Chatbot Initialize Function
#---------------------------------------
def Init():
	
    """Required tick function"""
    # Globals
    global MySettings
    MySettings = Settings()

    global basic
    basic = getBasicFunctions()
    
    initAlerts()
    updateGameIconInUIBar()


    if not os.path.isfile(m_ConfigFile):
        text_file = codecs.open(m_ConfigFile, encoding='utf-8-sig', mode='w')
        out = json.dumps(MySettings.__dict__, encoding="utf-8-sig")
        text_file.write(out)
        text_file.close()
    else:
        with codecs.open(m_ConfigFile,encoding='utf-8-sig', mode='r') as ConfigFile:
            MySettings.__dict__ = json.load(ConfigFile)

    if not os.path.isfile(m_ConfigFileJs):
        text_file = codecs.open(m_ConfigFileJs, encoding='utf-8-sig', mode='w')
        jsFile = "var settings =" + json.dumps(MySettings.__dict__, encoding="utf-8-sig") + ";"
        text_file.write(jsFile)
        text_file.close()


    ## Init the Streamlabs Event Receiver
    global EventReceiver
    EventReceiver = StreamlabsEventClient()
    EventReceiver.StreamlabsSocketConnected += EventReceiverConnected
    EventReceiver.StreamlabsSocketDisconnected += EventReceiverDisconnected
    EventReceiver.StreamlabsSocketEvent += EventReceiverEvent

    ## Auto Connect if key is given in settings
    if MySettings.socket_token:
        EventReceiver.Connect(MySettings.socket_token)

    # End of Init
    return


def Execute(data):

    if data.IsChatMessage() and data.GetParam(0).lower() == "!testb":
        
        donationName = "Kobi QQ"
        donationAmount = 20
        eventList = []
        varList = []

        eventList.append("Alerts_showDonationEvent")
        varDict = {"userName":donationName,"donationAmount":donationAmount}
        varList.append(varDict)
        dict = {"eventList":eventList,"varList":varList} 

        Parent.BroadcastWsEvent("sendEvent", json.dumps(dict))

    if data.IsChatMessage() and data.GetParam(0).lower() == "!testc":
        
        Name = "Kobi QQ"
        Months = 20


        Parent.Log(ScriptName,str("subscription", "{0} resubscribed for {1} months total!" .format(Name, Months)))
        basic.streamWhisper(Parent,"kobiqq",str("subscription {0} resubscribed for {1} months Test!".format(Name, Months)))

    return

def Tick():
	return

#---------------------------------------
# Script Functions
#---------------------------------------
def EventReceiverConnected(sender, args):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    Parent.Log(ScriptName, "Connected at " + str(current_time))
    return

def EventReceiverDisconnected(senmder, args):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    Parent.Log(ScriptName, "Disconnected at " + str(current_time))

def EventReceiverEvent(sender, args):
    evntdata = args.Data

    if evntdata and evntdata.For == "twitch_account":

        if evntdata.Type == "follow":
            for message in evntdata.Message:

                if MySettings.activateFollowMessage:
                    basic.streamMessage(Parent,str(MySettings.followMessage.format(message.Name)))

                updateLatestNotification("follow",message.Name,"0")

                eventList = []
                varList = []

                eventList.append("Alerts_showFollowEvent")
                varDict = {"userName":message.Name}
                varList.append(varDict)
                dict = {"eventList":eventList,"varList":varList} 

                Parent.BroadcastWsEvent("sendEvent", json.dumps(dict))

        elif evntdata.Type == "subscription":
            for message in evntdata.Message:

                if message.SubType == "resub":

                    Parent.Log(ScriptName,"resub streak 0")

                    if MySettings.activateSubscribeMessage:

                        basic.streamMessage(Parent,str(MySettings.reSubMessage.format(message.Name)))

                        #I think there was a bug in the basic.Whispermessage
                        #Parent.Log(ScriptName,str("subscription", "{0} resubscribed for {1} months total!".format(message.Name, message.Months)))
                        #basic.streamWhisper(Parent,"kobiqq",str("subscription {0} resubscribed for {1} months Test!".format(message.Name, message.Months)))
                        
                        #Parent.Log(ScriptName,"resub streak 1")


                    Parent.Log(ScriptName,"resub streak 2")

                    updateLatestNotification("sub",message.Name,message.Months)
                    subName = message.Name

                    eventList = []
                    varList = []

                    eventList.append("Alerts_showSubEvent")
                    varDict = {"userName":message.Name,"subAmount":message.Months}
                    varList.append(varDict)
                    dict = {"eventList":eventList,"varList":varList} 

                    Parent.BroadcastWsEvent("sendEvent", json.dumps(dict))

                    Parent.Log(ScriptName,"resub streak 3")

                    userID = twitchFuncs.getTwitchUserID(Parent,str(message.Name))
                    insertProfileData(userID,str(subName),"sub",str(message.Months))

                    Parent.Log(ScriptName,"resub streak 4")
                    Parent.Log(ScriptName,str(message.Months))

                elif message.SubType == "subscriber" and message.Months >= 1:

                    #welcome back sub?
                    Parent.Log(ScriptName,"resub 0")

                    if MySettings.activateSubscribeMessage:
                        basic.streamMessage(Parent,str(MySettings.wbSubMessage.format(message.Name, message.Months)))

                        #Parent.Log(ScriptName,str("subscription", "{0} resubscribed for {1} months total!".format(message.Name, message.Months)))
                        #basic.streamWhisper(Parent,"kobiqq",str("subscription {0} resubscribed for {1} months Test!".format(message.Name, message.Months)))

                        Parent.Log(ScriptName,"resub 1")
                    
                    updateLatestNotification("sub",message.Name,message.Months)
                   
                    eventList = []
                    varList = []

                    eventList.append("Alerts_showSubEvent")
                    dict = {"userName":message.Name,"subAmount":message.Months}
                    varList.append(dict)
                    dict = {"eventList":eventList,"varList":varList} 

                    Parent.BroadcastWsEvent("sendEvent", json.dumps(dict))

                    Parent.Log(ScriptName,"resub 2")

                    subName = message.Name
                    userID = twitchFuncs.getTwitchUserID(Parent,str(message.Name))
                    insertProfileData(userID,str(subName),"sub",str(message.Months))

                    Parent.Log(ScriptName,"resub 3")

                else:

                    if MySettings.activateSubscribeMessage:

                        basic.streamMessage(Parent,str(MySettings.newSubMessage.format(message.Name)))
                        basic.streamWhisper(Parent,"kobiqq",str("first sub test"))

                    updateLatestNotification("sub",message.Name,"0")

                    eventList = []
                    varList = []

                    eventList.append("Alerts_showSubEvent")
                    dict = {"userName":message.Name,"subAmount":message.Months}
                    varList.append(dict)
                    dict = {"eventList":eventList,"varList":varList} 

                    Parent.BroadcastWsEvent("sendEvent", json.dumps(dict))

                    subName = message.Name
                    userID = twitchFuncs.getTwitchUserID(Parent,str(message.Name))
                    insertProfileData(userID,str(subName),"sub",str(1))

        elif evntdata.Type == "bits":

            for message in evntdata.Message:

                bitAmount = message.Amount
                bitMessage = message.Message 

                if MySettings.activateBitMessage:
                    basic.streamMessage(Parent,str(MySettings.bitsMessage.format(message.Name)))
                    basic.streamWhisper(Parent,"kobiqq",str("Bit Test succesfull" + str(MySettings.bitsMessage.format(message.Name))))

                updateLatestNotification("bits",message.Name,bitAmount)

                if MySettings.banChampWithBits:

                    splitted = bitMessage.split()
                    BanWord1 = splitted[1].lower()
                    BanWord2 = splitted[2].lower()
                    Parent.Log("bits",str(message.Name))

                    dict = {"userName":message.Name,"bitAmount":bitAmount,"BanWord1":BanWord1,"BanWord2":BanWord2}
                    Parent.BroadcastWsEvent("Alert_Ban_Slot", json.dumps(dict))

                eventList = []
                varList = []

                eventList.append("Alerts_showBitEvent")
                dict = {"userName":message.Name,"bitAmount":bitAmount}
                varList.append(dict)
                dict = {"eventList":eventList,"varList":varList} 

                Parent.BroadcastWsEvent("sendEvent", json.dumps(dict))
                    
                userID = twitchFuncs.getTwitchUserID(Parent,str(message.Name))
                insertProfileData(userID,str(message.Name),"bits",str(bitAmount))
              
        elif evntdata.Type == "host":

            for message in evntdata.Message:
                hostName     = message.Name
                hostViewers  = message.Viewers  

                if MySettings.activateHostMessage:
                    basic.streamMessage(Parent,str(MySettings.hostMessage.format(message.Name)))

                eventList = []
                varList = []

                eventList.append("Alerts_showHostEvent")
                varDict = {"userName":hostName,"hostAmount":hostViewers}
                varList.append(varDict)
                dict = {"eventList":eventList,"varList":varList} 

                Parent.BroadcastWsEvent("sendEvent", json.dumps(dict))

                updateLatestNotification("host",hostName,hostViewers)
                userID = twitchFuncs.getTwitchUserID(Parent,str(message.Name))

        #check iif this is working
        elif evntdata.Type == "raid":

            for message in evntdata.Message:
                raidName     = message.Name
                raidViewers  = message.Raiders  

                if MySettings.activateRaidMessage:
                    Parent.SendStreamMessage ("Woah a raid with " + str(raidViewers) + " by " + str(message.Name) + ", thanks a lot <3!" )
                updateLatestNotification("raid",raidName,raidViewers)

                eventList = []
                varList = []

                eventList.append("Alerts_showRaidEvent")
                varDict = {"userName":message.Name}
                varList.append(varDict)
                dict = {"eventList":eventList,"varList":varList} 

                Parent.BroadcastWsEvent("sendEvent", json.dumps(dict))


    elif evntdata and evntdata.For == "streamlabs":

        if evntdata.Type == "donation":

            for message in evntdata.Message:
                donationName     = message.Name
                donationAmount = message.Amount

                basic.streamWhisper(Parent,"kobiqq",str(donationName + " " + donationAmount))


                eventList = []
                varList = []

                eventList.append("Alerts_showDonationEvent")
                varDict = {"userName":donationName,"donationAmount":donationAmount}
                varList.append(varDict)
                dict = {"eventList":eventList,"varList":varList} 

                Parent.BroadcastWsEvent("sendEvent", json.dumps(dict))

                #dict = {"donationName":donationName,"donationAmount":donationAmount}
                #Parent.BroadcastWsEvent("EVENT_SHOW_DONATION", json.dumps(dict))

                Parent.SendStreamWhisper("kobiqq","donation Test" + str(MySettings.donation.format(message.Name)))
                updateLatestNotification("donation",donationName,donationAmount)
                insertProfileData(userID,message.Name,"donation",donationAmount)


    return

def updateLatestNotification(eventType,fromName,amount):

    conn = sqlite3.connect(os.path.dirname(__file__) + "/../globalFiles/Datenbanken/streamMetaData.db")
    c = conn.cursor()

    try:
        c.execute("SELECT fromViewer FROM latestNotifications WHERE alertType='" + str(eventType) + "'")
        row = c.fetchone()

        xoxo = row[0]

        c.execute("UPDATE latestNotifications SET fromViewer ='" + str(fromName) + "',amount ='" + str(amount) + "' WHERE alertType='" + str(eventType) + "'")
        conn.commit()

    except:
        c.execute("INSERT INTO latestNotifications ('alertType','fromViewer','amount') values ('" + str(eventType) + "','" + str(fromName) + "','" + str(amount) + "') ")
        conn.commit()

    finally:
        conn.close()
    

    return


def insertProfileData(twitchID,userName,supportType,Amount):


    conn = sqlite3.connect(os.path.dirname(__file__) + "/../globalFiles/Datenbanken/streamUserData.db")
    c = conn.cursor()

    try:

        c.execute("SELECT totalSub,totalBits,totalDonation,totalGiftedSubs FROM profileData WHERE twitchID='" + str(twitchID) + "'")
        row = c.fetchone()

        totalSub = row[0]
        totalBits = row[1]
        totalDonation = row[2]
        totalGiftedSubs = row[3]

        if supportType == "sub":

            newTotalSub = int(Amount) 
            c.execute("UPDATE profileData SET userName ='" + str(userName) + "',totalSub ='" + str(newTotalSub) + "' WHERE twitchID='" + str(twitchID) + "'")
            conn.commit()

        elif supportType == "bits":

            newTotalBits = int(totalBits) + int(Amount) 
            c.execute("UPDATE profileData SET userName ='" + str(userName) + "', totalBits ='" + str(newTotalBits) + "' WHERE twitchID='" + str(twitchID) + "'")
            conn.commit()

        elif supportType == "donation":

            newTotalDonation = int(totalDonation) + int(Amount) 
            c.execute("UPDATE profileData SET userName ='" + str(userName) + "',totalDonation ='" + str(newTotalDonation) + "' WHERE twitchID='" + str(twitchID) + "'")
            conn.commit()

        elif supportType == "giftedSub":

            newTotalGiftesSubs = int(totalGiftedSubs) + int(Amount) 
            c.execute("UPDATE profileData SET userName ='" + str(userName) + "',totalGiftedSubs ='" + str(newTotalGiftesSubs) + "' WHERE twitchID='" + str(twitchID) + "'")
            conn.commit()

    except:

        if supportType == "sub":

            c.execute("INSERT INTO profileData ('twitchID','userName','totalSub','totalBits','totalDonation','totalGiftedSubs') values ('" + str(twitchID) + "','" + str(userName) + "','" + str(Amount) + "','0','0','0') ")
            conn.commit()

        elif supportType == "bits":

            c.execute("INSERT INTO profileData ('twitchID','userName','totalSub','totalBits','totalDonation','totalGiftedSubs') values ('" + str(twitchID) + "','" + str(userName) + "','0','" + str(Amount) + "','0','0') ")
            conn.commit()

        elif supportType == "donation":

            c.execute("INSERT INTO profileData ('twitchID','userName','totalSub','totalBits','totalDonation','totalGiftedSubs') values ('" + str(twitchID) + "','" + str(userName) + "','0','0','" + str(Amount) + "','0') ")
            conn.commit()
        
        elif supportType == "giftedSub":

            c.execute("INSERT INTO profileData ('twitchID','userName','totalSub','totalBits','totalDonation','totalGiftedSubs') values ('" + str(twitchID) + "','" + str(userName) + "','0','0','0','"+ str(Amount) +"') ")
            conn.commit()

    finally:
        conn.close()

    return

def initAlerts():
    
    conn = sqlite3.connect(os.path.dirname(__file__) + "/../globalFiles/Datenbanken/streamMetaData.db")
    c = conn.cursor()

    try:

        c.execute("SELECT fromViewer,amount FROM latestNotifications WHERE alertType='follow'")
        row = c.fetchone()

        followName = row[0]

        c.execute("SELECT fromViewer,amount FROM latestNotifications WHERE alertType='sub'")
        row = c.fetchone()

        subName = row[0]
        subAmount = row[1]

        c.execute("SELECT fromViewer,amount FROM latestNotifications WHERE alertType='bits'")
        row = c.fetchone()

        bitsName = row[0]
        bitsAmount = row[1]

        c.execute("SELECT fromViewer,amount FROM latestNotifications WHERE alertType='donation'")
        row = c.fetchone()

        donationName = row[0]
        donationAmount = row[1]

        eventList = []
        varList = []

        eventList.append("Alerts_Init")
        dict = {"followName":followName,"subName":subName,"subAmount":subAmount,"bitsName":bitsName,"bitsAmount":bitsAmount,"donationName":donationName,"donationAmount":donationAmount}
        varList.append(dict)
        dict = {"eventList":eventList,"varList":varList} 

        Parent.BroadcastWsEvent("sendEvent", json.dumps(dict))

    except:

        pass

    finally:
        conn.close()

    return

def updateGameIconInUIBar():

    conn = sqlite3.connect(os.path.dirname(__file__) + "/../globalFiles/Datenbanken/streamMetaData.db")
    c = conn.cursor()

    try:

        c.execute("SELECT game FROM gameStats WHERE id='1'")
        row = c.fetchone()
        game = row[0]

    except:
        basicFuncs.printLog(Parent,str(ScriptName), "Error couldnt Open DB or find a game on ID 1")

    finally:
        conn.close()

    eventList = []
    varList = []

    eventList.append("updateGameIcons")
    varDict = {"currentGame":game}
    varList.append(varDict)
    dict = {"eventList":eventList,"varList":varList} 

    Parent.BroadcastWsEvent("sendEvent", json.dumps(dict))   

def OpenReadMe():
	""" Open the script readme file in users default .txt application. """
	os.startfile(ReadMeFile)
	return

def OpenCopyright():
	""" Open the script readme file in users default .txt application. """
	os.startfile(CopyrightFile)
	return

def OpenStream():
	os.startfile("https://www.twitch.tv/kobiqq")
	return

def OpenSL():
	os.startfile("https://streamlabs.com/dashboard/#/settings/api-settings")
	return




#c.execute("DELETE FROM whisperuser WHERE id='" + str(userID) + "'")
#c.execute("INSERT INTO whisperuser ('name','whisperAttempts') values ('" + viewers + "','" + str(case) + "') ")
#c.execute("UPDATE viptracking SET VIPPoints ='" + str(VIPPoints) + "' WHERE name='" + str(viewers) + "'")

#Reload Settings
def ReloadSettings(jsonData):
    MySettings.__dict__ = json.loads(jsonData)
    Parent.BroadcastWsEvent("EVENT_CURRENCY_RELOAD", jsonData)
    return

#---------------------------------------
# Reload Settings on Save
#---------------------------------------
def ReloadSettings(jsonData):
    # Globals
    global MySettings

    # Reload saved settings
    MySettings.ReloadSettings(jsonData)

    if EventReceiver and not EventReceiver.IsConnected:
        if MySettings.socket_token:
            EventReceiver.Connect(MySettings.socket_token)

    # End of ReloadSettings
    return

def UpdateSettings():
    with open(m_ConfigFile) as ConfigFile:
        MySettings.__dict__ = json.load(ConfigFile)
    return


def Unload():

	# Disconnect EventReceiver cleanly
	global EventReceiver
	if EventReceiver and EventReceiver.IsConnected:
		EventReceiver.Disconnect()
	EventReceiver = None

	# End of Unload
	return
