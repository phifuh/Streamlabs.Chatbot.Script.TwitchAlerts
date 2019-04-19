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
                "EVENT_SHOW_DONATION",
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

            //console.log(arr.banword1);
            //console.log(arr.banword2);

            startslot(arr.bitName, arr.bitAmount, arr.BanWord1, arr.BanWord2);
            
        }

        else if (jsonObject.event == "EVENT_SHOW_DONATION") {
            var arr = JSON.parse(jsonObject.data);


            //donationName = arr.donationName;
            //donationAmount = arr.donationAmount;

            showDonation(arr.donationName, arr.donationAmount);
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