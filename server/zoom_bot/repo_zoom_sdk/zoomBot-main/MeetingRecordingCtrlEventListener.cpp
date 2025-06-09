#include "MeetingRecordingCtrlEventListener.h"

using namespace std;


MeetingRecordingCtrlEventListener::MeetingRecordingCtrlEventListener(void(*onIsGivenRecordingPermission)())
{
	onIsGivenRecordingPermission_ = onIsGivenRecordingPermission;
}

/// \brief Callback event that the status of my local recording changes.
/// \param status Value of recording status. For more details, see \link RecordingStatus \endlink enum.
void MeetingRecordingCtrlEventListener::onRecordingStatus(RecordingStatus status) {}
/// \brief Callback event that the status of cloud recording changes.
/// \param status Value of recording status. For more details, see \link RecordingStatus \endlink enum.
void MeetingRecordingCtrlEventListener::onCloudRecordingStatus(RecordingStatus status) {}

/// \brief Callback event that the recording authority changes.
/// \param bCanRec TRUE indicates to enable to record.
void MeetingRecordingCtrlEventListener::onRecordPrivilegeChanged(bool bCanRec) {

	if (bCanRec) {
		if (onIsGivenRecordingPermission_)onIsGivenRecordingPermission_();
	}
}

/// \brief Callback event that the status of request local recording privilege.
/// \param status Value of request local recording privilege status. For more details, see \link RequestLocalRecordingStatus \endlink enum.
void MeetingRecordingCtrlEventListener::onLocalRecordingPrivilegeRequestStatus(RequestLocalRecordingStatus status) {}

void MeetingRecordingCtrlEventListener::onRequestCloudRecordingResponse(RequestStartCloudRecordingStatus status)
{
}


/// \brief Callback event when a user requests local recording privilege.
/// \param handler A pointer to the IRequestLocalRecordingPrivilegeHandler. For more details, see \link IRequestLocalRecordingPrivilegeHandler \endlink.
void MeetingRecordingCtrlEventListener::onLocalRecordingPrivilegeRequested(IRequestLocalRecordingPrivilegeHandler* handler) {}

void MeetingRecordingCtrlEventListener::onStartCloudRecordingRequested(IRequestStartCloudRecordingHandler* handler)
{
}

void MeetingRecordingCtrlEventListener::onCloudRecordingStorageFull(time_t gracePeriodDate)
{
}

void MeetingRecordingCtrlEventListener::onEnableAndStartSmartRecordingRequested(IRequestEnableAndStartSmartRecordingHandler* handler)
{
}

void MeetingRecordingCtrlEventListener::onSmartRecordingEnableActionCallback(ISmartRecordingEnableActionHandler* handler)
{
}

void MeetingRecordingCtrlEventListener::onTranscodingStatusChanged(TranscodingStatus status, const zchar_t* path)
{
}


