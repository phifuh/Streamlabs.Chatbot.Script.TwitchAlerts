#!/usr/bin/python
# -*- coding: utf-8 -*-


#1022 lines of code before
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
import traceback

clr.AddReferenceToFileAndPath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "StreamlabsEventReceiver.dll"))
from StreamlabsEventReceiver import StreamlabsEventClient

sys.path.append(os.path.join(os.path.dirname(__file__), "../globalFiles/Moduls/pythonWrapper"))
import cBotWrapper

clr.AddReferenceToFileAndPath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../globalFiles/Moduls/personalDll/twitchAPI/bin/Debug/netstandard2.0/twitchAPI.dll"))
from twitchRestAPI import *


sys.path.append(os.path.join(os.path.dirname(__file__), "../globalFiles/Moduls/pythonClasses"))
from OBSRemoteParameters import *
import streamlabsSettingClass

from datetime import datetime
from datetime import date


ScriptName = "Notifications"
Website = "twitch.tv/kobiqq"
Description = "Stream controls + Notification"
Creator = "Global | KobiQQ"
Version = "1.2"

EventReceiver = None

ReadMeFile = os.path.join(os.path.dirname(__file__), "ReadMe.txt")
CopyrightFile = os.path.join(os.path.dirname(__file__), "Copyright.txt")

def Init():
	

	#Moduls/classes
	global twitchAPICalls, obsRemote,donationBarIsHidden

	donationBarIsHidden = True
	
	global ScriptSettings
	SettingsFile = os.path.join(os.path.dirname(__file__), "Settings/settings.json")
	ScriptSettings = streamlabsSettingClass.scriptSettings(SettingsFile)

	global wrapper
	wrapper = cBotWrapper.CBotWrapperClass(Parent)

	twitchAPICalls = StandartAPICalls()
	obsRemote = obsRemoteClass(Parent)

	global commercialActive
	commercialActive = False

	initEventAlertBar()
	initDonationBar()
	updateGameIconInUIBar()
	initNotficationGoals()

	#check if OBS is connected 
	testOBSConnection()


	## Init the Streamlabs Event Receiver
	global EventReceiver
	EventReceiver = StreamlabsEventClient()
	EventReceiver.StreamlabsSocketConnected += EventReceiverConnected
	EventReceiver.StreamlabsSocketDisconnected += EventReceiverDisconnected
	EventReceiver.StreamlabsSocketEvent += EventReceiverEvent

	## Auto Connect if key is given in settings
	if ScriptSettings.socket_token:
		EventReceiver.Connect(ScriptSettings.socket_token)

	global lastTimestamp
	lastTimestamp = time.time()

	return


def Execute(data):

	if data.IsChatMessage() :
		#and (Parent.IsLive() or not ScriptSettings.OnlyLive)
		userName = Parent.GetDisplayName(data.User) 

		if data.GetParam(0).lower() == ScriptSettings.runADCommand and Parent.HasPermission(data.User,"caster",userName) == True:

			global adLenght

			if (data.GetParam(1).lower() != None):
				adLenght = data.GetParam(1)
			else:
				adLenght = 30

			channelID = "26197959"
			twitchAPICalls.runAD(Parent,str(channelID), str(adLenght))

			#runAD(adLenght)

			commercialActive = True

			wrapper.sendSocketEvents(["Commercial_Run"],[{"":""}])
			obsRemote.changeToScene("Commercial", 0)

		elif data.GetParam(0).lower() == ScriptSettings.runADCommand and Parent.HasPermission(data.User,"subscriber",userName) == True and data.GetParam(1).lower() != None:

			adViewerEngageMent = data.GetParam(1)
			wrapper.sendSocketEvents(["Commercial_Run"],[{"viewerChoice":adViewerEngageMent}])

		elif data.GetParam(0).lower() == ScriptSettings.changeUI and Parent.HasPermission(data.User,"caster",userName) == True:

			changeUI = data.GetParam(1).lower()

			if changeUI == "on" or changeUI == "visible" or changeUI == "off" or changeUI == "hide" or changeUI == "hidden":

				if changeUI == "on" or changeUI == "visible":
					changeUI = "Visible"
				else:
					changeUI = "Hidden"

				wrapper.sendSocketEvents(["Alerts_ToggleUI_Visibility"],[{"UIvisibility":changeUI}])

			else:

				wrapper.sendSocketEvents(["Alerts_ChangeUI_Position"],[{"UIPosition":changeUI}])
		
		elif data.GetParam(0).lower() == "!dono" and Parent.HasPermission(data.User,"caster",userName) == True:

			changeUI = data.GetParam(1).lower()

			if changeUI == "on" or changeUI == "visible":
				changeUI = "Visible"
			else:
				changeUI = "Hidden"

			wrapper.sendSocketEvents(["Alerts_ToggleDonationUI_Visibility"],[{"donationBarvisibility":changeUI}])

		elif data.GetParam(0).lower() == "!uiupdate":

			if (data.GetParam(1).lower() != None):
				game = data.GetParam(1)
			else:
				game = "default"


			eventList = []
			varList = []

			#TTS alert with streak
			eventList.append("Alerts_changeUIDesign")
			dict = {"game":game}
			varList.append(dict)
			dict = {"eventList":eventList,"varList":varList} 

			Parent.BroadcastWsEvent("sendEvent", json.dumps(dict, ensure_ascii=False).encode('utf8'))


	return

