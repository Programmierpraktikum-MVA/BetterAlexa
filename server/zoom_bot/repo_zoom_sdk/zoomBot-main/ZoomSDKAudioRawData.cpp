//GetAudioRawData
#include "rawdata/rawdata_audio_helper_interface.h"
#include "ZoomSDKAudioRawData.h"
#include "zoom_sdk_def.h" 
#include <iostream>
#include "ZoomSDKVirtualAudioMicEvent.h"
#include "rawdata/zoom_rawdata_api.h"
#include <fstream>
#include "audioHandling.h"
#include "meeting_sdk.h"
#include "terminalInteractions.h"
#include <memory>

#include <vector>
#include <thread>
#include <chrono> 


uint32_t sampleRate=48000; 
uint16_t channels =1;
uint16_t bitsPerSample = 16;

/*recording:
    we get (very) short snippets of audio data in onMixedAudioRawDataReceived, all data right now (for single streams eg one per participant fill 
    onOneWayAudioRawDataReceived and change the settings in meetingSDK) usually 16bit signed, 48000hz, might change tho. 
    We test if those contain relevant data, and if we should make a request in talkingInAudio and SafeFileWrapper. If we wanna
    send the request we safe the buffer, give it to the modified betterAlexa client, wait for a response (also in SafeFileWrapper) and play 
    that with the playback object via the main zoom_sdk file.

    CheckAndStartRawRecording instantiates this object if we get the call back for becoming (co-)host, or getting recording permission (my understanding 
    is that wed need OAuth via the api for this but id prefer not to touch that). This way takes three clicks so im leaving it at that, but 
    we could also start our own meetings for a one command solution (see StartMeeting in meeting_sdk).
*/

ZoomSDKAudioRawData::ZoomSDKAudioRawData(){
	this->nFiles = 0;
    innitCapture(true); //resets some vars for testing for if we should make a request (false) plus for recording (true)
    this->audioThreshhold = 10;  //max allowed background noise, this worked for me, tho my mic isnt half bad and im testing in relative silence
    this->timeThreshholdSilence = 96000; //2s of silence until a request is made
    this->timeThreshholdAudio = 48000; //frames of audio until we consider it speach, this plus minLengthAudio is for more fine grained control
    this->minLengthOfAudio = 72000;  //we send files with more frames then this
    this->compensateForShortAudioInterference = 50; //the data can be pretty noisy, speech has consistently high values. This is per package (~600 frames)
    
}

void ZoomSDKAudioRawData::innitCapture(bool bufferAsWell){
    if (bufferAsWell){
        this->bufLen = 0;
        this->dataBuffer.clear();
        this->containedAudio = false;
    }
    this->isBreak = false;
	this->loudFrames = 0;
    this->framesOfSilence = 0;
}


int ZoomSDKAudioRawData::saveFileWrapper(){
    //too little audio and the request isnt going to contain a relevant question, wait for more
    if (this->bufLen < this->minLengthOfAudio){ 
        innitCapture(false);
        std::cout << "too little audio" << std::endl;
        return -1;
    }

    //keep previous request for datamining etc? disable if space saving is a concern
    std::string fileName = "./audio"+std::to_string(this->nFiles)+".wav";
    std::string responseName = "./response"+ std::to_string(this->nFiles)+".mp3";
    auto error = audioHandling::saveFile(fileName.c_str(),this->dataBuffer.data(),this->bufLen, sampleRate, channels, bitsPerSample);
    //maybe consider giving feedback to the participants in this case
    if (error != 0){
        std::cout<<"couldnt save, probably a bigger problem going on"<<std::endl;
        innitCapture(true);
        return -1;
    }
    std::cout<<"sent file " +fileName<<std::endl;
    
    zoom::setIsPlaying(true);
    std::thread(cmd::playFileWrapper, fileName, this->nFiles).detach();
	
	//zoom::CheckAndStartRawSending("response1.mp3");
    //startSendRawAudio("./response.mp3"); //maybe possible alternative way, see comments above function

	this->nFiles += 1;
    innitCapture(true);
    return 0;
}




