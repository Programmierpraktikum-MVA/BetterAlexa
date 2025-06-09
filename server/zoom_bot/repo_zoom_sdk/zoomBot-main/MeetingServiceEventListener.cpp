#include "MeetingServiceEventListener.h"
#include <rawdata/zoom_rawdata_api.h>
#include <iostream>

MeetingServiceEventListener::MeetingServiceEventListener(void (*onMeetingStarts)(), void (*onMeetingEnds)(), void (*onInMeeting)())
{
	onMeetingEnds_ = onMeetingEnds;
	onMeetingStarts_ = onMeetingStarts;
	onInMeeting_ = onInMeeting;
}

void MeetingServiceEventListener::onMeetingStatusChanged(MeetingStatus status, int iResult)
{
	std::cout << "onMeetingStatusChanged: " << status << ", iResult: " << iResult << std::endl;
	switch (status)
	{
	case MEETING_STATUS_IDLE:
		printf("No meeting is running.\n");
		break;
	case MEETING_STATUS_CONNECTING:
		printf("Connect to the meeting server status.\n");
		break;
	case MEETING_STATUS_WAITINGFORHOST:
		printf("Waiting for the host to start the meeting.\n");
		break;
	case MEETING_STATUS_INMEETING:
		printf("onMeetingStatusChanged() In Meeting.\n");
		if (onInMeeting_) onInMeeting_();
		break;
	case MEETING_STATUS_DISCONNECTING:
		printf("Disconnect the meeting server, leave meeting status.\n");
		break;
	case MEETING_STATUS_RECONNECTING:
		printf("Reconnecting meeting server status\n");
		break;
	case MEETING_STATUS_FAILED:
		printf("Failed to connect the meeting server.\n");
		break;
	case MEETING_STATUS_ENDED:
		printf("Meeting ends.\n");
		if (onMeetingEnds_) onMeetingEnds_();
		break;
	case MEETING_STATUS_UNKNOWN:
		printf("Unknown status.\n");
		break;
	case MEETING_STATUS_LOCKED:
		printf("Meeting is locked to prevent the further participants to join the meeting.\n");
		break;
	case MEETING_STATUS_UNLOCKED:
		printf("Meeting is open and participants can join the meeting.\n");
		break;
	case MEETING_STATUS_IN_WAITING_ROOM:
		printf("Participants who join the meeting before the start are in the waiting room.\n");
		break;


	}

}

void MeetingServiceEventListener::onMeetingStatisticsWarningNotification(StatisticsWarningType type)
{
	std::cout << "onMeetingStatisticsWarningNotification, type: " << type << std::endl;
}

void MeetingServiceEventListener::onMeetingParameterNotification(const MeetingParameter* meeting_param)
{
	std::cout << "onMeetingParameterNotification" << std::endl;
	if (onMeetingStarts_) onMeetingStarts_();
}

void MeetingServiceEventListener::onSuspendParticipantsActivities()
{
}

 void MeetingServiceEventListener::onAICompanionActiveChangeNotice(bool bActive) 
{
}

 void MeetingServiceEventListener::onMeetingTopicChanged(const zchar_t* sTopic)
 {
 }

 void MeetingServiceEventListener::onMeetingFullToWatchLiveStream(const zchar_t* sLiveStreamUrl)
 {
 }
