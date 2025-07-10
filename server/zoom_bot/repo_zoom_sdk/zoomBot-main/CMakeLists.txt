cmake_minimum_required(VERSION 3.16)

project(meetingSDK CXX C)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
add_definitions(-std=c++11)
set(CMAKE_BUILD_TYPE Debug)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin)

set(CMAKE_TOOLCHAIN_FILE "/home/betteralexa/vcpkg/scripts/buildsystems/vcpkg.cmake")

find_package(OpenSSL REQUIRED)
find_package(PkgConfig REQUIRED)
include_directories(/home/betteralexa/vcpkg/installed/x64-linux/include)
include_directories(/home/betteralexa/BetterAlexa/server/zoom_bot/repo_zoom_sdk/zoomBot-main/jwt-cpp/include)
#find_package(jwt-cpp CONFIG REQUIRED) #was commented
find_package(ZLIB REQUIRED)

#pybind integration
set(pybind11_DIR "/home/betteralexa/.venv/lib/python3.10/site-packages/pybind11/share/cmake/pybind11")
find_package(pybind11 REQUIRED)
pybind11_add_module(meeting_sdk
	meeting_sdk_pybind.cpp
	meeting_sdk.cpp
)

# Find GLib using pkg-config
pkg_check_modules(GLIB REQUIRED glib-2.0)
pkg_check_modules(GIO REQUIRED gio-2.0)


include_directories(${CMAKE_SOURCE_DIR}/include)
include_directories(${CMAKE_SOURCE_DIR}/include/h)
#include_directories(${CMAKE_SOURCE_DIR}/jwt-cpp/include) #new

# Include GLib directories
include_directories(${GLIB_INCLUDE_DIRS} ${GIO_INCLUDE_DIRS})
link_directories(${GLIB_LIBRARY_DIRS} ${GIO_LIBRARY_DIRS})
add_definitions(${GLIB_CFLAGS_OTHER} ${GIO_CFLAGS_OTHER})


include_directories(/usr/include/glib-2.0/)
include_directories(/usr/include/glib-2.0/glib)
include_directories(/usr/lib/x86_64-linux-gnu/glib-2.0/include/)
include_directories(/usr/lib64/glib-2.0/include/)


link_directories(${CMAKE_SOURCE_DIR}/lib/zoom_meeting_sdk)
link_directories(${CMAKE_SOURCE_DIR}/lib/zoom_meeting_sdk/qt_libs)
link_directories(${CMAKE_SOURCE_DIR}/lib/zoom_meeting_sdk/qt_libs/Qt/lib)
#link_directories(${CMAKE_SOURCE_DIR}/lib/portaudio)



add_executable(meetingSDK
              ${CMAKE_SOURCE_DIR}/meeting_sdk.cpp
              ${CMAKE_SOURCE_DIR}/miniaudio.c
              ${CMAKE_SOURCE_DIR}/MeetingReminderEventListener.h
              ${CMAKE_SOURCE_DIR}/MeetingReminderEventListener.cpp
              ${CMAKE_SOURCE_DIR}/MeetingServiceEventListener.h
              ${CMAKE_SOURCE_DIR}/MeetingServiceEventListener.cpp
              ${CMAKE_SOURCE_DIR}/NetworkConnectionHandler.h
              ${CMAKE_SOURCE_DIR}/NetworkConnectionHandler.cpp
              ${CMAKE_SOURCE_DIR}/AuthServiceEventListener.h
              ${CMAKE_SOURCE_DIR}/AuthServiceEventListener.cpp
              ${CMAKE_SOURCE_DIR}/MeetingParticipantsCtrlEventListener.h
              ${CMAKE_SOURCE_DIR}/MeetingParticipantsCtrlEventListener.cpp
              ${CMAKE_SOURCE_DIR}/MeetingRecordingCtrlEventListener.h
              ${CMAKE_SOURCE_DIR}/MeetingRecordingCtrlEventListener.cpp
              ${CMAKE_SOURCE_DIR}/ZoomSDKRenderer.h
              ${CMAKE_SOURCE_DIR}/ZoomSDKRenderer.cpp
              ${CMAKE_SOURCE_DIR}/ZoomSDKAudioRawData.h
              ${CMAKE_SOURCE_DIR}/ZoomSDKAudioRawData.cpp
              ${CMAKE_SOURCE_DIR}/ZoomSDKVideoSource.h
              ${CMAKE_SOURCE_DIR}/ZoomSDKVideoSource.cpp
              ${CMAKE_SOURCE_DIR}/ZoomSDKVirtualAudioMicEvent.h
              ${CMAKE_SOURCE_DIR}/ZoomSDKVirtualAudioMicEvent.cpp
              ${CMAKE_SOURCE_DIR}/audioHandling.cpp
              ${CMAKE_SOURCE_DIR}/audioHandling.h
              ${CMAKE_SOURCE_DIR}/terminalInteractions.cpp
              ${CMAKE_SOURCE_DIR}/terminalInteractions.h              
              )

# Link GLib libraries
target_link_libraries(meetingSDK ${GLIB_LIBRARIES} ${GIO_LIBRARIES})

target_link_libraries(meetingSDK m)
target_link_libraries(meetingSDK gcc_s gcc)
target_link_libraries(meetingSDK meetingsdk)
target_link_libraries(meetingSDK glib-2.0)
target_link_libraries(meetingSDK curl)
target_link_libraries(meetingSDK pthread)
#target_link_libraries(meetingSDK jwt-cpp::jwt-cpp) #was commented 
#target_link_libraries(meetingSDK jwt-cpp) #instead try this
target_link_libraries(meetingSDK OpenSSL::SSL OpenSSL::Crypto)
configure_file(${CMAKE_SOURCE_DIR}/config.txt ${CMAKE_SOURCE_DIR}/bin/config.txt COPYONLY)

file(COPY ${CMAKE_SOURCE_DIR}/lib/zoom_meeting_sdk/ DESTINATION ${CMAKE_SOURCE_DIR}/bin)
