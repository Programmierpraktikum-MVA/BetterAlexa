let recorder;
let isSpeaking = false;
let timeout = 0;
const uploadInterval = 10; // Wie oft überprüft werden soll in ms
const silenceThreshold = 0.01; // Schwellwert für Stille
const uploadThreshold = 500; // nach wie langer Stille hochgeladen werden soll in ms

async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const input = audioContext.createMediaStreamSource(stream);
    const analyser = audioContext.createAnalyser();
    input.connect(analyser);

    recorder = new Recorder(input, { numChannels: 1 });

    setInterval(async () => {
        const isSilent = await checkSilence(analyser);
        if (isSpeaking) {
            if (isSilent) {
                timeout++;
                if (timeout > uploadThreshold / uploadInterval) {
                    isSpeaking = false;
                    timeout = 0;
                    console.log('Recording stopped...')
                    await upload(recorder);
                }
            }
            else {
                timeout = 0;
            }
        }
        else {
            if (!isSilent) {
                isSpeaking = true;
                console.log('Recording started!');
                recorder.record();
            }
        }
    }, uploadInterval);
}
async function upload(recorder) {
    recorder.stop();
    recorder.exportWAV(async (blob) => {
        const formData = new FormData();
        formData.append('audio', blob, 'audio.wav');
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            console.log(result);
        } catch (error) {
            console.error('Error uploading audio:', error);
        }
    });
    recorder.clear();
}

async function checkSilence(analyser) {
    const bufferLength = analyser.fftSize;
    const dataArray = new Float32Array(bufferLength);
    analyser.getFloatTimeDomainData(dataArray);

    let sum = 0.0;
    for (const value of dataArray) {
        sum += value * value;
    }
    const rms = Math.sqrt(sum / bufferLength);

    return rms < silenceThreshold;
}