def Tick():

	global commercialActive,lastTimestamp,donationBarIsHidden

	#Not implemented
	if commercialActive:

		#play music or minigame function which is not definied
		if time.time() - tournyRegistrationPeriodStart < adLenght:
			pass

		else:
			commercialActive = False
			obsRemote.changeToScene("Switch ingame", 0)
			
	#Sliding the donation bar in after the Intervall is done
	if ScriptSettings.donationBarActive:

		#Parent.Log(ScriptName, str(ScriptSettings.donationBarActive))

		if time.time() - lastTimestamp > ScriptSettings.donationBarCDTime + ScriptSettings.donationBarVisibleTime and donationBarIsHidden == True :

			lastTimestamp = time.time()
			
			donationBarIsHidden = False
			wrapper.sendSocketEvents(["donationBarSlide"],	[{"slideStatus":"slideIn"}])

		elif time.time() - lastTimestamp > ScriptSettings.donationBarVisibleTime and donationBarIsHidden == False:

			donationBarIsHidden = True
			wrapper.sendSocketEvents(["donationBarSlide"],	[{"slideStatus":"slideOut"}])

	return


#Event Reciever Code Block
#region
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

		#Parent.Log("Event type",str(evntdata.Type))

		if evntdata.Type == "follow":

			for message in evntdata.Message:

				if ScriptSettings.activateFollowMessage:

					wrapper.message(str(ScriptSettings.followMessage.format(message.Name)))

				updateLatestNotification("follow",message.Name,"0")
				wrapper.sendSocketEvents(["Alerts_showFollowEvent"],	[{"userName":message.Name}])

				#updateGoal()

		elif evntdata.Type == "subscription":
			for message in evntdata.Message:

				if message.SubType == "resub":

					Parent.Log(ScriptName,"resub streak 00")

					if ScriptSettings.activateSubscribeMessage:

						wrapper.message(str(ScriptSettings.reSubMessage.format(message.Name)))
						wrapper.log("resub streak 11")

					wrapper.log("resub streak 22")

					updateLatestNotification("sub",message.Name,message.Months)
					subName = message.Name

					wrapper.sendSocketEvents(["Alerts_showSubEvent"],	[{"userName":message.Name,"subAmount":message.Months}])

					wrapper.log("resub streak 33")

					userID = twitchFuncs.getTwitchUserID(Parent,str(message.Name))
					insertProfileData(userID,str(subName),"sub",str(message.Months))

					Parent.Log(ScriptName,"resub streak 4")
					Parent.Log(ScriptName,str(message.Months))

				elif message.SubType == "subscriber" and message.Months >= 1:

					#welcome back sub?
					wrapper.log("resub 00")

					if ScriptSettings.activateSubscribeMessage:

						wrapper.message(str(ScriptSettings.wbSubMessage.format(message.Name, message.Months)))
						wrapper.log("resub 1111")
					
					updateLatestNotification("sub",message.Name,message.Months)
					
					wrapper.sendSocketEvents(["Alerts_showSubEvent"],	[{"userName":message.Name,"subAmount":message.Months}])
					wrapper.log("resub 2222")

					subName = message.Name
					userID = twitchFuncs.getTwitchUserID(Parent,str(message.Name))
					insertProfileData(userID,str(subName),"sub",str(message.Months))

					wrapper.log("resub 3333")

				else:

					if ScriptSettings.activateSubscribeMessage:

						wrapper.message(str(ScriptSettings.newSubMessage.format(message.Name)))

					updateLatestNotification("sub",message.Name,"0")

					wrapper.sendSocketEvents(["Alerts_showSubEvent"],	[{"userName":message.Name,"subAmount":message.Months}])

					subName = message.Name
					userID = twitchFuncs.getTwitchUserID(Parent,str(message.Name))
					insertProfileData(userID,str(subName),"sub",str(1))

		elif evntdata.Type == "bits":

			for message in evntdata.Message:

				bitAmount = message.Amount
				bitMessage = message.Message 

				if ScriptSettings.activateBitMessage:
					wrapper.message(str(ScriptSettings.bitsMessage.format(message.Name)))


				updateLatestNotification("bits",message.Name,bitAmount)


				if ScriptSettings.banChampWithBits:

					splitted = bitMessage.split()
					BanWord1 = splitted[1].lower()
					BanWord2 = splitted[2].lower()
					Parent.Log("bits",str(message.Name))

					wrapper.sendSocketEvents(["Alerts_showBitEvent","Alert_Ban_Slot"],	[{"userName":message.Name,"bitAmount":bitAmount},{"userName":message.Name,"bitAmount":bitAmount,"BanWord1":BanWord1,"BanWord2":BanWord2}])

				else:					
					wrapper.sendSocketEvents(["Alert_Bit_Slot"],	[{"userName":message.Name,"bitAmount":bitAmount}])


					
				userID = twitchFuncs.getTwitchUserID(Parent,str(message.Name))
				insertProfileData(userID,str(message.Name),"bits",str(bitAmount))

		elif evntdata.Type == "host":

			for message in evntdata.Message:
				hostName     = message.Name
				hostViewers  = message.Viewers  

				if ScriptSettings.activateHostMessage:
					wrapper.message(str(ScriptSettings.hostMessage.format(message.Name)))

				wrapper.sendSocketEvents(["Alerts_showHostEvent"],	[{"userName":hostName,"hostAmount":hostViewers}])

				updateLatestNotification("host",hostName,hostViewers)
				userID = twitchFuncs.getTwitchUserID(Parent,str(message.Name))

		#check iif this is working
		elif evntdata.Type == "raid":

			for message in evntdata.Message:
				raidName     = message.Name
				raidViewers  = message.Raiders  

				if ScriptSettings.activateRaidMessage:
					wrapper.message(str(ScriptSettings.raidMessage.format(raidViewers,raidName)))

				if int(raidViewers) > 1:
					wrapper.message("Attention bois and girls. Check out twitch.tv/" + str(raidName) + " . A follow is free! ")

				updateLatestNotification("raid",raidName,raidViewers)

				wrapper.sendSocketEvents(["Alerts_showRaidEvent"],	[{"userName":message.Name}])


	elif evntdata and evntdata.For == "streamlabs":

		if evntdata.Type == "donation":

			for message in evntdata.Message:
				donationName     = message.Name
				donationAmount = message.Amount

				wrapper.log("dono came through")
				wrapper.sendSocketEvents(["Alerts_showDonationEvent"],	[{"userName":donationName,"donationAmount":donationAmount}])

				Parent.SendStreamWhisper("kobiqq","donation Test" + str(ScriptSettings.donation.format(message.Name)))
				updateLatestNotification("donation",donationName,donationAmount)
				insertProfileData(userID,message.Name,"donation",donationAmount)

				updateDonationTracker()

	return
