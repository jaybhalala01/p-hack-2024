var isPlaying = false; // Track whether the video is currently playing
var isDetecting = false; // Track whether the video is currently detecting


function readJSON() {
    try {
        // Fetch the JSON file from the server
        var data = JSON.parse(data);
        console.log(data);

        // Update the HTML with the JSON data
        document.querySelector('.dynamic-values').innerHTML = `
            <div class="text-white text-body">
                <h3 class="text-white">Total Vehicles</h3>
                <p>${data.total_vehicle}</p>
            </div>
            <div class="text-white text-body">
                <h3 class="text-white">Total Number Plates</h3>
                <p>${data.total_license}</p>
            </div>
            <div class="text-white text-body">
                <h3 class="text-white">Current Vehicles</h3>
                <p>${data.current_vehicle}</p>
            </div>
            <div class="text-white text-body">
                <h3 class="text-white">Current Number Plates</h3>
                <p>${data.current_license}</p>
            </div>
        `;
    } catch (error) {
        console.error('Error fetching the JSON file:', error);
    }
}

// Function to update dynamic values
async function updateDynamicValues() {
    try {
        const response = await fetch('/track_data');
        const data = await response.json();

        document.querySelector('.dynamic-values').innerHTML = `
            <div class="text-white text-body">
                <h3 class="text-white">Total Vehicles</h3>
                <p>${data.total_vehicle}</p>
            </div>
            <div class="text-white text-body">
                <h3 class="text-white">Total Number Plates</h3>
                <p>${data.total_license}</p>
            </div>
            <div class="text-white text-body">
                <h3 class="text-white">Current Vehicles</h3>
                <p>${data.current_vehicle}</p>
            </div>
            <div class="text-white text-body">
                <h3 class="text-white">Current Number Plates</h3>
                <p>${data.current_license}</p>
            </div>
        `;
    } catch (error) {
        console.error('Error fetching track data:', error);
    }
}



function updateLabel() {
    var input = document.getElementById('file');
    var fileName = document.getElementById('file-name');
    if (input.files && input.files.length > 0) {
        fileName.textContent = input.files[0].name;
    } else {
        fileName.textContent = 'No file chosen';
    }
}

function uploadFile(file, callback) {
    var formData = new FormData();
    formData.append('file', file);

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload_video', true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var response = JSON.parse(xhr.responseText);
            if (response.filename) {
                callback(response.filename);
            } else {
                alert('Error uploading file.');
            }
        }
    };
    xhr.send(formData);
}

function detectVideo() {
    var fileInput = document.getElementById('file');
    var file = fileInput.files[0];
    
    if (file) {
        uploadFile(file, function(filename) {
            var videoStream = document.getElementById('videoStream');
            var videoUpContainer = document.querySelector('.video-up-container');
            videoUpContainer.style.display = 'none'; // Hide the upload container
            videoStream.src = `/detect_video/${filename}`;
            videoStream.style.display = 'block'; // Show the video stream image
            isPlaying = true; // Set play state to true
            document.getElementById('play-pause-btn').textContent = 'Pause'; // Update button text
            let detect_button = document.getElementById('detect-btn') // Disable the detect button
            detect_button.disabled = true;
            detect_button.style.backgroundColor = 'grey';
        });
        isDetecting = true;
        playPauseVideo();
    } else {
        alert('Please upload a video file first.');
    }
}

function playPauseVideo() {
    //check if the video is uploaded
    var fileInput = document.getElementById('file');
    var file = fileInput.files[0];
    if (!file) {
        alert('Please upload a video file first.');
        return;
    }

    if (!isDetecting) {
        alert('Please detect the video first.');
        return;
    }
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/play_pause', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var response = JSON.parse(xhr.responseText);
            isPlaying = response.playing;
            ppb = document.getElementById('play-pause-btn');
            ppb.textContent = isPlaying ? 'Pause' : 'Play';
            ppb.style.backgroundColor = isPlaying ? 'red' : 'green';
        }
    };
    xhr.send();
}

function cancelStream() {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/cancel_stream', true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            // Reset the file input and other UI elements
            document.getElementById('file').value = '';
            document.getElementById('file-name').textContent = 'No file chosen';
            var videoStream = document.getElementById('videoStream');
            videoStream.src = '';
            videoStream.style.display = 'none';
            var videoUpContainer = document.querySelector('.video-up-container');
            videoUpContainer.style.display = 'flex';
            var detectButton = document.getElementById('detect-btn');
            detectButton.disabled = false;
            detectButton.style.backgroundColor = '';
            document.getElementById('play-pause-btn').textContent = 'Play';
            document.getElementById('play-pause-btn').style.backgroundColor = 'green';
            isPlaying = false;
            isDetecting = false;
            console.log('streaming')
        }
    };
    xhr.send();
}

if (isPlaying) {
    // Call updateDynamicValues every second (1000 milliseconds)
    setInterval(readJSON, 1000);
}




// Attach event listeners to buttons
document.getElementById('detect-btn').addEventListener('click', detectVideo);
document.getElementById('play-pause-btn').addEventListener('click', playPauseVideo);
document.getElementById('cancel-btn').addEventListener('click', cancelStream);
