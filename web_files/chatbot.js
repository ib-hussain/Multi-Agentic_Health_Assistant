document.addEventListener("DOMContentLoaded", function() {
    // DOM Elements
    const messageForm = document.getElementById('message-form');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const recordBtn = document.getElementById('record-btn');
    const chatMessages = document.getElementById('chat-messages');
    // State
    let isTyping = false;
    let mediaRecorder;
    let isRecording = false;
    let recordingTimer;
    let audioChunks = [];
    let currentStream;
    // Events
    recordBtn.addEventListener('click', toggleRecording);
    window.addEventListener('beforeunload', handlePageUnload);
    messageForm.addEventListener('submit', handleMessageSubmit);
    // Start/stop recording
    async function toggleRecording() {
        if (isRecording) {
            stopRecording();
            return;
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: { echoCancellation: true, noiseSuppression: true }
            });
            currentStream = stream;

            const mime = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
                ? 'audio/webm;codecs=opus'
                : (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus') ? 'audio/ogg;codecs=opus' : '');

            audioChunks = [];
            mediaRecorder = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined);

            mediaRecorder.ondataavailable = (e) => { if (e.data && e.data.size > 0) audioChunks.push(e.data); };
            mediaRecorder.onstop = handleRecordingStop;
            mediaRecorder.onerror = (e) => {
                console.error("Recording error:", e.error || e);
                addMessage("Recording error occurred. Please try again.", 'bot-message');
                cleanupAudio();
            };

            mediaRecorder.start(100); // collect chunks every 100ms
            isRecording = true;
            recordBtn.classList.add('recording');
            userInput.placeholder = "Recording... Click the mic again to stop";

            // Auto-stop after 2 minutes
            recordingTimer = setTimeout(() => {
                if (isRecording) {
                    stopRecording();
                    addMessage("Maximum recording time reached (2 minutes).", 'bot-message');
                }
            }, 120000);

        } catch (err) {
            console.error("Microphone error:", err);
            addMessage("Microphone access denied. Please check permissions.", 'bot-message');
            cleanupAudio();
        }
    }
    function stopRecording() {
        if (mediaRecorder && isRecording) {
            clearTimeout(recordingTimer);
            mediaRecorder.stop(); // will trigger handleRecordingStop
            isRecording = false;
            recordBtn.classList.remove('recording');
            userInput.placeholder = "Type your message...";
        }
    }
    async function handleRecordingStop() {
        try {
            if (!audioChunks.length) throw new Error("No audio data recorded");

            showSpinner();
            const recordedBlob = new Blob(audioChunks, { type: (mediaRecorder && mediaRecorder.mimeType) || 'audio/webm' });

            // Convert to 16kHz mono WAV for backend STT engines (Vosk/Whisper etc.)
            const wavBlob = await convertToWav16kMono(recordedBlob);

            const transcription = await transcribeAudio(wavBlob);

            // === CHANGE: only show it in the input, do NOT send/add as a chat message ===
            userInput.value = transcription || "";
            userInput.focus();
            try {
                const len = userInput.value.length;
                userInput.setSelectionRange(len, len);
            } catch (_) {}

        } catch (error) {
            console.error("Processing error:", error);
            addMessage(`Error: ${error.message}`, 'bot-message');
        } finally {
            hideSpinner();
            cleanupAudio();
        }
    }
    // Convert compressed MediaRecorder blob -> decoded PCM -> resample to 16kHz mono -> encode WAV
    async function convertToWav16kMono(inputBlob) {
        const arrayBuffer = await inputBlob.arrayBuffer();

        const ac = new (window.AudioContext || window.webkitAudioContext)();
        const decodedBuffer = await ac.decodeAudioData(arrayBuffer);

        // Downmix to mono
        const length = decodedBuffer.length;
        const channels = decodedBuffer.numberOfChannels;
        const mixed = new Float32Array(length);
        for (let ch = 0; ch < channels; ch++) {
            const data = decodedBuffer.getChannelData(ch);
            for (let i = 0; i < length; i++) mixed[i] += data[i];
        }
        for (let i = 0; i < length; i++) mixed[i] = mixed[i] / channels;

        // Resample to 16kHz using OfflineAudioContext
        const targetSampleRate = 16000;
        const offline = new OfflineAudioContext(1, Math.ceil(decodedBuffer.duration * targetSampleRate), targetSampleRate);
        const bufferMono = offline.createBuffer(1, length, decodedBuffer.sampleRate);
        bufferMono.copyToChannel(mixed, 0, 0);

        const src = offline.createBufferSource();
        src.buffer = bufferMono;
        src.connect(offline.destination);
        src.start(0);

        const rendered = await offline.startRendering();
        const samples = rendered.getChannelData(0);

        const wavBuffer = encodeWavFromFloat32(samples, targetSampleRate);
        await ac.close().catch(() => {});
        return new Blob([wavBuffer], { type: 'audio/wav' });
    }
    function encodeWavFromFloat32(samples, sampleRate) {
        const bytesPerSample = 2; // 16-bit PCM
        const blockAlign = 1 * bytesPerSample;
        const buffer = new ArrayBuffer(44 + samples.length * bytesPerSample);
        const view = new DataView(buffer);

        // RIFF header
        writeString(view, 0, 'RIFF');
        view.setUint32(4, 36 + samples.length * bytesPerSample, true);
        writeString(view, 8, 'WAVE');

        // fmt chunk
        writeString(view, 12, 'fmt ');
        view.setUint32(16, 16, true);   // size of fmt chunk
        view.setUint16(20, 1, true);    // PCM format
        view.setUint16(22, 1, true);    // mono
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, sampleRate * blockAlign, true);
        view.setUint16(32, blockAlign, true);
        view.setUint16(34, 8 * bytesPerSample, true); // bits per sample

        // data chunk
        writeString(view, 36, 'data');
        view.setUint32(40, samples.length * bytesPerSample, true);

        // PCM samples
        floatTo16BitPCM(view, 44, samples);
        return buffer;
    }
    function floatTo16BitPCM(view, offset, input) {
        for (let i = 0; i < input.length; i++, offset += 2) {
            let s = Math.max(-1, Math.min(1, input[i]));
            view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
        }
    }
    function writeString(view, offset, string) {
        for (let i = 0; i < string.length; i++) view.setUint8(offset + i, string.charCodeAt(i));
    }
    async function transcribeAudio(audioBlob) {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');

        const response = await fetch('/api/transcribe', { method: 'POST', body: formData });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.error || 'Transcription failed');
        }
        const result = await response.json();
        return result.transcription || "No transcription returned";
    }
    function handlePageUnload() {
        if (isRecording) stopRecording();
    }
    function cleanupAudio() {
        audioChunks = [];
        if (currentStream) {
            currentStream.getTracks().forEach(track => track.stop());
            currentStream = null;
        }
    }
    function showSpinner() {
        recordBtn.disabled = true;
        recordBtn.innerHTML = '<div class="spinner"></div>';
    }
    function hideSpinner() {
        recordBtn.disabled = false;
        recordBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
                <path fill="currentColor" d="M12 2a3 3 0 0 1 3 3v6a3 3 0 0 1-6 0V5a3 3 0 0 1 3-3zm7 9a1 1 0 0 1 1 1 7 7 0 0 1-14 0 1 1 0 0 1 1-1 1 1 0 0 1 1 1 5 5 0 0 0 10 0 1 1 0 0 1 1-1z"/>
            </svg>`;
    }
    // Simple bot plumbing (unchanged)
    function handleMessageSubmit(e) {
        e.preventDefault();
        const message = userInput.value.trim();
        if (message && !isTyping) {
            setInputState(false);
            isTyping = true;

            addMessage(message, 'user-message');
            userInput.value = '';
            const typingIndicator = addTypingIndicator();

            setTimeout(() => {
                typingIndicator.remove();
                addMessage(getBotResponse(message), 'bot-message');
                setInputState(true);
                isTyping = false;
            }, 1200);
        }
    }
    function getBotResponse(message) {
        const lowerMsg = message.toLowerCase();
        if (lowerMsg.includes('hello') || lowerMsg.includes('hi')) {
            return "Hello! How can I help you today?";
        } else if (lowerMsg.includes('calories')) {
            return "**Calorie Information:**\n* Apple - 95 calories\n* Banana - 105 calories\n* Orange - 62 calories";
        } else {
            return "I'm your virtual health assistant.";
        }
    }
    function addMessage(text, className) {
        const div = document.createElement('div');
        div.classList.add('message', className);
        div.innerHTML = className === 'bot-message'
            ? parseMarkdown(text)
            : text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
        chatMessages.appendChild(div);
        scrollToBottom();
    }
    function setInputState(enabled) {
        userInput.disabled = !enabled;
        sendBtn.disabled = !enabled;
        userInput.placeholder = enabled ? "Type your message..." : "Please wait...";
    }
    function parseMarkdown(text) {
        let html = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');
        html = html.replace(/^\* (.*$)/gim, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        if (!html.startsWith('<')) html = '<p>' + html + '</p>';
        return html;
    }
    function addTypingIndicator() {
        const typing = document.createElement('div');
        typing.classList.add('typing-indicator');
        typing.innerHTML = `
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>`;
        chatMessages.appendChild(typing);
        scrollToBottom();
        return typing;
    }
    function scrollToBottom() {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    }
});