#endregion

def dbConnection(dbName):
	"""Documentation: Decorater (Generic template function)\n
Arguments:	DB name - to select the correct Database		
Description:	Send a SQL querry to the decorator.
Return Value:	None\n
Notes: If I would define the dbName == "marioMaker": / conn 
in this scope, then its only called once at the creation of the decorator class. 
It was working fine in testing because its always called a new instance, but when apps are running we have to change the 
db name inside of the inner scope 
	"""

	path = "../../globalFiles/Datenbanken/" + str(dbName) + ".db"

	def dbConnector(fn):

		def invokeSQLQuerry(*args):

			conn = sqlite3.connect(os.path.abspath(os.path.join(__file__ , path)), check_same_thread=False)
			c = conn.cursor()

			try:
				result = fn(c,*args)

			except Exception as err:
				Parent.Log(ScriptName,"\nTraceback Error \n" + str(traceback.format_exc()))
				Parent.Log(ScriptName,"Query Failed in: " + str(fn) + " with the Error " + str(err) + "the absolute path of the DB" + str(path))
			else: 
				conn.commit()              
				return result          
			finally:
				conn.close()

		return invokeSQLQuerry

	return dbConnector

def testOBSConnection():

	wrapper.sendSocketEvents(["Alerts_showFollowEvent"],	[{"userName":"-"}])

