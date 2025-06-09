#include <cstring>
#include <cstdio>
#include <iostream>
#include <vector>

#include <fstream>
#include "zoom_sdk_raw_data_def.h"
#include <thread>
#include <chrono> 
#include "audioHandling.h"
#include <mutex>
#include "meeting_sdk.h"


extern "C" {
    #include "./miniaudio.h"
}

namespace audioHandling{

//thats the highlevel api. tried using that for the  virtualAudioMicEvent but that didnt work out
void * decodeMp3File(const char * fileName, unsigned long long  *frameN){
	ma_decoder_config outConfig = ma_decoder_config_init(ma_format_s16, 1, 48000);
    outConfig.encodingFormat = ma_encoding_format_mp3;

    void * buffer = nullptr;
    ma_result res = ma_decode_file(fileName, &outConfig, frameN, &buffer);

		return buffer;
}

//here still just in case well need to play .wavs at some point
// // WAV file header structure still good for testing(?)
// struct WavHeader {
//     char riff[4];        // "RIFF"
//     unsigned int size;   // Size of the file
//     char wave[4];        // "WAVE"
//     char fmt[4];         // "fmt "
//     unsigned int fmtSize;
//     unsigned short formatType;
//     unsigned short channels;
//     unsigned int sampleRate;
//     unsigned int byteRate;
//     unsigned short blockAlign;
//     unsigned short bitsPerSample;
//     char data[4];        // "data"
//     unsigned int dataSize;
// };
// bool readWavFile(const char* filename, AudioData& audioData) {
//     std::ifstream file(filename, std::ios::binary);
//     if (!file) {
//         std::cerr << "Could not open WAV file." << std::endl;
//         return false;
//     }

//     WavHeader header;
//     file.read(reinterpret_cast<char*>(&header), sizeof(WavHeader));

//     if (std::strncmp(header.riff, "RIFX", 4) != 0 || std::strncmp(header.wave, "WAVE", 4) != 0) {
//         std::cerr << "Not a valid WAV file." << std::endl;
//         return false;
//     }

//     audioData.samples.resize(header.dataSize / sizeof(float));
//     file.read(reinterpret_cast<char*>(audioData.samples.data()), header.dataSize);
//     audioData.position = 0;

//     return true;
// }


//saves databuffers pcm frames as a wav file. If you want to do it yourself, remember that wav is small endian!
int saveFile(const char* wavFilePath, void *dataBuffer, uint32_t bufLen, uint32_t sampleRate, uint16_t channels,uint16_t bitsPerSample) {
    auto format = ma_format_s16;
    if (bitsPerSample != 16){
        return -2;
    }
    //set prerequisits
    ma_encoder_config config = ma_encoder_config_init(ma_encoding_format_wav, format, channels, sampleRate);
    ma_encoder encoder;
    ma_result result = ma_encoder_init_file(wavFilePath, &config, &encoder);
    if (result != MA_SUCCESS) {
        return -1;
    }

    //actual writing
    uint64_t nFrames = channels*bufLen / (bitsPerSample/8);
    ma_uint64 framesWritten = nFrames;
    result = ma_encoder_write_pcm_frames(&encoder, dataBuffer, nFrames, &framesWritten);
    if (result != MA_SUCCESS) {
        std::cout<<"better Luck next time, no writing file rn" << std::endl;
        return -1;
    }

    ma_encoder_uninit(&encoder);
    return 0;
}

}

//function is called whenever the mic needs more data, that is frameCount frames written into pOutput
void playback::data_callback(ma_device* pDevice, void* pOutput, const void* pInput, ma_uint32 frameCount)
{
    playback* instance = static_cast<playback*>(pDevice->pUserData);
    ma_result result = ma_decoder_read_pcm_frames(&instance->decoder, pOutput, frameCount, NULL);

    //result will be MA_at_end, that is -17 if were finished. then well set finished = true, 
    //bc were not supposed to stop playback from within th callback
    if (result != MA_SUCCESS){
        instance->frameCountM.lock();
        instance->finished = true;
        instance->frameCountM.unlock();
    }

    (void)pInput;
}

