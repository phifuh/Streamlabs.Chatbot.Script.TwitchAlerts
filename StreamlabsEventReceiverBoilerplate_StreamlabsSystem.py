#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Streamlabs Event Receiver Boilerplate

    original creator Ocgineer

"""
import os
import json
import codecs
import clr


#---------------------------------------
# Script Import Libraries
#---------------------------------------
clr.AddReference("IronPython.Modules.dll")
clr.AddReferenceToFileAndPath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "StreamlabsEventReceiver.dll"))
from StreamlabsEventReceiver import StreamlabsEventClient


#---------------------------------------
# Script Information
#---------------------------------------
ScriptName = "Streamlabs Event Receiver"
Website = "kobiqq"
Description = "Streamlabs Event Receiver Boilerplate orginal from Ocgineer"
Creator = "Kobiqq"
Version = "1.1"

#---------------------------------------
# Script Variables
#---------------------------------------
SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
EventReceiver = None

#---------------------------------------
# Script Classes
#---------------------------------------
class Settings(object):
	""" Load in saved settings file if available else set default values. """
	def __init__(self, settingsfile=None):
		try:
			with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
				self.__dict__ = json.load(f, encoding="utf-8")
		except:
			self.socket_token = None

	def Reload(self, jsondata):
		""" Reload settings from AnkhBot uEventReceiver interface by given json data. """
		self.__dict__ = json.loads(jsondata, encoding="utf-8")

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
                #Parent.Log("follow", message.Name)
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

#---------------------------------------
# Chatbot Initialize Function
#---------------------------------------
def Init():
	
	# Load settings from settings file
    global ScriptSettings
    ScriptSettings = Settings(SettingsFile)

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

#---------------------------------------
# Chatbot Save Settings Function
#---------------------------------------
def ReloadSettings(jsondata):
	
	# Reload newly saved settings and verify
	ScriptSettings.Reload(jsondata)

	# Connect if token has been entered and EventReceiver is not connected
	# This can then connect without having to reload the script
	if EventReceiver and not EventReceiver.IsConnected:
		if ScriptSettings.socket_token:
			EventReceiver.Connect(ScriptSettings.socket_token)

	# End of ReloadSettings
	return

#---------------------------------------
#	Chatbot Script Unload Function
#---------------------------------------
def Unload():

	# Disconnect EventReceiver cleanly
	global EventReceiver
	if EventReceiver and EventReceiver.IsConnected:
		EventReceiver.Disconnect()
	EventReceiver = None

	# End of Unload
	return

#---------------------------------------
# Chatbot Execute Function
#---------------------------------------
def Execute(data):
	return

#---------------------------------------
# Chatbot Tick Function
#---------------------------------------
def Tick():
	return


def updateLatestNotification(type,fromName,amount):

    conn = sqlite3.connect(os.path.dirname(__file__) + "/../Datenbanken/streamMetaData.db")
    c = conn.cursor()

    try:
        c.execute("UPDATE latestNotifications SET byName ='" + str(fromName) + "',amount ='" + str(amount) + "' WHERE type='" + str(type) + "'")
        conn.commit()

    except:
        c.execute("INSERT INTO latestNotifications ('type','byName','amount') values ('" + str(type) + "','" + str(fromName) + "','" + str(amount) + "') ")
        conn.commit()

    finally:
        conn.close()
    

    return


#c.execute("DELETE FROM whisperuser WHERE id='" + str(userID) + "'")
#c.execute("INSERT INTO whisperuser ('name','whisperAttempts') values ('" + viewers + "','" + str(case) + "') ")
#c.execute("UPDATE viptracking SET VIPPoints ='" + str(VIPPoints) + "' WHERE name='" + str(viewers) + "'")