@dbConnection("streamMetaData")
def initEventAlertBar(c):
	
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

	wrapper.sendSocketEvents(["Alerts_Init"],	[{"followName":followName,"subName":subName,"subAmount":subAmount,"bitsName":bitsName,"bitsAmount":bitsAmount,"donationName":donationName,"donationAmount":donationAmount}])

	return

@dbConnection("streamMetaData")
def initDonationBar(c):

	c.execute("SELECT artikel,amount,bereitsGespendet,endDate FROM donation ORDER BY ranking ASC LIMIT 1")
	row = c.fetchone()

	artikel = row[0]
	neededAmount = row[1]
	bereitsGespendet = row[2]
	endDate = row[3]

	wrapper.sendSocketEvents(["Init_Donationbar"],	[{"artikel":artikel,"neededAmount":neededAmount,"bereitsGespendet":bereitsGespendet,"endDate":endDate}])


	return

@dbConnection("streamMetaData")
def initNotficationGoals(c):

	rightNow = datetime.strptime(""+str(datetime.now().day)+"/"+str(datetime.now().month)+"/"+str(datetime.now().year), "%d/%m/%Y")

	c.execute("SELECT dailyTimestamp FROM notficationGoals WHERE id='1'")
	row = c.fetchone()
		
	lastUpdatedDate  =  row[0]

	comparissionDate = datetime.strptime(lastUpdatedDate, "%d/%m/%Y")
	stringDate = ""+str(datetime.now().day)+"/"+str(datetime.now().month)+"/"+str(datetime.now().year)+""

	if (rightNow - comparissionDate).days >= 1:

		resetDailyGoals(stringDate)

	return

@dbConnection("streamMetaData")
def updateLatestNotification(c,eventType,fromName,amount):

	c.execute("SELECT fromViewer FROM latestNotifications WHERE alertType=?",(eventType,))
	row = c.fetchone()
	if row:

		c.execute("UPDATE latestNotifications SET fromViewer =? ,amount =? WHERE alertType=?",(fromName,amount,eventType,))

	else:
		c.execute("INSERT INTO latestNotifications ('alertType','fromViewer','amount') values (?,?,?) ",(eventType,fromName,amount,))

	return

@dbConnection("streamMetaData")
def resetDailyGoals(c,stringDate):

	c.execute("UPDATE notficationGoals SET dailyFollowers ='0', dailySubs ='0', dailyBits ='0', dailyDonation ='0', dailyTimestamp =? WHERE id='1'",(stringDate,))

	return

