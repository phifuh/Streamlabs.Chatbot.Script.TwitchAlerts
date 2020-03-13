var currentIndex = 0;
var delay = 100;
var audioElementChooser = 1;

var showEventText = function (target, message, userName, index, interval)
{

	if (currentIndex == nextCutoff) {

        currentIndex = 0;
        nextCutoff = userName.length;
        showName("#text_target_userName", userName.substring(0, nextCutoff), 0, delay);

		return;
	}

	$(target).append(message[index++]);
	currentIndex++;
	
	if (message[index] != " ") {
		playSound();		
    }

	setTimeout(function () {
        showEventText(target, message, userName, index, interval);
	}, interval);
};

var showName = function (target, nameText, index, interval) {


    if (currentIndex == nextCutoff) {

        
        return;
    }

    $(target).append(nameText[index++]);
    currentIndex++;

    if (nameText[index] != " ") {
        playSound();
    }

    setTimeout(function () {
        showName(target, nameText, index, interval);
    }, interval);
};

var playSound = function() {
	var targetId = "audio-source" + this.audioElementChooser;
	var audio = document.getElementById(targetId);
	audio.volume = 0.1;
	audio.play();

	if (this.audioElementChooser < 3) {
		this.audioElementChooser++;
	} else {
		this.audioElementChooser = 1;
	}
}


function createZeldaTextBox(text, userName) {

    //reset the input
    document.getElementById("text_target").innerHTML = "";
    document.getElementById("text_target_userName").innerHTML = "";

    currentIndex = 0;
    nextCutoff = text.length;

    var colors = ['#ff0000', '#00ff00', '#0000ff', '#F5BD1F'];
    var random_color = colors[Math.floor(Math.random() * colors.length)];
    document.getElementById('text_target_userName').style.color = random_color;

    showEventText("#text_target", text.substring(0, nextCutoff), userName, 0, delay);

}

