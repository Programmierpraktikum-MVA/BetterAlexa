#include <iostream>
#include <fstream>
#include <cstdio>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
#include <unistd.h>
#include <chrono> 
#include "meeting_sdk.h"
#include <thread>

#include "terminalInteractions.h"


namespace cmd{
    std::string create_vSpeaker;
    std::string create_vMic;
    std::string path_to_pythonVenv;
    std::string path_to_client;
    std::string path_to_client_folder;

    //defining those in the config reading fn meeting_sdk (cmd::path_to_cliend = [path]) didnt work
    //less elegant but who cares
    void setcreate_vSpeaker(std::string a){
        create_vSpeaker = a;
    }
    void setcreate_vMic(std::string a){
        create_vMic = a;
    }
    void setpath_to_pythonVenv(std::string a){
        path_to_pythonVenv = a;
    }
    void setpath_to_client(std::string a){
        path_to_client = a;
    }
    void setpath_to_client_folder(std::string a){
        path_to_client_folder = a;
    }


    int getLen(char * buf, int maxLen){
        for (int i = 0; i < maxLen; i++){
            if (buf[i] == 0){
                return i+1;
            }
        }   
        return -1;
    }
   
    //didnt work when this was a class, bc the class obj gets deleted, once the calling fn is finished(?) 
    //this works and looks better imo, so its staying
    void playFileWrapper(std::string fileName, int fileNum){
        if(sendAndCopyFile(fileName,fileNum) != 0){
            zoom::setIsPlaying(false);
        }
        return;
    }

    //execute command, copy that cout into output. cerr comes to our terminal tho
    //works for me but for logging you might want to change that
    int exec(std::string command, std::vector<char> *output){
        std::cout<<"executing command: " + command<<std::endl; 
        FILE * pipe = popen(command.c_str(), "r");
        if (!pipe){return -1;}

        int bufLen = 128;
        char * buf = (char *) malloc(bufLen);

        if (buf == NULL){
            return -1;
        }
        int retVal = 0;
        try{
            while(fgets(buf, bufLen, pipe) != 0){
                if (ferror(pipe)!= 0){return 1;}

                int l = getLen(buf, bufLen);
                if (l > 0){
                    output->insert(output->end(),buf, buf + l);
                }
            }
        } catch (int i){
            retVal = -2;
        }
        free(buf);
        pclose(pipe);
        return retVal;
    }

    //the recomended way of sending (virtualAudioMicEvent) will only work properly once, then speed up and fuck with the audio data
    //this way we route the output of audioHandling into a virtSpeaker and loop that into a vMic to use for the bot into zoom
    //thanks for that one guy on the forum that recomended that! Here we set both (but only once!)
    int setVSpeakerAndMic(std::string vSpeaker){
        std::vector<char> output;
        
        //audioHandling will absolutely use any virt audio mic and will (very probably) not play properly if theres more then one
        std::string command = "pactl list sinks";
        if (exec(command, &output) != 0){return -1;}
        std::string out(output.begin(),output.end());
        
        if (out.find(vSpeaker) != std::string::npos){
            std::cout << "speaker and mic already existed from earlier run"<<std::endl;
            return 0;
        }
        
        command = create_vSpeaker + " && " + create_vMic;
        if (exec(command, &output) != 0){return -1;}

        //typically expects two integer return values for pactl stuff. like 22\n23\n\0, so seven chars, seven bytes. 
        //if its more, something has prob gone wrong and we dont have the speakers available.
        if (output.size() > 7){
            return -1;
        }
        std::cout << "set vMic and Speaker" << std::endl;
        return 0;
    }

    int deleteClientOutPut(bool notGoneThroughToPlaying){
        if (notGoneThroughToPlaying){zoom::setIsPlaying(false);}
        std::string c = "rm " + path_to_client_folder;
        c = c + "response.mp3; " + c +"done; " + c + "error; " + c + "audio.wav";
        std::vector<char> output;
        return exec(c, &output);
    }

    //couple of things that need to happen: We need to copy the file to the client, call it, wait for it to finish,
    //decide if it worked, if so, copy the response and play it, if not then output the error, in any case we need 
    //to delete the done file thats set once the client finished and for cleanliness get rid of error or response.mp3 too.
    int sendAndCopyFile(std::string fileNameIn, int fileNumber){
        //copy recording to client folder
        const char * fileName = fileNameIn.c_str();
        std::string command = "cp " + fileNameIn + " " + path_to_client_folder + "audio.wav";
        std::vector<char> output;
        if (exec(command, &output) != 0 || output.size() > 0){return -1;}

        //executing sendfile script, using python3 executable from relevant venv. Will fail if thats not set to be executable
        command = path_to_pythonVenv +" " + path_to_client + " " + path_to_client_folder + "audio.wav";
        int err = exec(command, &output);
        if (err == -1 || output.size() <= 0){deleteClientOutPut(true);return -1;} 
    

        //modified client script will create a file called "done" in its folder. 
        //access is a relatively lightweight way to check for its existence important to delete it after tho
        std::string DFP = path_to_client_folder+"done";
        const char * doneFilePath = DFP.c_str();
        int timeToWait = 30;
        while(access(doneFilePath, F_OK) == -1){
          std::this_thread::sleep_for(std::chrono::milliseconds(500));
          timeToWait -= 1;
          //stop after [timeToWait/2 = 15]s so we dont stay here forever 
          if (timeToWait <= 0){
            std::cout << "betterAlexa client didnt work or took too long" << std::endl;
            deleteClientOutPut(true);
            return -1;
          }
        }

        //if smth has gone wrong the sendfile script will spit out a file called error
        DFP = path_to_client_folder + "error";
        std::string responseName = "./response"+ std::to_string(fileNumber)+".mp3";
        bool worked = false;
        if (access(DFP.c_str(), F_OK) == -1){
            //if that file doesnt exist, there will be a response.mp3 file that we can copy to our folder and play that
            command = "mv " + path_to_client_folder + "response.mp3 ./"+ responseName;
            worked = true;
        } else{
            //if the error file does exist well keep it for record keeping and print its content
            std::ifstream file(DFP); 
            if (!file) {deleteClientOutPut(true);return -1;}

            std::string line;
            while (std::getline(file, line)) { 
                std::cout << line << std::endl;
            }
            file.close();

            command = "mv " + path_to_client_folder + "error ./error"+std::to_string(fileNumber);
        }
        if (exec(command, &output) != 0){deleteClientOutPut(true);return  -1;} 

        //if we dont have an mp3 we can play it
        if (worked){
            zoom::CheckAndStartRawSending(responseName.c_str());
        }
        //in any case we need to delete some files {done ^ (error v response.mp3)}
        deleteClientOutPut(false);
        return 0;
    }
}