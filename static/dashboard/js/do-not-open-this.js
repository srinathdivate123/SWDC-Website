// // Hi there,
// // If you're reading this, then you're probably a clever developer trying to understand why you aren't able to copy-paste answers from ChatGPT or whatsoever..
// // But note that your efforts, by mutilating the code that is preventing you from pasting, will have no outcome.
// // So, with all due respect, we suggest you to close this window immediately and write your report without copy-pasting!
// // Have a good day! Yay!


const myForm = document.getElementById("myForm");
const submitBtn = document.getElementById("submitBtn");
const errorMessage = document.getElementById("errorMessage");
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
const errorAudio = document.getElementById("errorAudio");


function getRandomArray() {
  let arr = [0, 1, 2, 3, 4, 5];
  for (let i = arr.length - 1; i > 0; i--) {
    let j = Math.floor(Math.random() * (i + 1)); // Random index from 0 to i
    [arr[i], arr[j]] = [arr[j], arr[i]]; // Swap elements
  }
  return arr;
}

let minWordCount = 700; //700
let minWhiteSpaceCount = 70; //minWhiteSpaceCount

let nextBtn = document.getElementById("next-btn");
let submitButton = document.getElementById("submitBtn");
let prevBtn = document.getElementById("prev-btn");
let ques = document.getElementsByClassName("ques");
let ans = document.getElementsByClassName("ans");
let cnt = 0;

let sequence = getRandomArray();
ques[sequence[0]].style.display = "block";


function checkValidAnswer(btn, text, cnt) {
  var c = (ans[sequence[cnt]].value.match(/[a-zA-Z]/g) || []).length;

  if (c >= minWordCount) {
    btn.disabled = false;
    btn.style.backgroundColor = "#C9DF8A";
    btn.innerText = text;
    return true;
  } else {
    btn.disabled = false;
    btn.style.backgroundColor = "grey";
    btn.innerText = "Click here to check if your answer is eligible for submission.";
    return false;
  }
}


prevBtn.addEventListener("click", () => {
  if (cnt == ques.length) {
    submitButton.style.display = "none";
    submitButton.disabled = true;
    nextBtn.style.display = "block";
    cnt = ques.length - 1;
  }

  if (cnt >= 1) {
    cnt--;
    for (let i=0; i<ques.length; i++) {
      ques[i].style.display = "none";
    }
    ques[sequence[cnt]].style.display = "block";
  }

  if (cnt == 0) {
    prevBtn.style.display = "none";
  }
});


nextBtn.addEventListener("click", () => {
  if (cnt == ques.length) {
    res = checkValidAnswer(submitButton, "Submit Your Report", cnt)
  }
  else{
    res = checkValidAnswer(nextBtn, "Next Question", cnt)
  }
  if (countWhitespaces(ans[sequence[cnt]].value) < minWhiteSpaceCount){
    document.getElementById("errorMessage").style.display = "block";
    document.getElementById("errorMessage").innerText = `There are not enough whitespaces in your answer to count it as valid and readable. You will not be able to submit your report without correcting this.`;
    return;
  }
  if (res){
    if (cnt == 0){
        prevBtn.style.display = "block";
    }
    document.getElementById("errorMessage").style.display = "none";
    cnt++;

    if (cnt == ques.length){
        submitButton.disabled = false;
        submitButton.style.display = "block";
        nextBtn.style.display = "none";
        // cnt = 0;
    }
    else{
        for (let i=0; i<ques.length; i++) {
          ques[i].style.display = "none";
        }
        ques[sequence[cnt]].style.display = "block";
    }
  }
  else{
    document.getElementById("errorMessage").style.display = "block";
  }
});

let blurred = false;
function onBlur() {
  blurred = true;
}
window.addEventListener("blur", onBlur);
let tempWin = window.open("", "_blank", "width=1,height=1,top=-1000,left=-1000");
if (tempWin) {
  tempWin.close();
}
setTimeout(() => {
  if (!blurred) {
    errorAudio.play()
    alert("🚨 Oops! We have found some extensions that prevent getting detected when you change tabs. Please uninstall those extensions and come back to report filling..");
    document.getElementById("logoutForm").submit();
  }
  else
  {
    document.getElementById('reportfillingcontent').style.display = 'block';
    document.getElementById('popup_show').style.display = 'none';
  }
  window.removeEventListener("blur", onBlur);
}, 1000);


