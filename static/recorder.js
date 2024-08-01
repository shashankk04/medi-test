document.addEventListener('DOMContentLoaded', (event) => {
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let isProcessing = false;

    document.getElementById('start').addEventListener('click', startRecording);
    document.getElementById('stop').addEventListener('click', stopRecording);

    const audioPlayback = document.getElementById('audioPlayback');
    audioPlayback.addEventListener('ended', startRecording); // Automatically start recording after audio ends

    async function startRecording() {
        if (isRecording) return;

        isRecording = true;
        audioChunks = [];
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            console.log('Recording stopped');
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const audioBase64 = await convertBlobToBase64(audioBlob);
            await sendAudio(audioBase64);
            isRecording = false;
            // Automatically start recording again after processing
            if (!isProcessing) {
                startRecording();
            }
        };

        mediaRecorder.start();
        console.log('Recording started');
        updateUI('Recording...');
    }

    async function stopRecording() {
        if (!isRecording) return;

        console.log('Stop button clicked');
        mediaRecorder.stop();
        updateUI('Processing...');
        isProcessing = true;
        // Wait for the audio processing to complete
        await processAudio();
        isProcessing = false;
    }

    async function convertBlobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result.split(',')[1]);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }

    async function sendAudio(audioBase64) {
        try {
            const response = await fetch('/upload-audio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ audio: audioBase64 })
            });
            const data = await response.json();
            if (data.status === 'success') {
                console.log('Audio uploaded successfully');
                // Optionally, handle the response if needed
            } else {
                console.error('Error uploading audio:', data.message);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    async function processAudio() {
        try {
            const response = await fetch('/process-audio', { method: 'POST' });
            const data = await response.json();
            if (data.status === 'success') {
                document.getElementById('conversation').innerText = `Bot: ${data.response}`;
                document.getElementById('audioPlayback').src = data.audio;
                document.getElementById('audioPlayback').play();
                console.log('Bot response:', data.response);
            } else {
                console.error('Error processing audio:', data.message);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    function updateUI(message) {
        const conversationElement = document.getElementById('conversation');
        if (conversationElement) {
            conversationElement.innerText = message;
        } else {
            console.error('Conversation element not found');
        }
    }
});
