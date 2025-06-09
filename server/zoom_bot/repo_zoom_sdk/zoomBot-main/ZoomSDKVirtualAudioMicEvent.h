#ifndef ZOOMSDKVIRTUALAUDIOMICEVENT_H
#define ZOOMSDKVIRTUALAUDIOMICEVENT_H
//SendAudioRawData

#include <iostream>
#include <cstdint>
#include "rawdata/rawdata_audio_helper_interface.h"
#include "zoom_sdk.h"
#include "zoom_sdk_raw_data_def.h"
#include "ZoomSDKAudioRawData.h"


using namespace std;
using namespace ZOOMSDK;

class ZoomSDKVirtualAudioMicEvent :
	public IZoomSDKVirtualAudioMicEvent
{

private:
	IZoomSDKAudioRawDataSender* pSender_;
	std::string audio_source;
	ZoomSDKAudioRawData* sendOrigin;
	bool playSmth = true;
protected:

	/// \brief Callback for virtual audio mic to do some initialization.
/// \param pSender, You can send audio data based on this object, see \link IZoomSDKAudioRawDataSender \endlink.
	virtual void onMicInitialize(IZoomSDKAudioRawDataSender* pSender);

	/// \brief Callback for virtual audio mic can send raw data with 'pSender'.
	virtual void onMicStartSend();

	/// \brief Callback for virtual audio mic should stop send raw data.
	virtual void onMicStopSend();

	/// \brief Callback for virtual audio mic is uninitialized.
	virtual void onMicUninitialized();

public:
	void send(const char * fileName);
	ZoomSDKVirtualAudioMicEvent(std::string audio_source);
	void setRawDataForCallBack(ZoomSDKAudioRawData* o);
	void PlayAudioFileToVirtualMic();


};


#endif