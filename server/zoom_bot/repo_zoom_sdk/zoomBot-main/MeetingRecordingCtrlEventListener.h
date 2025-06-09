
#include <meeting_service_components/meeting_recording_interface.h>
#include "zoom_sdk.h"


USING_ZOOM_SDK_NAMESPACE

class MeetingRecordingCtrlEventListener :public IMeetingRecordingCtrlEvent
{

	void (*onIsGivenRecordingPermission_)();
public:
	MeetingRecordingCtrlEventListener(void (*onIsGivenRecordingPermission)());

	/// \brief Callback event that the status of my local recording changes.
	/// \param status Value of recording status. For more details, see \link RecordingStatus \endlink enum.
	virtual void onRecordingStatus(RecordingStatus status);

	/// \brief Callback event that the status of cloud recording changes.
	/// \param status Value of recording status. For more details, see \link RecordingStatus \endlink enum.
	virtual void onCloudRecordingStatus(RecordingStatus status);

	/// \brief Callback event that the recording authority changes.
	/// \param bCanRec TRUE indicates to enable to record.
	virtual void onRecordPrivilegeChanged(bool bCanRec);

	/// \brief Callback event that the status of request local recording privilege.
	/// \param status Value of request local recording privilege status. For more details, see \link RequestLocalRecordingStatus \endlink enum.
	virtual void onLocalRecordingPrivilegeRequestStatus(RequestLocalRecordingStatus status);

	/// \brief Callback event for when the host responds to a cloud recording permission request
	/// \param status Value of request host to start cloud recording response status. For more details, see \link RequestStartCloudRecordingStatus \endlink enum.
	virtual void onRequestCloudRecordingResponse(RequestStartCloudRecordingStatus status);

	/// \brief Callback event when a user requests local recording privilege.
	/// \param handler A pointer to the IRequestLocalRecordingPrivilegeHandler. For more details, see \link IRequestLocalRecordingPrivilegeHandler \endlink.
	virtual void onLocalRecordingPrivilegeRequested(IRequestLocalRecordingPrivilegeHandler* handler);

	/// \brief Callback event received only by the host when a user requests to start cloud recording.
	/// \param handler A pointer to the IRequestStartCloudRecordingHandler. For more details, see \link IRequestStartCloudRecordingHandler \endlink.
	virtual void onStartCloudRecordingRequested(IRequestStartCloudRecordingHandler* handler);

	/// \brief Callback event that the cloud recording storage is full.
	/// \param gracePeriodDate a point in time, in milliseconds, in UTC. You can use the cloud recording storage until the gracePeriodDate.
	virtual void onCloudRecordingStorageFull(time_t gracePeriodDate);

	/// \brief Callback event received only by the host when a user requests to enable and start smart cloud recording.
	/// \param handler A pointer to the IRequestEnableAndStartSmartRecordingHandler. For more details, see \link IRequestEnableAndStartSmartRecordingHandler \endlink.
	virtual void onEnableAndStartSmartRecordingRequested(IRequestEnableAndStartSmartRecordingHandler* handler);

	/// \brief Callback event received when you call \link EnableSmartRecording \endlink. You can use the handler to confirm or cancel enabling the smart recording.
	/// \param handler A pointer to the ISmartRecordingEnableActionHandler. For more details, see \link ISmartRecordingEnableActionHandler \endlink.
	virtual void onSmartRecordingEnableActionCallback(ISmartRecordingEnableActionHandler* handler);

	virtual void onTranscodingStatusChanged(TranscodingStatus status, const zchar_t* path);

};