let blurCnt = 0;

window.addEventListener("blur", () => {
    errorAudio.play()
    blurCnt++;
    if(blurCnt>3){
        document.getElementById("logoutForm").submit();
    }
});


function requestFullScreen() {
  let elem = document.documentElement;

  if (elem.requestFullscreen) {
    elem.requestFullscreen().catch(() => {
        errorAudio.play();
      alert("You have denied full screen request. Logging you out.");
      document.getElementById("logoutForm").submit();
    });
  } else {
      errorAudio.play();
    alert("Fullscreen is not supported on your device. Please fill your report from a device that supports full screen. Logging you out.");
    document.getElementById("logoutForm").submit();
  }
}

function denyFullScreen() {
    errorAudio.play();
  alert("You have denied full screen request. Logging you out.");
  document.getElementById("logoutForm").submit();
}

// Detect when fullscreen mode is active and hide the popup
document.addEventListener("fullscreenchange", function () {
  if (document.fullscreenElement) {
    document.getElementById("fullscreen-popup").style.display = "none"; // Hide popup
  }
});

let fullScreenViolate = 0;
document.addEventListener("fullscreenchange", function () {
  if (!document.fullscreenElement) {
    fullScreenViolate++;
    if (fullScreenViolate >= 3) {
        errorAudio.play()
      alert("You have violated full screen " + fullScreenViolate + " times. We're logging you out.");
      document.getElementById("logoutForm").submit();
    } else {
        errorAudio.play()
      alert("You have violated full screen " + fullScreenViolate + " times. You'll be logged out the third time you do this.");
      document.getElementById("fullscreen-popup").style.display = "block";
    }
  }
});

let lastKeyTime = Date.now();
let typingIntervals = [];

document.addEventListener("keydown", function (event) {
  let currentTime = Date.now();
  let timeDiff = currentTime - lastKeyTime;

  if (typingIntervals.length >= 3) {
    typingIntervals.shift();
  }
  typingIntervals.push(timeDiff);

  let deviation = Math.max(...typingIntervals) - Math.min(...typingIntervals);
  if (deviation < 30) {
    event.preventDefault();
  }

  lastKeyTime = currentTime;
});

document.addEventListener("keydown", function (event) {
  if (event.isTrusted === false) {
    event.preventDefault();
  }
});

// Prevent right click
document.addEventListener("contextmenu", function (event) {
  event.preventDefault();
  // alert("Right click is disabled");
});

// Prevent opening of DevTools on all browsers on Windows & Mac
document.addEventListener("keydown", function (event) {
  if (event.key === "Escape" || event.altKey || event.ctrlKey || event.metaKey || event.key === "Tab") {
    event.preventDefault();
    // alert("The ctrl key is disabled");
  } else if (
    event.key === "F12" ||
    event.keyCode === 123 || // F12
    (event.metaKey && event.altKey && event.key === "I") || // Cmd+Option+I (Mac DevTools)
    (event.metaKey && event.altKey && event.key === "i") || // Cmd+Option+I (Mac DevTools)
    (event.metaKey && event.key === "U") || (
      // Cmd+U (Mac View Source)
      event.metaKey && event.key === "u"
    ) // Cmd+U (Mac View Source)
  ) {
    event.preventDefault();
    // alert("DevTools shortcuts are disabled!");
  }
});

let ids = [];

