

// Hi there,
// If you're reading this, then you're probably a clever developer trying to understand why you aren't able to copy-paste answers from ChatGPT or whatsoever..
// But note that your efforts, by mutilating the code that is preventing you from pasting, will have no outcome.
// So, with all due respect, we suggest you to close this window immediately and write your report without copy-pasting!
// Have a good day!

const myForm = document.getElementById("myForm");
const submitBtn = document.getElementById("submitBtn");
const errorMessage = document.getElementById("errorMessage");
const userName = document.getElementById("userName");
const Objective_of_the_Activity = document.getElementById("Objective_of_the_Activity");
const Description_of_the_Activity = document.getElementById("Description_of_the_Activity");
const Benefits_to_Society = document.getElementById("Benefits_to_Society");
const Benefits_to_Self = document.getElementById("Benefits_to_Self");
const Learning_Experiences_challenges = document.getElementById("Learning_Experiences_challenges");
const How_did_it_help_you_to_shape_your_Empathy = document.getElementById("How_did_it_help_you_to_shape_your_Empathy");
const Objective_of_the_Activity_Hidden = document.getElementById("Objective_of_the_Activity_Hidden");
const Description_of_the_Activity_Hidden = document.getElementById("Description_of_the_Activity_Hidden");
const Benefits_to_Society_Hidden = document.getElementById("Benefits_to_Society_Hidden");
const Benefits_to_Self_Hidden = document.getElementById("Benefits_to_Self_Hidden");
const Learning_Experiences_challenges_Hidden = document.getElementById("Learning_Experiences_challenges_Hidden");
const How_did_it_help_you_to_shape_your_Empathy_Hidden = document.getElementById("How_did_it_help_you_to_shape_your_Empathy_Hidden");
const url = document.getElementById("url");
const urlError = document.getElementById("urlError");
var wordCount1 = document.getElementById("wordCount1");
var wordCount2 = document.getElementById("wordCount2");
var wordCount3 = document.getElementById("wordCount3");
var wordCount4 = document.getElementById("wordCount4");
var wordCount5 = document.getElementById("wordCount5");
var wordCount6 = document.getElementById("wordCount6");
const copyMsg1 = document.getElementById("copyMsg1");
const closeBtn1 = document.getElementById("closeBtn1");
const copyMsg2 = document.getElementById("copyMsg2");
const closeBtn2 = document.getElementById("closeBtn2");
const timesCopied = document.getElementById("timesCopied");
const errorAudio = document.getElementById('errorAudio');
const guardian_faculty = document.getElementById('guardian_faculty');
const guardianFacultyNotChosen = document.getElementById('guardianFacultyNotChosen');

closeBtn1.addEventListener('click', function() {
    copyMsg1.style.display = "none";
});

closeBtn2.addEventListener('click', function() {
    copyMsg2.style.display = "none";
});





var dictionary = {}
dictionary.Objective_of_the_Activity = '1';
dictionary.Description_of_the_Activity = '2';
dictionary.Benefits_to_Society = '3';
dictionary.Benefits_to_Self = '4';
dictionary.Learning_Experiences_challenges = '5';
dictionary.How_did_it_help_you_to_shape_your_Empathy = '6';



const logged_in_hours = document.getElementById('hours');
const logged_in_minutes = document.getElementById('minutes');
const time_left = document.getElementById('time_left');
function updateTimeLeft() {
    var currentDate = new Date();
    var timeLeft = 250 - (currentDate.getHours() * 60 + currentDate.getMinutes() - 330 - logged_in_hours.value * 60 - logged_in_minutes.value);
    time_left.innerHTML = timeLeft;
}

setInterval(updateTimeLeft, 60000);
updateTimeLeft();


function onLoadComplete() {
    setTimeout(updateCount(document.getElementById('wordCount1'), document.getElementById('Objective_of_the_Activity'), 'countMessage1', 'successMessage1'), 200);
    setTimeout(updateCount(document.getElementById('wordCount2'), document.getElementById('Description_of_the_Activity'), 'countMessage2', 'successMessage1'), 200);
    setTimeout(updateCount(document.getElementById('wordCount3'), document.getElementById('Benefits_to_Society'), 'countMessage3', 'successMessage1'), 200);
    setTimeout(updateCount(document.getElementById('wordCount4'), document.getElementById('Benefits_to_Self'), 'countMessage4', 'successMessage1'), 200);
    setTimeout(updateCount(document.getElementById('wordCount5'), document.getElementById('Learning_Experiences_challenges'), 'countMessage5', 'successMessage1'), 200);
    setTimeout(updateCount(document.getElementById('wordCount6'), document.getElementById('How_did_it_help_you_to_shape_your_Empathy'), 'countMessage6', 'successMessage1'), 200);
};
window.onload = setTimeout(onLoadComplete, 1000);


function enableSubmit() {
    var c1 = (Objective_of_the_Activity.value.match(/[a-zA-Z]/g) || []).length;
    var c2 = (Description_of_the_Activity.value.match(/[a-zA-Z]/g) || []).length;
    var c3 = (Benefits_to_Society.value.match(/[a-zA-Z]/g) || []).length;
    var c4 = (Benefits_to_Self.value.match(/[a-zA-Z]/g) || []).length;
    var c5 = (Learning_Experiences_challenges.value.match(/[a-zA-Z]/g) || []).length;
    var c6 = (How_did_it_help_you_to_shape_your_Empathy.value.match(/[a-zA-Z]/g) || []).length;
    if (c1 >= 700 && c2 >= 700 && c3 >= 700 && c4 >= 700 && c5 >= 700 && c6 >= 700) {
        submitBtn.disabled = false;
        submitBtn.style.backgroundColor = 'green';
        submitBtn.innerText = 'Submit Your Report';
    }
    else {
        submitBtn.disabled = true;
        submitBtn.style.backgroundColor = 'grey';
        submitBtn.innerText = 'Write all answers to enable submit button';
    }
};

