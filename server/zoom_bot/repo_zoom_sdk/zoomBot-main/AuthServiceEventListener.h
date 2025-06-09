#include "auth_service_interface.h"

USING_ZOOM_SDK_NAMESPACE


class AuthServiceEventListener : public IAuthServiceEvent
{
	
    	 void (*onAuthSuccess_)();
public:
    AuthServiceEventListener(void (*onAuthSuccess)());

    /// \brief Authentication result callback.
    /// \param ret Authentication result value.  For more details, see \link AuthResult \endlink enum.
    virtual void onAuthenticationReturn(AuthResult ret);

	/// \brief Callback of login result with fail reason.
	/// \param ret Login status. see \link LOGINSTATUS \endlink enum.
	/// \param pAccountInfo Valid when the ret is LOGINRET_SUCCESS. Otherwise NULL.
	/// \param reason Login fail reason. Valid when the ret is LOGIN_FAILED. Otherwise LoginFail_None. see \link LoginFailReason \endlink enum.
	virtual void onLoginReturnWithReason(LOGINSTATUS ret, IAccountInfo* pAccountInfo, LoginFailReason reason);

	/// \brief Logout result callback.
	virtual void onLogout();

	/// \brief Zoom identity has expired, please re-login or generate a new zoom access token via REST Api.
	virtual void onZoomIdentityExpired();

	/// \brief Zoom authentication identity will be expired in 10 minutes, please re-auth.
	virtual void onZoomAuthIdentityExpired();

	// /// \brief Notification service status changed callback.
    // /// \param status The value of transfer meeting service. For more details, see \link SDKNotificationServiceStatus \endlink.
	// virtual void onNotificationServiceStatus(SDKNotificationServiceStatus status) ;
};