function update_ids() {
  ids = [];
  var txtareas = document.querySelectorAll("textarea");
  var hiddenInputs = document.querySelectorAll(
    'input[type="hidden"]:not([name="csrfmiddlewaretoken"])'
  );

  for (let i = 0; i < txtareas.length; i++) {
    let randNum = Math.floor(Math.random() * 50000) + 100000;
    ids[i] = "random_" + randNum.toString();
    txtareas[i].id = ids[i];
  }

  for (let i = 0; i < hiddenInputs.length; i++) {
    let randNum = Math.floor(Math.random() * 90000) + 1000;
    ids[i + 6] = "random_" + randNum.toString();
    hiddenInputs[i].id = ids[i + 6];

    // Check values in the actual textarea and the hidden inputs. If they do not match, then someone has put value through the DevTools
    var txtareaVal = document.getElementById(ids[i]).value;
    var hiddenVal = document.getElementById(ids[i + 6]).value;
    if (Math.abs(txtareaVal.length - hiddenVal.length) > 2) {
      // alert("copied");
    }
  }
}


setInterval(update_ids, 5000);


closeBtn1.addEventListener("click", function () {
  copyMsg1.style.display = "none";
});

closeBtn2.addEventListener("click", function () {
  copyMsg2.style.display = "none";
});

// const logged_in_hours = document.getElementById("hours");
// const logged_in_minutes = document.getElementById("minutes");
// const time_left = document.getElementById("time_left");
// function updateTimeLeft() {
//   var currentDate = new Date();
//   var timeLeft = 250 - (currentDate.getHours() * 60 + currentDate.getMinutes() - 330 - logged_in_hours.value * 60 - logged_in_minutes.value);
//   time_left.innerHTML = timeLeft;
//   if (timeLeft<2)
//   {
//     document.getElementById("logoutForm").submit();
//   }
// }

// setInterval(updateTimeLeft, 60000);
// updateTimeLeft();

function onLoadComplete() {
  setTimeout(
    updateCount(
      document.getElementById("wordCount1"),
      document.getElementById(ids[0]),
      "countMessage1",
      "successMessage1"
    ),
    200
  );
  setTimeout(
    updateCount(
      document.getElementById("wordCount2"),
      document.getElementById(ids[1]),
      "countMessage2",
      "successMessage1"
    ),
    200
  );
  setTimeout(
    updateCount(
      document.getElementById("wordCount3"),
      document.getElementById(ids[2]),
      "countMessage3",
      "successMessage1"
    ),
    200
  );
  setTimeout(
    updateCount(
      document.getElementById("wordCount4"),
      document.getElementById(ids[3]),
      "countMessage4",
      "successMessage1"
    ),
    200
  );
  setTimeout(
    updateCount(
      document.getElementById("wordCount5"),
      document.getElementById(ids[4]),
      "countMessage5",
      "successMessage1"
    ),
    200
  );
  setTimeout(
    updateCount(
      document.getElementById("wordCount6"),
      document.getElementById([ids[5]]),
      "countMessage6",
      "successMessage1"
    ),
    200
  );
}
window.onload = setTimeout(onLoadComplete, 1000);

function enableSubmit() {
  var c1 = (document.getElementById(ids[0]).value.match(/[a-zA-Z]/g) || [])
    .length;
  var c2 = (document.getElementById(ids[1]).value.match(/[a-zA-Z]/g) || [])
    .length;
  var c3 = (document.getElementById(ids[2]).value.match(/[a-zA-Z]/g) || [])
    .length;
  var c4 = (document.getElementById(ids[3]).value.match(/[a-zA-Z]/g) || [])
    .length;
  var c5 = (document.getElementById(ids[4]).value.match(/[a-zA-Z]/g) || [])
    .length;
  var c6 = (document.getElementById(ids[5]).value.match(/[a-zA-Z]/g) || [])
    .length;
  if (
    c1 >= minWordCount &&
    c2 >= minWordCount &&
    c3 >= minWordCount &&
    c4 >= minWordCount &&
    c5 >= minWordCount &&
    c6 >= minWordCount
  ) {
    submitBtn.disabled = false;
    submitBtn.style.backgroundColor = "green";
    submitBtn.innerText = "Submit Your Report";
  } else {
    submitBtn.disabled = true;
    submitBtn.style.backgroundColor = "grey";
    submitBtn.innerText = "Click here to check if your answer is eligible for submission.";
  }
}

