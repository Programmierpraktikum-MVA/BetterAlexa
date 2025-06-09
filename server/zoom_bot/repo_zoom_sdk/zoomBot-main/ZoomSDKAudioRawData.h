#ifndef ZOOMSDKAUDIORAWDATA_H
#define ZOOMSDKAUDIORAWDATA_H

//GetAudioRawData
#include "rawdata/rawdata_audio_helper_interface.h"
#include "zoom_sdk_raw_data_def.h"
#include "zoom_sdk.h"
#include <vector>

USING_ZOOM_SDK_NAMESPACE

class ZoomSDKAudioRawData :	public IZoomSDKAudioRawDataDelegate {
private:
	int framesOfSilence;
	int loudFrames;
	bool isBreak;
	bool containedAudio;

	int audioThreshhold;
	int timeThreshholdSilence;
	int timeThreshholdAudio;
	int compensateForShortAudioInterference;

	int minLengthOfAudio;

	IZoomSDKAudioRawDataHelper * send_audio_helper;
	int sampleRate;
	
	std::vector<char> dataBuffer;
	unsigned int bufLen;
	int nFiles;


public:
	ZoomSDKAudioRawData();
	void innitCapture(bool bufferAsWell);
	virtual void onMixedAudioRawDataReceived(AudioRawData* data_);
	virtual void onOneWayAudioRawDataReceived(AudioRawData* data_, uint32_t node_id);
	virtual void onShareAudioRawDataReceived(AudioRawData* data_);
	virtual void onOneWayInterpreterAudioRawDataReceived(AudioRawData* data_, const zchar_t* pLanguageName);
	int saveFileWrapper();
	bool talkingInAudio(char * buf, int bufLen);
	void startSendRawAudio(const char* audioFile);
};


#endif