function checkUrl() {
    var urlVal = url.value;
    urlVal = urlVal.trim();
    if (urlVal === "http://" || urlVal === "https://") {
        urlError.innerHTML = "Your URL should be a valid URL. It has only http:// or https:// ";
        return false;
    }
    if (!(urlVal.includes("https://") || urlVal.includes("http://"))) {
        urlError.innerHTML = "Your URL must contain a http:// or https://";
        return false;

    }
    if (urlVal.includes(" ") || urlVal.includes(",")) {
        urlError.innerHTML = "Your URL cannot have a blank space or a comma.";
        return false;
    }
    return true;
};


function countWhitespaces(str) {
    let count = 0;
    for (let i = 0; i < str.length; i++) {
        if (str[i] === ' ' && str[i+1] != ' ' && str[i] != '\n' && str[i+1]!='\n') {
            count++;
        }
    }
    return count;
}
const answersError = document.getElementById('answersError');
function checkAnswers()
{
    var answers = [Objective_of_the_Activity, Description_of_the_Activity, Benefits_to_Society, Benefits_to_Self, Learning_Experiences_challenges, How_did_it_help_you_to_shape_your_Empathy]

    for (let i = 0; i<answers.length; i++)
    {
        var ans = answers[i].value.trim();
        var whiteSpaces = countWhitespaces(ans);
        if(whiteSpaces < 90)
        {
            str = 'Your answer to question ' + (i+1).toString()  + ' is - <br><br> ' + ans + '.<br><br> It has only ' + whiteSpaces + ' non-continuous white spaces. <br><br>This is not counted as a valid answer because it seems that you have typed continuous sentences whithout whitespaces to achieve the character count of 700 per question. This will make your answer difficult to read.<br><b>There must be atleast 90 whitespaces in your answer to count it as valid and readable. You will not be able to submit your report without correcting this.</b>'
            answersError.innerHTML = str;
            return false;
        }
    }
    return true;
}

myForm.addEventListener('submit', function (e) {
    e.preventDefault();
    var c1 = (Objective_of_the_Activity.value.match(/[a-zA-Z]/g) || []).length;
    var c2 = (Description_of_the_Activity.value.match(/[a-zA-Z]/g) || []).length;
    var c3 = (Benefits_to_Society.value.match(/[a-zA-Z]/g) || []).length;
    var c4 = (Benefits_to_Self.value.match(/[a-zA-Z]/g) || []).length;
    var c5 = (Learning_Experiences_challenges.value.match(/[a-zA-Z]/g) || []).length;
    var c6 = (How_did_it_help_you_to_shape_your_Empathy.value.match(/[a-zA-Z]/g) || []).length;
    if (c1 >= 700 && c2 >= 700 && c3 >= 700 && c4 >= 700 && c5 >= 700 && c6 >= 700) {
        if (checkUrl())
        {
            if(checkAnswers())
            {
                if(guardian_faculty.value === 'Choose')
                {
                    guardianFacultyNotChosen.style.display = 'block';
                }
                else
                {
                    myForm.submit();
                }
            }
        }
    }
    else {
        errorMessage.style.display = 'block';
    }
});


var textareas = document.querySelectorAll('textarea');
textareas.forEach(function (textarea) {
    textarea.addEventListener('paste', function (e) {
        e.preventDefault();
        var val = parseInt(timesCopied.textContent);
        val +=1;
        timesCopied.textContent = val;
        copyMsg1.style.display = 'block';
        errorAudio.play();
    });
});

function updateCount(wordCountParameter, myTextArea, countMessageArea, successMessageArea) {
    wordCountParameter.innerText = 700 - (myTextArea.value.match(/[a-zA-Z]/g) || []).length;
    if (parseInt(wordCountParameter.innerHTML) <= 0) {
        document.getElementById(countMessageArea).style.display = "none";
        document.getElementById(successMessageArea).style.display = "block";
    }
    else {
        document.getElementById(countMessageArea).style.display = "block";
        document.getElementById(successMessageArea).style.display = "none";
    }
};

textareas.forEach(function (textarea) {
    textarea.addEventListener('input', function () {
        var hiddenID = this.id.toString() + '_Hidden'
        const previousVal = document.getElementById(hiddenID);
        var diff = this.value.length - previousVal.value.length;
        if (diff > 2) {
            this.value = previousVal.value
            copyMsg2.style.display = 'block';
            errorAudio.play();
        }
        else {
            previousVal.value = this.value
        }
        var wordCount = 'wordCount' + dictionary[this.id];
        var countMessage = 'countMessage' + dictionary[this.id];
        var successMessage = 'successMessage' + dictionary[this.id];
        updateCount(document.getElementById(wordCount), document.getElementById(this.id), countMessage, successMessage);
        enableSubmit();
    })
});

guardian_faculty.addEventListener('change', function(){
    alert('ALERT:\n\nYou have chosen your Guardian Faculty as ' + guardian_faculty.value + '.\n\nNote that "Guardian Faculty" may not necessarily be your class teacher.\n\nGuardian Faculty is one who is allotted to you by the DESH Department.');
});