// Minimal browser mic → WAV recorder.
//
// Why Web Audio API and not MediaRecorder:
//   MediaRecorder produces WebM/Opus, which the Azure Speech SDK on the
//   server would need GStreamer to consume. Capturing raw PCM in the
//   browser and emitting a WAV blob keeps the server pipeline identical
//   to an uploaded .wav file.

(function () {
    const TARGET_SAMPLE_RATE = 16000;

    class MicRecorder {
        constructor() {
            this._audioContext = null;
            this._stream = null;
            this._processor = null;
            this._source = null;
            this._chunks = [];
            this._recording = false;
        }

        async start() {
            if (this._recording) return;
            this._chunks = [];

            this._stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            // AudioContext will resample input to this sampleRate for us.
            this._audioContext = new (window.AudioContext || window.webkitAudioContext)({
                sampleRate: TARGET_SAMPLE_RATE,
            });

            this._source = this._audioContext.createMediaStreamSource(this._stream);
            // ScriptProcessorNode is deprecated but still universally supported;
            // AudioWorklet would add a separate file for no demo-time benefit.
            this._processor = this._audioContext.createScriptProcessor(4096, 1, 1);

            this._processor.onaudioprocess = (e) => {
                const input = e.inputBuffer.getChannelData(0);
                // Copy -- the underlying buffer is reused by the browser.
                this._chunks.push(new Float32Array(input));
            };

            this._source.connect(this._processor);
            this._processor.connect(this._audioContext.destination);
            this._recording = true;
        }

        async stop() {
            if (!this._recording) return null;
            this._recording = false;

            this._processor.disconnect();
            this._source.disconnect();
            this._stream.getTracks().forEach((t) => t.stop());
            await this._audioContext.close();

            const sampleRate = this._audioContext.sampleRate; // should be 16000
            const pcm = flattenFloat32(this._chunks);
            const wavBlob = encodeWav(pcm, sampleRate);

            this._chunks = [];
            this._audioContext = null;
            this._stream = null;
            this._processor = null;
            this._source = null;

            return wavBlob;
        }

        get isRecording() {
            return this._recording;
        }
    }

    function flattenFloat32(chunks) {
        let length = 0;
        for (const c of chunks) length += c.length;
        const out = new Float32Array(length);
        let offset = 0;
        for (const c of chunks) {
            out.set(c, offset);
            offset += c.length;
        }
        return out;
    }

    function encodeWav(pcmFloat32, sampleRate) {
        const numChannels = 1;
        const bytesPerSample = 2;
        const byteRate = sampleRate * numChannels * bytesPerSample;
        const blockAlign = numChannels * bytesPerSample;
        const dataSize = pcmFloat32.length * bytesPerSample;
        const buffer = new ArrayBuffer(44 + dataSize);
        const view = new DataView(buffer);

        writeString(view, 0, "RIFF");
        view.setUint32(4, 36 + dataSize, true);
        writeString(view, 8, "WAVE");
        writeString(view, 12, "fmt ");
        view.setUint32(16, 16, true);            // PCM subchunk size
        view.setUint16(20, 1, true);             // PCM format
        view.setUint16(22, numChannels, true);
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, byteRate, true);
        view.setUint16(32, blockAlign, true);
        view.setUint16(34, 16, true);            // bits per sample
        writeString(view, 36, "data");
        view.setUint32(40, dataSize, true);

        let offset = 44;
        for (let i = 0; i < pcmFloat32.length; i++, offset += 2) {
            const s = Math.max(-1, Math.min(1, pcmFloat32[i]));
            view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
        }

        return new Blob([view], { type: "audio/wav" });
    }

    function writeString(view, offset, str) {
        for (let i = 0; i < str.length; i++) {
            view.setUint8(offset + i, str.charCodeAt(i));
        }
    }

    // Attach a record/stop/preview UI to a form, dropping the recorded WAV
    // into an existing <input type="file"> so the existing POST handler
    // sees it as if the user had uploaded a file.
    //
    // opts:
    //   buttonId      -- id of the record/stop toggle button
    //   statusId      -- id of the element that shows status text
    //   previewId     -- id of the <audio> element for playback
    //   fileInputId   -- id of the <input type="file"> to populate
    //   fileName      -- name to use for the synthesized File object
    function attachRecorderUi(opts) {
        const button = document.getElementById(opts.buttonId);
        const status = document.getElementById(opts.statusId);
        const preview = document.getElementById(opts.previewId);
        const fileInput = document.getElementById(opts.fileInputId);

        if (!button || !status || !preview || !fileInput) {
            console.warn("attachRecorderUi: missing one or more elements", opts);
            return;
        }

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            button.disabled = true;
            status.textContent = "Microphone not available in this browser.";
            return;
        }

        const recorder = new MicRecorder();
        const RECORD_LABEL = "Record from Microphone";
        const STOP_LABEL = "Stop Recording";
        button.textContent = RECORD_LABEL;

        button.addEventListener("click", async () => {
            if (!recorder.isRecording) {
                try {
                    await recorder.start();
                    button.textContent = STOP_LABEL;
                    button.classList.remove("btn-outline-secondary");
                    button.classList.add("btn-danger");
                    status.textContent = "Recording...";
                    // Not required for form submit; existing preview/file are stale now.
                    fileInput.value = "";
                    preview.removeAttribute("src");
                } catch (err) {
                    status.textContent = "Could not access microphone: " + err.message;
                }
            } else {
                try {
                    const blob = await recorder.stop();
                    button.textContent = RECORD_LABEL;
                    button.classList.remove("btn-danger");
                    button.classList.add("btn-outline-secondary");
                    status.textContent = "Recorded " + Math.round(blob.size / 1024) + " KB. Ready to submit.";

                    preview.src = URL.createObjectURL(blob);

                    const file = new File([blob], opts.fileName || "recording.wav", { type: "audio/wav" });
                    const dt = new DataTransfer();
                    dt.items.add(file);
                    fileInput.files = dt.files;
                } catch (err) {
                    status.textContent = "Recording failed: " + err.message;
                }
            }
        });
    }

    window.MicRecorder = MicRecorder;
    window.attachRecorderUi = attachRecorderUi;
})();
