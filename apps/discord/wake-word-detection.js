const speech = require('@google-cloud/speech');
const {
    Porcupine,
    BuiltinKeyword,
}= require("@picovoice/porcupine-node");
const accessKey = "iAAmSEhqCCoZq0kN1XIlom6y6g2wXjrpM6PsFxlhCaVeQeaVHPKNHA=="

class wakeWordDetection
{
    constructor(hotword, connection, voiceReceiverStream)
    {
        // boolean to check if it's currently recording to google speech api
        this.recording = false;
        this._connection = connection;
        this._guild = connection.channel.guild
        this._inputFormat = {
            config:
                {
                    encoding: 'LINEAR16',
                    audioChannelCount: 1,
                    sampleRateHertz: 16000,
                    languageCode: 'en-US'
                }};
        this._transcribed = '';
        this.startPorcupine(hotword, voiceReceiverStream);
    }
}

startPorcupine(hotword, voiceReceiverStream)
{
    // Porcupine takes in audio in chunks (frames). .frame_length property gives the size of
    // each frame. Porcupine accepts 16 kHz audio with 16-bit samples. For each frame,
    // Porcupine returns a number representing the detected keyword. -1 indicates no
    // detection. Positive indices correspond to keyword detections.

    this.porcupine = new Porcupine(
        accessKey,
        ['./wake-word/hey_bellamy.js'],
        [0.5]
    )

    keyword_index = porcupine.process(audio_frame)
    if (keyword_index >= 0){
        // Logik zum händel von keyword event
    } else {
        // discard audio frame
    }


}

while(true){
    let keywordIndex = porcupine.process("getNextAudioFrame");
    if (keywordIndex !== -1) {
        // detection event callback
    }
}
