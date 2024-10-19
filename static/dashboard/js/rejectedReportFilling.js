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
var countMessage1 = document.getElementById("countMessage1");
var countMessage2 = document.getElementById("countMessage2");
var countMessage3 = document.getElementById("countMessage3");
var countMessage4 = document.getElementById("countMessage4");
var countMessage5 = document.getElementById("countMessage5");
var countMessage6 = document.getElementById("countMessage6");
const guardian_faculty = document.getElementById('guardian_faculty');
const guardianFacultyNotChosen = document.getElementById('guardianFacultyNotChosen');

var dictionary = {}
dictionary.Objective_of_the_Activity = '1';
dictionary.Description_of_the_Activity = '2';
dictionary.Benefits_to_Society = '3';
dictionary.Benefits_to_Self = '4';
dictionary.Learning_Experiences_challenges = '5';
dictionary.How_did_it_help_you_to_shape_your_Empathy = '6';


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


submitBtn.addEventListener('click', function () {
    var c1 = (Objective_of_the_Activity.value.match(/[a-zA-Z]/g) || []).length;
    var c2 = (Description_of_the_Activity.value.match(/[a-zA-Z]/g) || []).length;
    var c3 = (Benefits_to_Society.value.match(/[a-zA-Z]/g) || []).length;
    var c4 = (Benefits_to_Self.value.match(/[a-zA-Z]/g) || []).length;
    var c5 = (Learning_Experiences_challenges.value.match(/[a-zA-Z]/g) || []).length;
    var c6 = (How_did_it_help_you_to_shape_your_Empathy.value.match(/[a-zA-Z]/g) || []).length;

    if(c1<=700)
        countMessage1.innerHTML = (700-c1).toString() + ' more characters needed.';
    else
        countMessage1.innerHTML = '';

    if(c2<=700)
        countMessage2.innerHTML = (700-c2).toString() + ' more characters needed.';
    else
        countMessage2.innerHTML = '';

    if(c3<=700)
        countMessage3.innerHTML = (700-c3).toString() + ' more characters needed.';
    else
        countMessage3.innerHTML = '';

    if(c4<=700)
        countMessage4.innerHTML = (700-c4).toString() + ' more characters needed.';
    else
        countMessage4.innerHTML = '';

    if(c5<=700)
        countMessage5.innerHTML = (700-c5).toString() + ' more characters needed.';
    else
        countMessage5.innerHTML = '';

    if(c6<=700)
        countMessage6.innerHTML = (700-c6).toString() + ' more characters needed.';
    else
        countMessage6.innerHTML = '';




    if (c1 >= 700 && c2 >= 700 && c3 >= 700 && c4 >= 700 && c5 >= 700 && c6 >= 700) {
        if (checkUrl())
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
    else
    {
        errorMessage.style.display = 'block';
    }
});


var textareas = document.querySelectorAll('textarea');
textareas.forEach(function (textarea) {
    textarea.addEventListener('paste', function (e) {
        e.preventDefault();
        alert('Please type the answers in your own words instead of copy-pasting.');
    });
});


textareas.forEach(function (textarea) {
    textarea.addEventListener('input', function () {
        var hiddenID = this.id.toString() + '_Hidden'
        const previousVal = document.getElementById(hiddenID);
        var diff = this.value.length - previousVal.value.length;
        if (diff > 15) {
            this.value = previousVal.value
            alert('You can enter at max 15 characters at once.');
        }
        else
            previousVal.value = this.value
    })
});




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


guardian_faculty.addEventListener('change', function(){
    alert('ALERT:\n\nYou have chosen your Guardian Faculty as ' + guardian_faculty.value + '.\n\nNote that "Guardian Faculty" may not necessarily be your class teacher.\n\nGuardian Faculty is one who is allotted to you by the DESH Department.');
});