#ifndef TERMINALINTERACTIONS_H
#define TERMINALINTERACTIONS_H

#include <string>
#include <cstdio>
#include <vector>

namespace cmd{

    void setcreate_vSpeaker(std::string a);
    void setcreate_vSpeaker(std::string a);
    void setcreate_vMic(std::string a);
    void setpath_to_pythonVenv(std::string a);
    void setpath_to_client(std::string a);
    void setpath_to_client_folder(std::string a);

    void playFileWrapper(std::string fileName, int fileNum);


    int deleteClientOutPut(bool notGoneThroughToPlaying);
    int exec(std::string command, std::vector<char> * output);
    int setVSpeakerAndMic(std::string vSpeaker);
    int sendAndCopyFile(std::string fileNameIn, int fileNumber);
    
  
}

#endif