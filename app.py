import streamlit as st
import streamlit.components.v1 as components

# Define the HTML and JavaScript code for recording audio
html_code = """
<!DOCTYPE html>
<html>
<head>
    <title>Audio Recorder</title>
</head>
<body>
    <h1>Record Audio</h1>
    <button id="start">Start Recording</button>
    <button id="stop" disabled>Stop Recording</button>
    <audio id="audioPlayback" controls></audio>

    <script>
        const startButton = document.getElementById('start');
        const stopButton = document.getElementById('stop');
        const audioPlayback = document.getElementById('audioPlayback');

        let mediaRecorder;
        let audioChunks = [];
        let silenceStart = null;
        let audioContext;
        let analyser;
        let source;
        let stream;

        startButton.addEventListener('click', async () => {
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            source = audioContext.createMediaStreamSource(stream);
            analyser = audioContext.createAnalyser();
            source.connect(analyser);
            analyser.fftSize = 2048;
            const bufferLength = analyser.fftSize;
            const dataArray = new Uint8Array(bufferLength);

            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                audioChunks = [];
                const audioUrl = URL.createObjectURL(audioBlob);
                audioPlayback.src = audioUrl;

                // Convert Blob to Base64
                const reader = new FileReader();
                reader.readAsDataURL(audioBlob);
                reader.onloadend = function() {
                    const base64AudioMessage = reader.result.split(',')[1];

                    // Send Base64 audio to Flask backend
                    fetch('http://localhost:5000/upload-audio', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ audio: base64AudioMessage }),
                    }).then(response => response.json())
                      .then(data => {
                          if (data.status === 'success') {
                              fetch('http://localhost:5000/process-audio', {
                                  method: 'POST',
                                  headers: {
                                      'Content-Type': 'application/json',
                                  },
                                  body: JSON.stringify({ path: data.path }),
                              }).then(response => response.json())
                                .then(data => {
                                    if (data.status === 'success') {
                                        const responseAudioUrl = `http://localhost:5000/${data.audio}`;
                                        const responseText = data.response;
                                        const responseAudio = new Audio(responseAudioUrl);
                                        document.getElementById('response').innerText = `Lucy: ${responseText}`;
                                        responseAudio.play();
                                    }
                                });
                          }
                      })
                      .catch(error => console.error('Error:', error));
                }
                
                // Reset variables
                silenceStart = null;
                stream.getTracks().forEach(track => track.stop());
                audioContext.close();
                startButton.disabled = false;
                stopButton.disabled = true;
            };

            const detectSilence = () => {
                analyser.getByteTimeDomainData(dataArray);
                let silence = true;
                for (let i = 0; i < bufferLength; i++) {
                    if (dataArray[i] > 128 + 5 || dataArray[i] < 128 - 5) {
                        silence = false;
                        break;
                    }
                }
                if (silence) {
                    if (silenceStart === null) {
                        silenceStart = Date.now();
                    } else {
                        if (Date.now() - silenceStart > 2000) {
                            mediaRecorder.stop();
                        }
                    }
                } else {
                    silenceStart = null;
                }
                if (mediaRecorder.state === "recording") {
                    requestAnimationFrame(detectSilence);
                }
            };

            startButton.disabled = true;
            stopButton.disabled = false;
            detectSilence();
        });

        stopButton.addEventListener('click', () => {
            mediaRecorder.stop();
        });
    </script>
    <p id="response"></p>
</body>
</html>
"""

# Embed the HTML and JavaScript in Streamlit
components.html(html_code, height=600)