//deprecated twice rn, see ZoomSDKVirtualAudioMicEvent.cpp and/or CheckAndStartRawSending() in meeting_sdk.cpp for alt ways of sending audio, never really worked well, so im taking the other route
//initializing the audio helper here specifically for one request might work, so im leaving it here, esp with regular sdk updates
// void ZoomSDKAudioRawData::startSendRawAudio(const char* audioFile)
// {
//     ZoomSDKVirtualAudioMicEvent * send_audio_source = new ZoomSDKVirtualAudioMicEvent(audioFile);
//     this->send_audio_helper = GetAudioRawdataHelper();
// 	SDKError err = this->send_audio_helper->setExternalAudioSource(send_audio_source);
	
// 	if (err != SDKERR_SUCCESS)
// 	{
// 		std::cerr << "Error occured start send raw audio" << std::endl;
// 		return;
// 	}
// 	std::cout << "Success start send raw audio" << std::endl;

//     //prob not the way you want to do this
//     std::this_thread::sleep_for(std::chrono::seconds(30));
//     this->send_audio_helper->unSubscribe();
// }

//checks if we need to (1) safe that part, (2) could be ready to make request (have more than an utterance) and (3) should do that now
bool ZoomSDKAudioRawData::talkingInAudio(char * buf, int bufLen){
    int tmpFOS = 0;
    int tmpLF = 0;
    bool containsAudio = false;
    for(int i = 0; i < bufLen; i++){
		int absVal = std::abs(buf[i]);
        if ((absVal)< this->audioThreshhold){
            tmpFOS += 1;
        }else{  
            tmpLF += 1;
        }
    }
    //(1) currently there is audio -> write package to buffer and not (3)*
    if (tmpLF > this->compensateForShortAudioInterference){
        this->loudFrames += tmpLF; 
        //*  
        this->isBreak = false;
        containsAudio = true; 

        //(2) there is enough audio to constitute speech
        if (this->loudFrames > this->timeThreshholdAudio){
            //one package is a fraction of a second, if we reset the break requirement everytime we wont get anywhere
            this->framesOfSilence = 0;
            this->containedAudio = true;
        }
    //no relevant audio, dont need to write it to the buffer
    }else {
        this->framesOfSilence += tmpFOS;
        //(3) is there enough audio to think that a request has ended?
        if (this->framesOfSilence > this->timeThreshholdSilence){
            this->loudFrames = 0;        
            this->isBreak = true;
        }
    }

    return containsAudio;
}


bool haveSetTransmissionDetails = false;

//get All audio data. Should work for onOneWayAudioRawDataReceived in a simmiliar way, if we treat every participant indivually, or mix all audios
//if we get this or that is determined in the config somewhere => developers.zoom.us/docs/meeting-sdk/linux/
void ZoomSDKAudioRawData::onMixedAudioRawDataReceived(AudioRawData* audioRawData)
{
    //we dont want to get in a loop talking to ourself
    if (zoom::getIsPlaying()){
        return;
    }

    if (!haveSetTransmissionDetails){
        //really not necessary, but hey. Didnt bother with bitsPerSample tho.. Do it if you want to, audioRawData->GetTimeStamp() is right there
	    sampleRate = audioRawData->GetSampleRate(); 
	    channels = audioRawData->GetChannelNum();
        haveSetTransmissionDetails = true;
    }
    char * buffer = audioRawData->GetBuffer();
	uint length = audioRawData->GetBufferLen();   
    if (buffer == nullptr || length <= 0){
        return;
    }

    //check if we need to save this snippet(~600frames => ~.01s)(containsAudio), if someone has been talking (this->containedAudio) 
    //and if theyve stopped now, that is if we should consider making a request(this->isBreak)
	bool containsAudio = talkingInAudio(buffer,length);

    //safe to buffer
	if (containsAudio) {
        this->dataBuffer.reserve(length);
        std::copy(buffer, buffer + length, std::back_inserter(this->dataBuffer));
        this->bufLen += length;
    }

	//make a request with that buffer
	if (this->isBreak && this->containedAudio){
		saveFileWrapper();
	}
}

void ZoomSDKAudioRawData::onShareAudioRawDataReceived(AudioRawData* data_)
{
}

void ZoomSDKAudioRawData::onOneWayInterpreterAudioRawDataReceived(AudioRawData* data_, const zchar_t* pLanguageName)
{
}

void ZoomSDKAudioRawData::onOneWayAudioRawDataReceived(AudioRawData* audioRawData, uint32_t node_id)
{
	//std::cout << "Received onOneWayAudioRawDataReceived" << std::endl;
	//add your code here
}
