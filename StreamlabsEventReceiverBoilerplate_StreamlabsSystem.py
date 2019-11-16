#!/usr/bin/python
# -*- coding: utf-8 -*-


#---------------------------------------
# Script Import Libraries
#---------------------------------------
import os
import json
import codecs
import clr

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

import sqlite3

clr.AddReferenceToFileAndPath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "StreamlabsEventReceiver.dll"))
from StreamlabsEventReceiver import StreamlabsEventClient


#---------------------------------------
# Script Information
#---------------------------------------
ScriptName = "Notifications"
Website = "twitch.tv/kobiqq"
Description = "Alert Notifications"
Creator = "KobiQQ"
Version = "1.2"

#---------------------------------------
# Variables
#---------------------------------------

m_ConfigFile = os.path.join(os.path.dirname(__file__), "Settings/settings.json")
m_ConfigFileJs = os.path.join(os.path.dirname(__file__), "Settings/settings.js")

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
            self.OnlyLive = True
            self.self.socket_token = None


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


#---------------------------------------
# Chatbot Initialize Function
#---------------------------------------
def Init():
	
    """Required tick function"""
    # Globals
    global MySettings
    MySettings = Settings()


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
    if ScriptSettings.socket_token:
        EventReceiver.Connect(ScriptSettings.socket_token)

    # End of Init
    return


def Execute(data):
	return

def Tick():
	return

#---------------------------------------
# Script Functions
#---------------------------------------
def EventReceiverConnected(sender, args):
	Parent.Log(ScriptName, "Connected")
	return

def EventReceiverDisconnected(senmder, args):
	Parent.Log(ScriptName, "Disconnected")

def EventReceiverEvent(sender, args):
    evntdata = args.Data
    if evntdata and evntdata.For == "twitch_account":
        if evntdata.Type == "follow":
            for message in evntdata.Message:
                Parent.SendStreamMessage ("" + message.Name + " Thank you for the Follow! kobiqqLove")
                updateLatestNotification("follow",message.Name,"0")

        elif evntdata.Type == "subscription":
            for message in evntdata.Message:

                if message.SubType == "resub":
                    Parent.Log("subscription", "{0} resubscribed for {1} months total!".format(message.Name, message.Months))
                    Parent.SendStreamWhisper("kobiqq","sub test!2" + str(message.Name))
                    updateLatestNotification("sub",message.Name,message.Months)
                    #message.Months
                    Parent.SendStreamMessage ("" + str(message.Name) + " kobiqqChampion. Thank you for your continious support!")
                elif message.SubType == "subscriber" and message.Months >= 1:
                    Parent.Log("subscription", "{0} resubscribed for {1} months total!".format(message.Name, message.Months))
                    Parent.SendStreamWhisper("kobiqq","sub test!" + str(message.Name))
                    updateLatestNotification("sub",message.Name,message.Months)
                else:
                    Parent.Log("subscription", "{0} subscribed!".format(message.Name))
                    Parent.SendStreamMessage ("We got a new Squirrel in the Family. Thank You " + str(message.Name) + " for your support! kobiqqChampion")
                    #deutsch + englisch message
                    #alle sub perks auf meiner website + link
                    Parent.SendStreamWhisper(message.Name,"Hey, Willkommen im Sub-Club. Ich hoffe, du wirst Freude an deinen neuen Emotes haben! kobiqqLove kobiqqChampion kobiqqGG. Vergiss nicht dein Discord mit Twitch zu verknuepfen, um alle Sub-perks nutzen zu koennen. Kobi!")
                    updateLatestNotification("sub",message.Name,"0")

        elif evntdata.Type == "bits":

            for message in evntdata.Message:
                bitName   = message.Name
                bitAmount = message.Amount
                bitMessage = message.Message 
                splitted = bitMessage.split()
                BanWord1 = splitted[1].lower()
                BanWord2 = splitted[2].lower()
                Parent.Log("bits",str(bitName))
                dict = {"bitName":bitName,"bitAmount":bitAmount,"BanWord1":BanWord1,"BanWord2":BanWord2}
                Parent.BroadcastWsEvent("EVENT_CURRENCY_SHOW_BIT_SLOTS", json.dumps(dict))
                Parent.SendStreamWhisper("kobiqq","bit test!" + str(message.Name))
                updateLatestNotification("bits",bitName,bitAmount)

        elif evntdata.Type == "host":

            for message in evntdata.Message:
                hostName     = message.Name
                hostViewers  = message.Viewers  
                #Parent.Log("host","testRaid")
                Parent.SendStreamWhisper("kobiqq","host test!" + str(message.Name))
                updateLatestNotification("host",hostName,hostViewers)

        elif evntdata.Type == "raid":

            for message in evntdata.Message:
                raidName     = message.Name
                raidViewers  = message.Raiders  
                Parent.SendStreamMessage ("Uii ein Raid mit " + str(raidViewers) + " von " + str(message.Name) + ", Vielen dank!! Wo bleibt das !hype?!" )
                #Parent.Log("raid","testRaid")
                Parent.SendStreamWhisper("kobiqq","raid test!" + str(message.Name))
                updateLatestNotification("raid",raidName,raidViewers)


    elif evntdata and evntdata.For == "streamlabs":

        if evntdata.Type == "donation":

            for message in evntdata.Message:
                donationName     = message.Name
                donationAmount = message.Amount
                Parent.Log("donate2",str(donationName))
                Parent.Log("donate2",str(donationAmount))
                dict = {"donationName":donationName,"donationAmount":donationAmount}
                Parent.BroadcastWsEvent("EVENT_SHOW_DONATION", json.dumps(dict))
                Parent.SendStreamWhisper("kobiqq","donation test!")
                updateLatestNotification("donation",donationName,donationAmount)


    return


def updateLatestNotification(eventType,fromName,amount):

    conn = sqlite3.connect(os.path.dirname(__file__) + "/../Datenbanken/streamMetaData.db")
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
        if ScriptSettings.socket_token:
            EventReceiver.Connect(ScriptSettings.socket_token)

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
