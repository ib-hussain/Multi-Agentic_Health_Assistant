document.addEventListener("DOMContentLoaded", function() {
    // DOM Elements
    const messageForm = document.getElementById('message-form');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const recordBtn = document.getElementById('record-btn');
    const chatMessages = document.getElementById('chat-messages');

    const attachImageBtn = document.getElementById('attach-image-btn');
    const uploadAudioBtn = document.getElementById('upload-audio-btn');
    const imageInput = document.getElementById('image-input');
    const audioInput = document.getElementById('audio-input');

    // State
    let isTyping = false;
    let mediaRecorder;
    let isRecording = false;
    let recordingTimer;
    let audioChunks = [];
    let currentStream;
    let pendingImageFile = null; // image to send with next prompt

    // Events
    attachImageBtn.addEventListener('click', () => imageInput.click());
    uploadAudioBtn.addEventListener('click', () => audioInput.click());
    imageInput.addEventListener('change', handleImageSelected);
    audioInput.addEventListener('change', handleAudioSelected);

    recordBtn.addEventListener('click', toggleRecording);
    window.addEventListener('beforeunload', handlePageUnload);
    messageForm.addEventListener('submit', handleMessageSubmit);

    // ----- Image attach flow -----
    function handleImageSelected(e) {
        const file = e.target.files[0];
        if (!file) return;

        const ext = (file.name.split('.').pop() || '').toLowerCase();
        const allowed = ['png', 'jpg', 'jpeg', 'ico'];
        if (!allowed.includes(ext)) {
            addMessage("Unsupported image type. Allowed: png, jpg, jpeg, ico.", 'bot-message');
            imageInput.value = '';
            pendingImageFile = null;
            return;
        }

        pendingImageFile = file;
        addMessage("Image attached. It will be sent with your next prompt.", 'bot-message');
    }

    async function uploadImage(file, promptText) {
        const ext = (file.name.split('.').pop() || '').toLowerCase();
        const form = new FormData();
        form.append('file', file, `upload.${ext}`);
        form.append('prompt', promptText || ' ');
        // If you ever want to pass user_id explicitly instead of relying on session:
        // form.append('user_id', window.USER_ID || '');

        const res = await fetch('/api/upload-image', { method: 'POST', body: form });
        if (!res.ok) {
            const err = await res.json().catch(()=>({}));
            throw new Error(err.error || 'Image upload failed');
        }
        const data = await res.json();
        return data; // {success, description?, message?, ext}
    }

    // ----- MP3 upload flow (save + transcribe, no chat send) -----
    async function handleAudioSelected(e) {
        const file = e.target.files[0];
        if (!file) return;

        const ext = (file.name.split('.').pop() || '').toLowerCase();
        if (ext !== 'mp3') {
            addMessage("Only .mp3 files are allowed for audio upload.", 'bot-message');
            audioInput.value = '';
            return;
        }

        try {
            showSpinnerOn(uploadAudioBtn);

            const form = new FormData();
            form.append('file', file, 'upload.mp3');

            const res = await fetch('/api/upload-audio', { method: 'POST', body: form });
            if (!res.ok) {
                const err = await res.json().catch(()=>({}));
                throw new Error(err.error || 'Audio upload failed');
            }
            const data = await res.json();

            userInput.value = data.transcription || "";
            userInput.focus();
            try {
                const len = userInput.value.length;
                userInput.setSelectionRange(len, len);
            } catch (_) {}

        } catch (err) {
            addMessage(`Audio upload error: ${err.message}`, 'bot-message');
        } finally {
            audioInput.value = '';
            hideSpinnerOn(uploadAudioBtn);
        }
    }

    // ----- Send text (and maybe image) -----
    async function handleMessageSubmit(e) {
        e.preventDefault();
        const message = userInput.value.trim();
        const hasImage = !!pendingImageFile;

        if (!message && !hasImage) return;

        setInputState(false);
        isTyping = true;

        let imageURL = null;
        try {
            if (hasImage) {
                showSpinnerOn(attachImageBtn);
                imageURL = URL.createObjectURL(pendingImageFile); // local preview immediately
                // Show user's message + image
                addMessageWithImage(message, imageURL, 'user-message');

                // Ask backend to save and describe (returns markup)
                const typingIndicator = addTypingIndicator();
                const server = await uploadImage(pendingImageFile, message);
                typingIndicator.remove();

                if (server.success) {
                    // Display returned markup as bot message (parseMarkdown handles it)
                    addMessage(server.description, 'bot-message');
                } else {
                    addMessage(`Error: ${server.message || 'Unable to describe image.'}`, 'bot-message');
                }
            } else {
                // Pure text flow (no image): keep your simple bot
                addMessage(message, 'user-message');
                const typingIndicator = addTypingIndicator();
                setTimeout(() => {
                    typingIndicator.remove();
                    addMessage(getBotResponse(message), 'bot-message');
                }, 800);
            }
        } catch (err) {
            addMessage(`Send failed: ${err.message}`, 'bot-message');
        } finally {
            userInput.value = '';
            if (imageURL) URL.revokeObjectURL(imageURL);
            pendingImageFile = null;
            imageInput.value = '';
            hideSpinnerOn(attachImageBtn);

            setInputState(true);
            isTyping = false;
        }
    }

    // ----- Recording / transcription (fill input only) -----
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

            mediaRecorder.start(100);
            isRecording = true;
            recordBtn.classList.add('recording');
            userInput.placeholder = "Recording... Click the mic again to stop";

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
            mediaRecorder.stop();
            isRecording = false;
            recordBtn.classList.remove('recording');
            userInput.placeholder = "Type your message...";
        }
    }

    async function handleRecordingStop() {
        try {
            if (!audioChunks.length) throw new Error("No audio data recorded");
            showSpinnerOn(recordBtn);

            const recordedBlob = new Blob(audioChunks, { type: (mediaRecorder && mediaRecorder.mimeType) || 'audio/webm' });
            const wavBlob = await convertToWav16kMono(recordedBlob);
            const transcription = await transcribeAudio(wavBlob);

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
            hideSpinnerOn(recordBtn);
            cleanupAudio();
        }
    }

    // ----- Audio processing helpers -----
    async function convertToWav16kMono(inputBlob) {
        const arrayBuffer = await inputBlob.arrayBuffer();
        const ac = new (window.AudioContext || window.webkitAudioContext)();
        const decodedBuffer = await ac.decodeAudioData(arrayBuffer);

        const length = decodedBuffer.length;
        const channels = decodedBuffer.numberOfChannels;
        const mixed = new Float32Array(length);
        for (let ch = 0; ch < channels; ch++) {
            const data = decodedBuffer.getChannelData(ch);
            for (let i = 0; i < length; i++) mixed[i] += data[i];
        }
        for (let i = 0; i < length; i++) mixed[i] = mixed[i] / channels;

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
        const bytesPerSample = 2;
        const blockAlign = 1 * bytesPerSample;
        const buffer = new ArrayBuffer(44 + samples.length * bytesPerSample);
        const view = new DataView(buffer);
        writeString(view, 0, 'RIFF');
        view.setUint32(4, 36 + samples.length * bytesPerSample, true);
        writeString(view, 8, 'WAVE');
        writeString(view, 12, 'fmt ');
        view.setUint32(16, 16, true);
        view.setUint16(20, 1, true);
        view.setUint16(22, 1, true);
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, sampleRate * blockAlign, true);
        view.setUint16(32, blockAlign, true);
        view.setUint16(34, 16, true);
        writeString(view, 36, 'data');
        view.setUint32(40, samples.length * bytesPerSample, true);
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

    // ----- UI helpers -----
    function showSpinnerOn(btn) {
        btn.disabled = true;
        btn.dataset.prev = btn.innerHTML;
        btn.innerHTML = '<div class="spinner"></div>';
    }
    function hideSpinnerOn(btn) {
        if (!btn.dataset.prev) return;
        btn.disabled = false;
        btn.innerHTML = btn.dataset.prev;
        delete btn.dataset.prev;
    }

    function setInputState(enabled) {
        userInput.disabled = !enabled;
        sendBtn.disabled = !enabled;
        userInput.placeholder = enabled ? "Type your message..." : "Please wait...";
    }

    function addMessage(text, className) {
        if (!text && className !== 'bot-message') return;
        const div = document.createElement('div');
        div.classList.add('message', className);
        div.innerHTML = className === 'bot-message'
            ? parseMarkdown(text || '')
            : (text || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        chatMessages.appendChild(div);
        scrollToBottom();
    }

    function addMessageWithImage(text, imageURL, className) {
        const div = document.createElement('div');
        div.classList.add('message', className);
        const safeText = (text || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');

        const img = document.createElement('img');
        img.src = imageURL;
        img.alt = "attached image";
        img.style.maxWidth = '240px';
        img.style.borderRadius = '12px';
        img.style.display = 'block';
        img.style.marginTop = safeText ? '8px' : '0';

        if (safeText) {
            const p = document.createElement('div');
            p.innerHTML = safeText;
            div.appendChild(p);
        }
        div.appendChild(img);

        chatMessages.appendChild(div);
        scrollToBottom();
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
