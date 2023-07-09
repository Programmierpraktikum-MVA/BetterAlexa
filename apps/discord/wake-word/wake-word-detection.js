const {Porcupine, BuiltinKeyword} = require("@picovoice/porcupine-node");
const fs = require('fs');
const WaveFile = require('wavefile').WaveFile;
const env = require('dotenv').config({path: '../../.env'});


class WakeWordDetection {

    constructor() {
        if (env.error) throw env.error;
        this.accessKey = env.parsed.PICOVOICE_ACCESS_KEY;
        this.porcupine = new Porcupine(
            this.accessKey,
            ['./wake-word/Bellamy_en_linux_v2_2_0.ppn', BuiltinKeyword.GRASSHOPPER, BuiltinKeyword.BUMBLEBEE],
            [0.5, 0.5, 0.5]
        );
    }


    chunkArray(array, size) {
        return Array.from({length: Math.ceil(array.length / size)}, (v, index) =>
            array.slice(index * size, index * size + size)
        );
    }


    classify(file_path) {
        let wav = new WaveFile(fs.readFileSync(file_path))

        let frameLength = this.porcupine.frameLength
        let samples = wav.getSamples(true, Int16Array)
        let frames = this.chunkArray(samples, frameLength)

        if (frames && frames[frames.length - 1].length !== frameLength) {
            frames.pop();
        }

        for (let index = 0; index < frames.length; index++) {
            const keywordIndex = this.porcupine.process(frames[index]);
            if (keywordIndex >= 0) {
                return true;
            }
        }
        return false;
    }
    // TODO deconstruct for porcupine.release()
}

module.exports = WakeWordDetection;





