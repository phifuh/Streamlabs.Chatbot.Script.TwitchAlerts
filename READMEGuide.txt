This is a boilerplate script how to use the StreamlabsEventReceiver.dll created by Ocgineer#0042
in Chatbot Python scripts to receive real time Streamlabs events. This script is intended for 
script developers only!

The SocketKey users need to enter to connect to Streamlabs Socket API can be found on the API Settings
page; https://streamlabs.com/dashboard/#/settings/api-settings > API Tokens and enter that as a setting
as done in this boilerplate as an example.


The following describes the objects that can be contained within the Data object;

##############################################

Data.For (string)

    "twitch_account"
    "mixer_account"
    "youtube_account"
    "streamlabs"

##############################################

Data.Type (string) for *twitch_account*

    "follow"
    "subMisteryGift"
    "subscription"
    "resub" 		-- seems to be used only for testing resub alert?
    "bits"
    "host"
    "raid"

--------------------------------------------

Data.Type (string) for *mixer_account*

    "follow"
    "subscription"
    "host"

--------------------------------------------

Data.Type (string) for *youtube_account*

    "follow" (actual subscription)
    "subscription" (sponsor)
    "superchat"

--------------------------------------------

Data.Type (string) for *streamlabs*

Message object "donation"

    Name (string)
    Amount (int)

##############################################

Data.Message (list)

    contains objects specific for the platform and event
    ** THIS IS A LIST AND MULTIPLE EVENTS CAN BE IN IT **

----------------------

Message object Twitch follow

    Name (string)
    IsTest (bool)
    IsRepeat (bool)
    IsLive (bool)
    Id (string)
    CreatedAt (DateTime)


Message object Twitch subscriber or resub

    Name (string)
    IsTest (bool)
    IsRepeat (bool)
    IsLive (bool)
    DisplayName (string)
    Message (string)
    Gifter (string)
    Months  (int)
    StreakMonths (nullable int)  	-- investigating when exactly holds value (resub type)
    SubPlan (string)
    SubPlanName (string)
    SubType (string) 			-- "sub" | "resub" investigating if twitch & SL changes did something to this.


Message object Twitch subMisteryGift

    Name (string)
    IsTest (bool)
    IsRepeat (bool)
    IsLive (bool)
    Amount (int)
    Gifter (string)
    GifterDisplayName (string)
    SubPlan (string)
    SubType (string)


Message object Twitch bits

    Name (string)
    IsTest (bool)
    IsRepeat (bool)
    IsLive (bool)
    Message (string)
    Amount (int)


Message object Twitch host

    Name (string)
    IsTest (bool)
    IsRepeat (bool)
    IsLive (bool)
    Viewers (int)


Message object Twitch raid

    Name (string)
    IsTest (bool)
    IsRepeat (bool)
    IsLive (bool)
    Raiders (int)

-----------------------

Message object Mixer follow

    Name (string)
    IsTest (bool)
    IsRepeat (bool)
    IsLive (bool)
    CreatedAt (datetime)


Message object Mixer subscription

    Name (string)
    IsTest (bool)
    IsRepeat (bool)
    IsLive (bool)
    Months (int)
    Message (string)
    CreatedAt (datetime)


Message object Mixer host

    Name (string)
    IsTest (bool)
    IsRepeat (bool)
    IsLive (bool)
    Viewers (int)
    
-----------------------

Message object YouTube follow (subscription)

    Name (string)
    IsTest (bool)
    IsRepeat (bool)
    IsLive (bool)
    Id (string)
    CreatedAt (datetime)

Message object YouTube subscription (sponsor)

    Name (string)
    IsTest (bool)
    IsRepeat (bool)
    IsLive (bool)
    Id (string)
    SponsorSince (datetime)
    ChannelUrl (string)
    Months (int)

Message object YouTube superchat

    Name (string)
    IsTest (bool)
    IsRepeat (bool)
    IsLive (bool)
    Id (string)
    ChannelId (string)
    ChannelUrl (string)
    Message (string)
    Amount (int)
    Currency (string)
    FormattedAmount (string)
    CreatedAt (datetime)