function countWhitespaces(str) {
  let count = 0;
  for (let i = 0; i < str.length; i++) {
    if (str[i] === " " && str[i + 1] != " " && str[i] != "\n" && str[i + 1] != "\n")
    {
      count++;
    }
  }
  return count;
}
const answersError = document.getElementById("answersError");
function checkAnswers() {
  for (let i = 0; i < 6; i++) {
    var ans = document.getElementById(ids[i]).value.trim();
    var whiteSpaces = countWhitespaces(ans);
    if (whiteSpaces < minWhiteSpaceCount) {
      str =
        "Your answer to question " +
        (i + 1).toString() +
        " is - <br><br> " +
        ans +
        ".<br><br> It has only " +
        whiteSpaces +
        " non-continuous white spaces. <br><br>This is not counted as a valid answer because it seems that you have typed continuous sentences whithout whitespaces to achieve the character count of minWordCount per question. This will make your answer difficult to read.<br><b>There must be atleast minWhiteSpaceCount whitespaces in your answer to count it as valid and readable. You will not be able to submit your report without correcting this.</b>";
      answersError.innerHTML = str;
      return false;
    }
  }
  return true;
}

myForm.addEventListener("submit", function (e) {
  e.preventDefault();
  var c1 = (document.getElementById(ids[0]).value.match(/[a-zA-Z]/g) || [])
    .length;
  var c2 = (document.getElementById(ids[1]).value.match(/[a-zA-Z]/g) || [])
    .length;
  var c3 = (document.getElementById(ids[2]).value.match(/[a-zA-Z]/g) || [])
    .length;
  var c4 = (document.getElementById(ids[3]).value.match(/[a-zA-Z]/g) || [])
    .length;
  var c5 = (document.getElementById(ids[4]).value.match(/[a-zA-Z]/g) || [])
    .length;
  var c6 = (document.getElementById(ids[5]).value.match(/[a-zA-Z]/g) || [])
    .length;
  if (
    c1 >= minWordCount &&
    c2 >= minWordCount &&
    c3 >= minWordCount &&
    c4 >= minWordCount &&
    c5 >= minWordCount &&
    c6 >= minWordCount
  ) {
    if (checkAnswers()) {
      myForm.submit();
    }
  } else {
    errorMessage.style.display = "block";
  }
});

var textareas = document.querySelectorAll("textarea");
let copyAns = [false, false, false, false, false, false];

for (let i = 0; i < textareas.length; i++) {
  textareas[i].addEventListener("paste", function (e) {
    e.preventDefault();
    var val = parseInt(timesCopied.textContent);
    val += 1;
    timesCopied.textContent = val;
    copyMsg1.style.display = "block";
    errorAudio.play();
  });

  textareas[i].addEventListener("input", function () {
    const txtareaID = document.getElementById(ids[i]);
    const hiddenID = document.getElementById(ids[6 + i]);
    var diff = txtareaID.value.length - hiddenID.value.length;

    // if (diff > 8) {
    //     txtareaID.value = hiddenID.value;
    //     copyMsg2.style.display = "block";
    //     errorAudio.play();
    // } else {
      hiddenID.value = txtareaID.value;
    // }
    var wordCount = "wordCount" + (i + 1).toString();
    var countMessage = "countMessage" + (i + 1).toString();
    var successMessage = "successMessage" + (i + 1).toString();
    updateCount(
      document.getElementById(wordCount),
      document.getElementById(txtareaID.id),
      countMessage,
      successMessage
    );
    enableSubmit();

    // if (cnt == 5){
    //   checkValidAnswer(submitButton, "Submit Your Report", cnt);
    // }
    // else{
    //   checkValidAnswer(nextBtn, "Next Question", cnt);
    // }
  });
}

function updateCount(
  wordCountParameter,
  myTextArea,
  countMessageArea,
  successMessageArea
) {
  wordCountParameter.innerText =
    minWordCount - (myTextArea.value.match(/[a-zA-Z]/g) || []).length;
  if (parseInt(wordCountParameter.innerHTML) <= 0) {
    document.getElementById(countMessageArea).style.display = "none";
    document.getElementById(successMessageArea).style.display = "block";
  } else {
    document.getElementById(countMessageArea).style.display = "block";
    document.getElementById(successMessageArea).style.display = "none";
  }
}