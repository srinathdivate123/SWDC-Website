const instructionsContainer = document.getElementById("instructionsContainer");
const proceedBtn = document.getElementById("proceedBtn");
const proceedMessage = document.getElementById("proceedMessage");
var currentIndex = 0;
var proceedStatus = [
  "Establishing secure connection with our servers...",
  "Initialising Plagarism Detection Software...",
  "Encrpyting your data...",
  "Allocating back-end resource...",
  "Almost done...",
  "Proceeding to Report Filling page...",
];

function uncheckAllCheckboxes() {
  const ckboxes = document.querySelectorAll('input[type="checkbox"]');
  ckboxes.forEach(function (checkbox) {
    checkbox.checked = false;
  });
  proceedBtn.disabled = true;
}

function iterateWithDelay(intervalID) {
  if (currentIndex < proceedStatus.length) {
    proceedMessage.innerHTML = proceedStatus[currentIndex];
    currentIndex++;
  } else {
    clearInterval(intervalID);
    uncheckAllCheckboxes();
    window.location.href = "/v/report-filling";
  }
}

const url = document.getElementById("url");

function checkUrl() {
  var urlVal = url.value;
  urlVal = urlVal.trim();
  if (urlVal === "http://" || urlVal === "https://") {
    alert("Your URL should be a valid URL. It has only http:// or https:// ");
    return false;
  }
  if (!(urlVal.includes("https://") || urlVal.includes("http://"))) {
    alert("Your URL must contain a http:// or https://");
    return false;
  }
  if (urlVal.includes(" ") || urlVal.includes(",")) {
    alert("Your URL cannot have a blank space or a comma.");
    return false;
  }
  return true;
}

const guardian_faculty = document.getElementById("guardian_faculty");

guardian_faculty.addEventListener("change", function () {
  alert(
    "ALERT:\n\nYou have chosen your Guardian Faculty as " +
      guardian_faculty.value +
      '.\n\nNote that "Guardian Faculty" may not necessarily be your class teacher.\n\nGuardian Faculty is one who is allotted to you by the DESH Department.'
  );
});

const proceedForm = document.getElementById('proceedForm');
proceedBtn.addEventListener("click", function () {
  if (guardian_faculty.value === "Choose") {
    alert('Please choose your guardian faculty')
    return
  }

  if(!checkUrl())
  {
    return;
  }
  proceedForm.submit();



  proceedBtn.style.display = "none";
  proceedMessage.style.display = "block";
  document.getElementById("loader").style.display = "block";
  var intervalID = setInterval(iterateWithDelay, 3500);
  iterateWithDelay(intervalID);
});

function checkCheckboxes() {
  const ckboxes = document.querySelectorAll('input[type="checkbox"]');
  var state = true;
  ckboxes.forEach(function (checkbox) {
    if (!checkbox.checked) {
      state = false;
    }
  });
  return state;
}
const checkboxes = document.querySelectorAll('input[type="checkbox"]');

checkboxes.forEach(function (checkbox) {
  checkbox.addEventListener("change", function () {
    var state = checkCheckboxes();
    if (state) {
      proceedBtn.disabled = false;
    } else {
      proceedBtn.disabled = true;
    }
  });
});
