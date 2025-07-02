
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const imageDataInput = document.getElementById("image_data");
const punchTypeInput = document.getElementById("punch_type");
const dt = document.getElementById("datetime");
const statusText = document.getElementById("spoof-status");
const btnIn = document.getElementById("btn-in");
const btnOut = document.getElementById("btn-out");
const boxCanvas = document.createElement("canvas");
boxCanvas.style.position = "absolute";
boxCanvas.style.top = video.offsetTop + "px";
boxCanvas.style.left = video.offsetLeft + "px";
boxCanvas.width = video.offsetWidth;
boxCanvas.height = video.offsetHeight;
video.parentNode.appendChild(boxCanvas);
const boxContext = boxCanvas.getContext("2d");

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        alert("Failed to access camera: " + err);
        if (statusText) statusText.innerText = "❌ Camera not available";
        console.error("❌ Camera not accessible:", err);
    });

function capture(punchType) {
    document.querySelectorAll('.punch-button').forEach(btn => btn.disabled = true);
    document.getElementById('loaderRing').style.display = 'block';

    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL('image/jpeg');
    imageDataInput.value = imageData;
    punchTypeInput.value = punchType;

    document.getElementById('captureForm').submit();
}

function updateDateTime() {
    const now = new Date();
    dt.innerText = now.toLocaleString();
}

setInterval(updateDateTime, 500);
updateDateTime();

async function checkSpoof(imageData) {
    const form = new FormData();
    form.append("image_data", imageData);

    try {
        const res = await fetch("/detect_spoof", {
            method: "POST",
            body: form,
        });
        const data = await res.json();

        boxContext.clearRect(0, 0, boxCanvas.width, boxCanvas.height);

        if (data.bbox && data.bbox.length === 4) {
            const [x, y, w, h] = data.bbox;
            boxContext.strokeStyle = data.status === "real" ? "green" : "red";
            boxContext.lineWidth = 3;
            boxContext.strokeRect(x, y, w, h);
        }

        if (data.status === "real") {
            statusText.innerText = "✅ Real Face Detected";
            btnIn.disabled = false;
            btnOut.disabled = false;
        } else if (data.status === "fake") {
            statusText.innerText = "❌ Please show real face.";
            btnIn.disabled = true;
            btnOut.disabled = true;
        } else {
            statusText.innerText = "⚠️ Detection Error";
            btnIn.disabled = true;
            btnOut.disabled = true;
        }
    } catch (err) {
        console.error("Spoof check error:", err);
        statusText.innerText = "❌ Server Error";
        btnIn.disabled = true;
        btnOut.disabled = true;
    }
}

function captureSnapshotForSpoofCheck() {
    const context = canvas.getContext("2d");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL("image/jpeg");
    checkSpoof(imageData);
}

setInterval(captureSnapshotForSpoofCheck, 2000);
