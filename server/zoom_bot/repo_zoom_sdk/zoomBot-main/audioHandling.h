#ifndef AUDIOHANDLING_H
#define AUDIOHANDLING_H

extern "C" {
    #include "./miniaudio.h"
}
#include <iostream>
#include <vector> 
#include <mutex>


namespace audioHandling{


    struct AudioData {
        std::vector<float> samples;
        size_t position;
    };

    void * decodeMp3File(const char * fileName, unsigned long long *frameN);
    bool readWavFile(const char* filename, AudioData& audioData);
    int saveFile(const char* wavFilePath, void *dataBuffer, uint32_t bufLen, uint32_t sampleRate, uint16_t channels,uint16_t bitsPerSample);

};


class playback{
    private:
        int16_t * pCurData;
        void * origData;
        unsigned long long framesLeft;
        uint64_t bytesPerFrame;
        ma_device device;
        std::mutex frameCountM;

        ma_decoder decoder;
        bool finished;



    public:
        playback(const char * devName,int devNameLen);
        static void data_callback(ma_device* pDevice, void* pOutput, const void* pInput, ma_uint32 frameCount);
        int setFile(const char * fileName);
        void uninit();



};
#endif
