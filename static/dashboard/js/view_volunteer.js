let failForm = document.getElementById("failForm");
let rejForm = document.getElementById("rejForm");
let approveConfirmContainer = document.getElementById("approveConfirmContainer");
let blo = document.getElementById("blocker");
let approveText = document.getElementById("approveText");
let chk1 = document.getElementById("chk1");
let chk2 = document.getElementById("chk2");
let approveConfirmBtn = document.getElementById("approveConfirmBtn");

var msg = ["Approving the Volunteer...", "Generating the Certificate...", "Generating the Report...", "Sending an E-Mail...", "Almost done..."];
var currentIndex = 0;

function iterateWithDelay(intervalID) {
    if (currentIndex < msg.length) {
        approveText.innerHTML = '&nbsp; &nbsp;' + msg[currentIndex];
        currentIndex++;
    }
    else {
        clearInterval(intervalID);
        document.getElementById('ApproveForm').submit();
    }
};

function checkboxes(){
    if(chk1.checked && chk2.checked)
        approveConfirmBtn.disabled = false;
    else
        approveConfirmBtn.disabled = true;
};

chk1.addEventListener('change', checkboxes);
chk2.addEventListener('change', checkboxes);

approveConfirmBtn.addEventListener('click', function (event) {
    if (!document.getElementById('attendance').checked) {
        let confirmAttendance  = confirm("At least 50% attendance checkbox is unchecked. The volunteer won’t receive a certificate even if you approve the report.\nIf their attendance is above 50%, please tick the checkbox.");
        if (!confirmAttendance) {
            event.preventDefault();
            return;
        }
    }

    reportMarks = document.querySelector('#reportMarks');
    dataCollectionMarks = document.querySelector('#dataCollection');

    reportMarks = parseInt(reportMarks.value, 10);
    dataCollectionMarks = parseInt(dataCollectionMarks.value, 10);

    if ((reportMarks >= 0 && reportMarks <= 15) && (dataCollectionMarks >= 0 && dataCollectionMarks <= 10)) {
        document.querySelector('.options-container').style.display = 'none';
        document.getElementById('loader').style.display = 'inline-block';
        approveText.style.display = 'inline-block';
        approveConfirmContainer.style.display = "none";
        blo.style.display = "none";
        // var intervalID = setInterval(iterateWithDelay, 2100);
        // iterateWithDelay(intervalID);
    }
});

document.getElementById('confirmrejectionForm').addEventListener('submit', function (event) {
    event.preventDefault();
    document.getElementById('confirmrejectionBtn').style.display = 'none';
    document.getElementById('rejectText').style.display = 'inline-block';
    document.getElementById('confirmrejectionForm').submit();
});


document.getElementById('confirmfailForm').addEventListener('submit', function (event) {
    event.preventDefault();
    document.getElementById('confirmfailBtn').style.display = 'none';
    document.getElementById('failText').style.display = 'inline-block';
    document.getElementById('confirmfailForm').submit();
});

document.getElementById('approveBtn').addEventListener('click', function() {
    console.log("Approve");
    approveConfirmContainer.style.display = "block";
    blo.style.display = "block";
});

document.getElementById('rejectBtn').addEventListener('click', function() {
    rejForm.style.display = "block";
    blo.style.display = "block";
});

document.getElementById('failBtn').addEventListener('click', function() {
    failForm.style.display = "block";
    blo.style.display = "block";
});

document.getElementById('blocker').addEventListener('click', function() {
    rejForm.style.display = "none";
    failForm.style.display = "none";
    approveConfirmContainer.style.display = "none";
    blo.style.display = "none";
});