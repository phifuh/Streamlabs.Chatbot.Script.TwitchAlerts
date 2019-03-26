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
Description = "Streamlabs Event Receiver Boilerplate example script for developers"
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
                Parent.Log("follow", message.Name)

        elif evntdata.Type == "subscription":
            for message in evntdata.Message:
                if message.SubType == "resub":
                    Parent.Log("subscription", "{0} resubscribed for {1} months total!".format(message.Name, message.Months))
                else:
                    Parent.Log("subscription", "{0} subscribed!".format(message.Name))

        elif evntdata.Type == "bits":

            for message in evntdata.Message:
                bitName   = message.Name
                bitAmount = message.Amount 
                dict = {"name":bitName,"bitAmount":bitAmount}

                Parent.BroadcastWsEvent("EVENT_CURRENCY_SHOW_BIT_SLOTS", json.dumps(dict))

        elif evntdata.Type == "host":

            for message in evntdata.Message:
                hostName     = message.Name
                hostViewers  = message.Viewers  


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
