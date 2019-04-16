if (window.WebSocket) {
    //---------------------------------
    //  Variables
    //---------------------------------
    var serviceUrl = "ws://127.0.0.1:3337/streamlabs"
    var socket = new WebSocket(serviceUrl);
    //---------------------------------
    //  Events
    //---------------------------------
    socket.onopen = function()
    {
        // Format your Authentication Information
        var auth = {
            author: "KobiQQ",
            website: "https://www.twitch.tv/kobiQQ",
            api_key: API_Key,
            events: [
                "EVENT_CURRENCY_SHOW_BIT_SLOTS",
                "EVENT_CURRENCY_RELOAD",
            ]
        }
        
        //  Send your Data to the server
        socket.send(JSON.stringify(auth));
        console.log("Connected");
    };

    socket.onerror = function(error)
    {
        //  Something went terribly wrong... Respond?!
        console.log("Error: " + error);
    }

    socket.onmessage = function (message) 
    {
        var jsonObject = JSON.parse(message.data);
        //console.log(jsonObject.event);
        //console.log(jsonObject);

        if (jsonObject.event == "EVENT_CURRENCY_SHOW_BIT_SLOTS")
        {
            var arr = JSON.parse(jsonObject.data);


            bitName = arr.bitName;
            bitAmount = arr.bitAmount;
            BanWord1 = arr.banword1;
            BanWord2 = arr.banword2;

            startslot(bitName, bitAmount, BanWord1, BanWord2);
            
		}
        else if(jsonObject.event == "EVENT_CURRENCY_RELOAD")
        {
            //  Pass Data Along
            var jsonData = JSON.parse(jsonObject.data);
            loadSettings(jsonData);
        }

    }

    socket.onclose = function () 
    {
        //  Connection has been closed by you or the server
        console.log("Connection Closed!");
    }   

    
    function loadSettings(jsonData) {
        settings = jsonData;
    }
}