1. prerequisites:

vcpkg install jwt-cpp
sudo apt-get install libsfml-dev

for meetingsdk:
apt-get update && \
apt-get install -y build-essential cmake
apt-get install -y pkgconf
apt-get install -y gtkmm-3.0

apt-get install -y --no-install-recommends --no-install-suggests \
    libx11-xcb1 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    libxcb-shm0 \
    libxcb-randr0 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-xtest0


1.1 getting credentials and sdk:
https://marketplace.zoom.us/ log in, dropdown menu (develop) in top right corner > Build App > General App. Click through app creation: they will complain if there isnt an OAuth Redirect URL, isnt needed for us tho. https://zoom.us is a valid entry. Get client ID and secret, in "surface" select meetings, "Zoom App SDK" and add relevant apis (all event and api permissions, or API: getMeetingContext, getMEetingParticipants, getUserContext, geRecordingContext, setAudioState, getAudioState, shareComputerAudio, joinMeeting, getZoomRoomDeviceDetails; Events: onMyUserContextChange, onZoomRoomEvent), in "Embed" select MeetingSDK and download latest linux version, add Scopes (User>vier users zak token> view users zak token,Meeting>real-time media streams>real time audio streams, zoom App>enable zoom App with zoom meeting client)

1.2 setting credentials and sdk
add client id and secret to config.txt, also meeting number and password (must be personal meeting room if the app isnt published on the marketplace!). While were here: make sure the pactl commands work for you find alternative if not. There needs to be a an output that feeds an input, set the names of them in meeting_sdk.cpp>joinMeeting() line 662 following
Also we need the path to:
	 an executable of python within the venv of the BetterAlexa client. (.venv/bin/python3, make sure its set as executable tho)
	 the client folder where the audiofiles will come and go
	 the modified client.py file (sendFile.py) within said folder

Once youve got the zoomsdk, extract and add from that:
 -  `h` to `./include/h`
 - `qt_libs` to `./lib/zoom_meeting_sdk/qt_libs`
 - all the `lib******.so` files to `./lib/zoom_meeting_sdk/lib******.so`
 - `translation.json` to `./lib/zoom_meeting_sdk/json`
 - oficially: softlink  `libmeetingsdk.so` to `libmeetingsdk.so.1` within `./lib/zoom_meeting_sdk/` . You can use the command `ln -s libmeetingsdk.so libmeetingsdk.so.1` to do so
   works better: just copy and rename. sometimes the linker has problems with softlinks!

2. build:
set the CMakePresets and CMakeUserPresets and set(CMAKE_TOOLCHAIN_FILE "/home/tmg/vcpkg/scripts/buildsystems/vcpkg.cmake") in CMakeLists.txt

within build folder: cmake .. and cmake --build .

3. execut:
have betterAlexa running (not the client)
start personal meeting room
start compiled program (./bin/meetingSDK)
make bot host


Further notes:
		name of bot is set in meeting_sdk.cpp>JoinMeeting() l 602 withoutloginParam.userName = "Bot";
		exact details on when the bot listens/answers can be tuned in ZoomSdkAudioRawData.cpp>ZoomSDKAudioRawData() more detailed explanation can also be found there
