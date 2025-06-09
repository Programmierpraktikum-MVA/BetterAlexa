//SendAudioRawData
#include <iostream>
#include <cstdint>
#include <fstream>
#include <cstring>
#include <cstdio>
#include <vector>

#include "ZoomSDKAudioRawData.h"
#include "rawdata/rawdata_audio_helper_interface.h"
#include "ZoomSDKVirtualAudioMicEvent.h"
#include "zoom_sdk_def.h" 
#include "audioHandling.h"
#include "meeting_sdk.h"
#include <mutex>


#include <thread>
#include <chrono>  // for sleep
#include <cmath>

extern "C" {
    #include "./miniaudio.h"
    }

using namespace std;
using namespace ZOOM_SDK_NAMESPACE;

int audio_play_flag = -1;

std::mutex m;
/*this is the recomended way, but if you call "send" more then once it will (does for me) fuck up. 
	higher speeds, corrupted audio without any apparent reason.I found that the way around that is 
	to play stuff on the mic it selects in the zoom_sdk file (see audioHandling)
*/

void ZoomSDKVirtualAudioMicEvent::PlayAudioFileToVirtualMic(){
	while (audio_play_flag > 0 && this->pSender_) {
		unsigned long long nFrames;
		
		std::cout << "playing audio" << std::endl;
		//read and decode mp3. Decoder should take about any file, only tested mp3s tho. see miniaudio for details
		char *outputBuf = (char *) audioHandling::decodeMp3File(this->audio_source.c_str(),&nFrames);
		uint64_t bufSize = nFrames * 16/8;
			
		SDKError err = this->pSender_->send( outputBuf, bufSize,48000 , ZOOMSDK::ZoomSDKAudioChannel::ZoomSDKAudioChannel_Mono);
		if (err != SDKERR_SUCCESS && this->playSmth) {
			std::cout << "Error: Failed to send audio data to virtual mic. Error code: " << err << std::endl;
			zoom::setIsPlaying(false);
		}		

		auto end = std::chrono::steady_clock::now() + std::chrono::seconds(nFrames/48000);
		while (std::chrono::steady_clock::now() < end) {
			std::this_thread::yield();
		}
		
		//to record and answer again
		zoom::setIsPlaying(false);

		std::cout<<"playing "<<nFrames<<" frames"<<std::endl;
		//audioHandling::saveFile("testaudio.wav", outputBuf,bufSize,48000,1,16);  //debug, uncomment to see into the pipeline
		free(outputBuf);
		std::cout << "finnished audio" << std::endl;

		audio_play_flag = -1;
	}
}

/// \brief Callback for virtual audio mic to do some initialization.
/// \param pSender, You can send audio data based on this object, see \link IZoomSDKAudioRawDataSender \endlink.
void ZoomSDKVirtualAudioMicEvent::onMicInitialize(IZoomSDKAudioRawDataSender* pSender) {
	// pSender->send();	
	pSender_ = pSender;
	printf("ZoomSDKVirtualAudioMicEvent OnMicInitialize, waiting for turnOn chat command\n");
}

void ZoomSDKVirtualAudioMicEvent::setRawDataForCallBack(ZoomSDKAudioRawData* o){
	this->sendOrigin = o;
}

void ZoomSDKVirtualAudioMicEvent::send(const char * fileName) {
	this->audio_source = fileName;
	audio_play_flag = 1;
	thread(&ZoomSDKVirtualAudioMicEvent::PlayAudioFileToVirtualMic,this).detach();

}

/// \brief Callback for virtual audio mic can send raw data with 'pSender'.
void ZoomSDKVirtualAudioMicEvent::onMicStartSend() {
	printf("onMicStartSend\n");
	std::cout << "onStartSend" << std::endl;
	if (pSender_ && audio_play_flag != 1) {
		while (audio_play_flag > -1) {}
		audio_play_flag = 1;
		thread(&ZoomSDKVirtualAudioMicEvent::PlayAudioFileToVirtualMic,this).detach();

	}
}

/// \brief Callback for virtual audio mic should stop send raw data.
void ZoomSDKVirtualAudioMicEvent::onMicStopSend() {
	printf("onMicStopSend\n");
	audio_play_flag = 0;
}
/// \brief Callback for virtual audio mic is uninitialized.
void ZoomSDKVirtualAudioMicEvent::onMicUninitialized() {
	std::cout << "onUninitialized" << std::endl;
	this->pSender_ = nullptr;
}

ZoomSDKVirtualAudioMicEvent::ZoomSDKVirtualAudioMicEvent(std::string audio_source)
{
	this->audio_source = audio_source;
}
