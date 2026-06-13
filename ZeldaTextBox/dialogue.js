var currentIndex = 0;
/*var delay = 50;*/
var delay = 100;
var audioElementChooser = 1;

var showEventText = function (target, message, userName, index, interval, mode)
{
    

	if (currentIndex == nextCutoff) {

        currentIndex = 0;
        nextCutoff = userName.length;
        displayText("#text_target_userName", userName.substring(0, nextCutoff), 0, delay, mode);

		return;
	}

	$(target).append(message[index++]);
	currentIndex++;
	
	if (message[index] != " ") {
        playSound(mode);
    }

	setTimeout(function () {
        showEventText(target, message, userName, index, interval, mode);
	}, interval);
};

var displayText = function (target, nameText, index, interval, mode) {


    if (currentIndex == nextCutoff) {

        return;
    }

    $(target).append(nameText[index++]);
    currentIndex++;



    /*plays a sound everytime a space is*/
    if (nameText[index] != " ") {
        playSound(mode);
    }

    setTimeout(function () {
        displayText(target, nameText, index, interval, mode);
    }, interval);
};

var playSound = function (mode) {


    


    if (mode == 1) {

        var targetId = "audio-source-kroko-" + this.audioElementChooser;
        var audio = document.getElementById(targetId);
        audio.volume = 0.1;

        var randomPlayback = (randomInteger(60, 130) / 100);

        audio.playbackRate = randomPlayback;

        //Attempt in radomizing the sounds
        x = randomInteger(0, 10)
        if (x > 3) {
            audio.play();
        }
    }

    if (mode == 2) {

        var targetId = "audio-source-banjo-" + this.audioElementChooser;
        var audio = document.getElementById(targetId);
        audio.volume = 0.1;

        var randomPlayback = (randomInteger(90, 130) / 100);

        audio.playbackRate = randomPlayback;

        //Attempt in radomizing the sounds
        x = randomInteger(0, 10)
        if (x > 2) {
            audio.play();
        }
    }


    else {

        var targetId = "audio-source-normal-" + this.audioElementChooser;
        var audio = document.getElementById(targetId);
        audio.volume = 0.1;

        //this working perfectly fine for the classic sound
        audio.play();
    }


	if (this.audioElementChooser < 3) {
		this.audioElementChooser++;
	} else {
		this.audioElementChooser = 1;
	}
}

function randomInteger(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function createZeldaTextBox(text, userName) {

    //update the height of dialogue-box - to match how many lines we will have

    //reset the input
    document.getElementById("text_target").innerHTML = "";
    document.getElementById("text_target_userName").innerHTML = "";

    currentIndex = 0;
    nextCutoff = text.length;

    //Red, Green, LightBlue, Yellow
    var colors = ['#ff0000', '#00ff00', '#0080ff', '#F5BD1F'];
    var random_color = colors[Math.floor(Math.random() * colors.length)];
    document.getElementById('text_target_userName').style.color = random_color;


    mode = randomInteger(1, 3)
    showEventText("#text_target", text.substring(0, nextCutoff), userName, 0, delay, mode);

}

