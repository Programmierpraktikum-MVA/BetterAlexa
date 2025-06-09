#include "meeting_service_components/meeting_reminder_ctrl_interface.h" // Assuming this header includes the required definitions
#include "zoom_sdk.h"

USING_ZOOM_SDK_NAMESPACE


class MeetingReminderEventListener : public ZOOM_SDK_NAMESPACE::IMeetingReminderEvent
{
public:
    MeetingReminderEventListener();

	/// \brief Callback event of the reminder dialog show.
	/// \param content The detail content in the reminder dialog. For more details, see \link IMeetingReminderContent \endlink enum.
	/// \param handle A pointer to the IMeetingReminderHandler. For more details, see \link IMeetingReminderHandler \endlink.
	virtual void onReminderNotify(IMeetingReminderContent* content, IMeetingReminderHandler* handle);

	/// \brief Callback event of the enable reminder dialog show.
	/// \param content The detail content in the reminder dialog. For more details, see \link IMeetingEnableReminderHandler \endlink enum.
	/// \param handle A pointer to the IMeetingReminderHandler. For more details, see \link IMeetingEnableReminderHandler \endlink.
	virtual void onEnableReminderNotify(IMeetingReminderContent* content, IMeetingEnableReminderHandler* handle);
    
};