#include "AuthServiceEventListener.h"
#include <iostream>


AuthServiceEventListener::AuthServiceEventListener(void(*onAuthSuccess)())
{
    
    onAuthSuccess_ = onAuthSuccess;
}

void AuthServiceEventListener::onAuthenticationReturn(ZOOM_SDK_NAMESPACE::AuthResult ret) {
    if (ret == ZOOM_SDK_NAMESPACE::AuthResult::AUTHRET_JWTTOKENWRONG)
    {
        // SDK Auth call failed because the JWT token is invalid.
       std::cout << "Auth failed: JWT Token is invalid." << std::endl;
    }
    else if (ret == ZOOM_SDK_NAMESPACE::AuthResult::AUTHRET_SUCCESS)
    {
        // SDK Authenticated successfully
        std::cout << "Auth succeeded: JWT." << std::endl;
          if (onAuthSuccess_) onAuthSuccess_();
    }
    else 
        std::cout << "Auth failed: " << ret << std::endl;
}

void AuthServiceEventListener::onLoginReturnWithReason(LOGINSTATUS ret, IAccountInfo* pAccountInfo, LoginFailReason reason)
{
    std::cout << "onLoginReturnWithReason: " << reason << std::endl;
  
}

void AuthServiceEventListener::onLogout()
{
    std::cout << "onLogout" << std::endl;
}

void AuthServiceEventListener::onZoomIdentityExpired()
{
    std::cout << "onZoomIdentityExpired" << std::endl;
}

void AuthServiceEventListener::onZoomAuthIdentityExpired()
{
    std::cout << "onZoomAuthIdentityExpired" << std::endl;
}

// void AuthServiceEventListener::onNotificationServiceStatus(SDKNotificationServiceStatus status)
// {
//     std::cout << "onNotificationServiceStatus: " << status << std::endl;
// }