@dbConnection("streamUserData")
def insertProfileData(c,twitchID,userName,supportType,Amount):

	c.execute("SELECT totalSub,totalBits,totalDonation,totalGiftedSubs FROM profileData WHERE twitchID=?",(twitchID,))
	row = c.fetchone()
	if row:

		totalSub = row[0]
		totalBits = row[1]
		totalDonation = row[2]
		totalGiftedSubs = row[3]

		if supportType == "sub":

			newTotalSub = int(Amount) 
			c.execute("UPDATE profileData SET userName =?,totalSub =? WHERE twitchID=?",(userName,newTotalSub,twitchID,))

		elif supportType == "bits":

			newTotalBits = int(totalBits) + int(Amount) 
			c.execute("UPDATE profileData SET userName =?, totalBits =? WHERE twitchID=?",(userName,newTotalBits,twitchID,))

		elif supportType == "donation":

			newTotalDonation = int(totalDonation) + int(Amount) 
			c.execute("UPDATE profileData SET userName =?,totalDonation =? WHERE twitchID=?",(userName,newTotalDonation,twitchID,))

		elif supportType == "giftedSub":

			newTotalGiftesSubs = int(totalGiftedSubs) + int(Amount) 
			c.execute("UPDATE profileData SET userName =? ,totalGiftedSubs =? WHERE twitchID=?",(userName,newTotalGiftesSubs,twitchID,))

	else:

		if supportType == "sub":

			c.execute("INSERT INTO profileData ('twitchID','userName','totalSub','totalBits','totalDonation','totalGiftedSubs') values (?,?,?,?,?,?) ",(twitchID,userName,Amount,0,0,0,))

		elif supportType == "bits":

			c.execute("INSERT INTO profileData ('twitchID','userName','totalSub','totalBits','totalDonation','totalGiftedSubs') values (?,?,?,?,?,?) ",(twitchID,userName,0,Amount,0,0,))

		elif supportType == "donation":

			c.execute("INSERT INTO profileData ('twitchID','userName','totalSub','totalBits','totalDonation','totalGiftedSubs') values (?,?,?,?,?,?) ",(twitchID,userName,0,0,Amount,0,))
		
		elif supportType == "giftedSub":

			c.execute("INSERT INTO profileData ('twitchID','userName','totalSub','totalBits','totalDonation','totalGiftedSubs') values (?,?,?,?,?,?) ",(twitchID,userName,0,0,0,Amount,))

	return

@dbConnection("streamMetaData")
def updateGameIconInUIBar(c):

	c.execute("SELECT game FROM gameStats WHERE id='1'")
	row = c.fetchone()
	game = row[0]

	wrapper.sendSocketEvents(["updateGameIcons"],	[{"currentGame":game}])


def updateDonationTracker():

	#run update sql
	wrapper.sendSocketEvents(["updateDonoBar"],	[{"donationProgress":donationPercentage}])

def changeUIPositionBtn():

	wrapper.sendSocketEvents(["Alerts_ChangeUI_Position"],	[{"UIPosition":ScriptSettings.UI_Position.lower()}])

	return

def changeUIVisiblityBtn():

	wrapper.sendSocketEvents(["Alerts_ToggleUI_Visibility"],[{"UIvisibility":ScriptSettings.UI_Visibility}])

	return

def donationVisibilityBtn():

	changeDonationUI = ScriptSettings.donationVisibility.lower()

	#wrapper.log(str(changeDonationUI))

	if changeDonationUI == "visible":
		changeDonationUI = "Visible"
	else:
		changeDonationUI = "Hidden"

	wrapper.sendSocketEvents(["Alerts_ToggleDonationUI_Visibility"],	[{"donationBarvisibility":changeDonationUI}])

	return


#Stream Control - Presets and ADS
#region
def runADfromUI():

	twitchAPICalls.runAD(Parent,str(ScriptSettings.OauthToken), str(ScriptSettings.ADInterval))

	return

def presetOne():
	
	return

def presetTwo():
	
	return

def presetThree():
	
	return

def updateTwitchTitleAndGame():


	return
#endregion

#UI Elements - Readme - Copyright - Stream
#region
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
#endregion


#SETTINGS functions: save changes in the UI / Reload / deafault
#region 
def ReloadSettings(jsondata):

	"""	ReloadSettings is an optional function that gets called once the user clicks on
		the Save Settings button of the corresponding script in the scripts tab if an
		user interface has been created for said script. The entire Json object will be
		passed to the function	so you can load that back	into your settings without
		having to read the newly saved settings file."""

	ScriptSettings.Reload(jsondata)

	if EventReceiver and not EventReceiver.IsConnected:
		if ScriptSettings.socket_token:
			EventReceiver.Connect(ScriptSettings.socket_token)

	return

def SetDefaults():

	""" SetDefaults Custom User Interface Button """
	defaultSettings = defaultScriptSettings()
	defaultSettings.Save()

	return

def Unload():

	# Disconnect EventReceiver cleanly
	global EventReceiver
	if EventReceiver and EventReceiver.IsConnected:
		EventReceiver.Disconnect()
	EventReceiver = None

	return
#endregion

