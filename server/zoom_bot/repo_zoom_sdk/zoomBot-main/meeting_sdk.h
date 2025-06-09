#ifndef MEETINGSDK_H
#define MEETINGSDK_H

namespace zoom{
    //check if you meet the requirements to send raw data
    void setIsPlaying(bool now);
    bool getIsPlaying();
    void CheckAndStartRawSending(const char * fileName);
    void muteUnmute();

}

#endif