//sets decoder and file, starts playing
int playback::setFile(const char * fileName){
    //decoder decodes file
    ma_decoder_config outConfig = ma_decoder_config_init(ma_format_s16, 1, 48000);
    outConfig.encodingFormat = ma_encoding_format_mp3;
    ma_result result = ma_decoder_init_file(fileName, &outConfig, &this->decoder);
    if (result != MA_SUCCESS) {
        std::cout<<"Could not load audio file"<<std::endl;
        zoom::setIsPlaying(false);
        return -2;
    }

    //finished is used to determin when we should stop playback
    std::cout<<"starting audio";
    this->frameCountM.lock();
    this->finished = false;
    zoom::setIsPlaying(true);

    if (ma_device_start(&this->device) != MA_SUCCESS) {
        printf("Failed to start playback device.\n");
        ma_device_uninit(&this->device);
        zoom::setIsPlaying(false);
        return -1;
    }

    //wait for finished == true
    while (!this->finished){
        this->frameCountM.unlock();
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
        std::cout<<".";
        this->frameCountM.lock();
    }
    this->frameCountM.unlock();

    //we might need a bit of time to readjust (has thrown some errors for me otherwise)
    std::this_thread::sleep_for(std::chrono::milliseconds(1000));

    if (ma_device_stop(&this->device) != MA_SUCCESS) {
        printf("Failed to stop playback device.\n");
        return -1;
    }
    std::cout<<"finished audio"<<std::endl;

    //thats to make sure were not answering twice at the same time
    zoom::setIsPlaying(false);
    ma_decoder_uninit(&this->decoder);

    return 0;
}


//set the device to prepare for playing. Needs to be done once	
playback::playback(const char * devName, int devNameLen){
    ma_result result;
    ma_device_config deviceConfig;
    ma_context context;

    if (ma_context_init(NULL, 0, NULL, &context) != MA_SUCCESS) {
        return;
    }

    ma_device_info* pPlaybackInfos;
    ma_uint32 playbackCount;
    ma_device_info* pCaptureInfos;
    ma_uint32 captureCount;
    if (ma_context_get_devices(&context, &pPlaybackInfos, &playbackCount, &pCaptureInfos, &captureCount) != MA_SUCCESS) {
        return;
    }

    //pactl will call the device devName.n for every n subsequent called device, so make sure youere only setting that once
    ma_uint32 rightDev = -1;
    for (ma_uint32 iDevice = 0; iDevice < playbackCount; iDevice += 1) {
        auto curDev = pPlaybackInfos[iDevice];
        if (strncmp(curDev.name,devName,devNameLen) == 0){
            std::cout<< curDev.name << "is selected" << std::endl;
            rightDev = iDevice;
        }
    }
    if (rightDev == -1){
        std::cout<<"could not find right audio device. Check how you configured the virtual speaker/mic and as what you defined them here" << std::endl;
        return;
    }

    //config sets the params for playback
    deviceConfig = ma_device_config_init(ma_device_type_playback);

    deviceConfig.playback.pDeviceID = &pPlaybackInfos[rightDev].id;
    deviceConfig.playback.format   = ma_format_s16;
    deviceConfig.playback.channels = 1;
    deviceConfig.sampleRate        = 48000;
    deviceConfig.dataCallback      = data_callback;
    deviceConfig.pUserData = this;
    
    this->bytesPerFrame = deviceConfig.playback.channels * 16/8;

    if (ma_device_init(NULL, &deviceConfig, &this->device) != MA_SUCCESS) {
        printf("Failed to open playback device.\n");
        return;
    }
}

void playback::uninit(){
    //free(this->origData);
    ma_device_uninit(&device);
}

