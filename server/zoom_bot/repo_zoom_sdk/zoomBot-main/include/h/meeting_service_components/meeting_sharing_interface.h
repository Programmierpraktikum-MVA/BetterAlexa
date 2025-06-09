/*!
* \file meeting_sharing_interface.h
* \brief Meeting Service Sharing Interface
* 
*/
#ifndef _MEETING_SHARING_INTERFACE_H_
#define _MEETING_SHARING_INTERFACE_H_
#include "zoom_sdk_def.h"

BEGIN_ZOOM_SDK_NAMESPACE
/*! \enum ShareSettingType
	\brief Share setting type.
	Here are more detailed structural descriptions..
*/
enum ShareSettingType
{
	ShareSettingType_LOCK_SHARE, ///<Only host can share, the same as "lock share"
	ShareSettingType_HOST_GRAB,   ///<Anyone can share, but one sharing only at one moment, and only host can grab other's sharing
	ShareSettingType_ANYONE_GRAB,  ///<Anyone can share, but one sharing only at one moment, and anyone can grab other's sharing
	ShareSettingType_MULTI_SHARE,  ///<Anyone can share, Multi-share can exist at the same time
	
};

/*! \enum AudioShareMode
	\brief Audio share mode.
	Here are more detailed structural descriptions.
*/
enum AudioShareMode
{
	AudioShareMode_Mono,		///<Mono mode.
	AudioShareMode_Stereo		///<Stereo mode
};

/*! \struct tagZoomSDKSharingSourceInfo
    \brief Visible shared source information.
    Here are more detailed structural descriptions..
*/
typedef struct tagZoomSDKSharingSourceInfo
{
	unsigned int userid;			///<User ID.
	unsigned int shareSourceID;		///<Share source ID.
	SharingStatus status;			///<The values of sharing status, see \link SharingStatus \endlink enum.
	bool isShowingInFirstView;		///<Display or not on the primary view. Available only for Zoom UI mode.
	bool isShowingInSecondView;		///<Display or not on the secondary view. Available only for Zoom UI mode.
	bool isCanBeRemoteControl;		///<Enable or disable the remote control.
	bool bEnableOptimizingVideoSharing;    ///<Enable or disable the optimizing video.

	ShareType contentType;			///<Type of sharing, see \link ShareType \endlink enum.
	HWND hwndSharedApp;				///<Handle of sharing application or white-board. It is invalid unless the value of the eShareType is SHARE_TYPE_AS or SHARE_TYPE_WB.
	const zchar_t* monitorID;		///<The ID of screen to be shared. It is invalid unless the value of the eShareType is SHARE_TYPE_DS.

	tagZoomSDKSharingSourceInfo()
	{
		userid = 0;
		shareSourceID = 0;
		contentType = SHARE_TYPE_UNKNOWN;
		status = Sharing_Self_Send_Begin;
		isShowingInFirstView = false;
		isShowingInSecondView = false;
		isCanBeRemoteControl = false;
		bEnableOptimizingVideoSharing = false;
		hwndSharedApp = nullptr;
		monitorID = nullptr;
	}
}ZoomSDKSharingSourceInfo;

/*! \enum AdvanceShareOption 
    Additional type of current sharing sent to others.
    Here are more detailed structural descriptions.
*/
enum AdvanceShareOption
{
	AdvanceShareOption_ShareFrame,///<Type of sharing a selected area of desktop.
	AdvanceShareOption_PureComputerAudio,///<Type of sharing only the computer audio.
	AdvanceShareOption_ShareCamera,///<Type of sharing the camera.
};

enum MultiShareOption
{
	Enable_Multi_Share = 0, ///<Multi-participants can share simultaneously.
	Enable_Only_HOST_Start_Share, ///<Only host can share at a time.
	Enable_Only_HOST_Grab_Share, ///<One participant can share at a time, during sharing only host can start a new sharing and the previous sharing will be replaced.
	Enable_All_Grab_Share, ///<One participant can share at a time, during sharing everyone can start a new sharing and the previous sharing will be replaced.
};

enum ZoomSDKVideoFileSharePlayError
{
	ZoomSDKVideoFileSharePlayError_None, 
	ZoomSDKVideoFileSharePlayError_Not_Supported, ///<Not supported.
	ZoomSDKVideoFileSharePlayError_Resolution_Too_High, ///<The resolution is too high to play.
	ZoomSDKVideoFileSharePlayError_Open_Fail, ///<Failed to open.
	ZoomSDKVideoFileSharePlayError_Play_Fail, ///<Failed to play.
	ZoomSDKVideoFileSharePlayError_Seek_Fail  ///<Failed to seek.
};

/// \brief Reminder handler of switching from multi-share to single share.
///
class IShareSwitchMultiToSingleConfirmHandler
{
public:
	/// \brief Cancel to switch multi-share to single share. All sharing will be remained.
	virtual SDKError Cancel() = 0;

	/// \brief Switch multi-share to single share. All sharing will be stopped.
	virtual SDKError Confirm() = 0;

	virtual ~IShareSwitchMultiToSingleConfirmHandler() {};
};

/// \brief Callback event of meeting share controller.
///
class IMeetingShareCtrlEvent
{
public:
	virtual ~IMeetingShareCtrlEvent() {}

	/// \brief Callback event of the changed sharing status. 
	/// \param shareInfo Sharing information. For more details, see \link ZoomSDKSharingSourceInfo \endlink structure.
	/// \remarks The userId changes according to the status value. When the status value is the Sharing_Self_Send_Begin or Sharing_Self_Send_End, the userId is the user own ID. Otherwise, the value of userId is the sharer ID.
	virtual void onSharingStatus(ZoomSDKSharingSourceInfo shareInfo) = 0;

	/// \brief Callback event of failure to start sharing. 
	virtual void onFailedToStartShare() = 0;

	/// \brief Callback event of locked share status.
	/// \param bLocked TRUE indicates that it is locked. FALSE unlocked.
	/// \deprecated This interface is marked as deprecated, and is replaced by onShareSettingTypeChangedNotification(ShareSettingType type).
	virtual void onLockShareStatus(bool bLocked) = 0;

	/// \brief Callback event of changed sharing information.
	/// \param shareInfo Sharing information. For more details, see \link ZoomSDKSharingSourceInfo \endlink structure.
	virtual void onShareContentNotification(ZoomSDKSharingSourceInfo shareInfo) = 0;

	/// \brief Callback event of switching multi-participants share to one participant share.
	/// \param handler_ An object pointer used by user to complete all the related operations. For more details, see \link IShareSwitchMultiToSingleConfirmHandler \endlink.
	virtual void onMultiShareSwitchToSingleShareNeedConfirm(IShareSwitchMultiToSingleConfirmHandler* handler_) = 0;	

	/// \brief Callback event of sharing setting type changed.
	/// \param type Sharing setting type. For more details, see \link ShareSettingType \endlink structure.
	virtual void onShareSettingTypeChangedNotification(ShareSettingType type) = 0;

	/// \brief Callback event of the shared video's playback has completed.
	virtual void onSharedVideoEnded() = 0;

	/// \brief Callback event of the video file playback error.
	/// \param error The error type. For more details, see \link ZoomSDKVideoFileSharePlayError \endlink structure.
	virtual void onVideoFileSharePlayError(ZoomSDKVideoFileSharePlayError error) = 0;

	/// \brief Callback event of the changed optimizing video status. 
	/// \param shareInfo Sharing information. For more details, see \link ZoomSDKSharingSourceInfo \endlink structure.
	virtual void onOptimizingShareForVideoClipStatusChanged(ZoomSDKSharingSourceInfo shareInfo) = 0;
};

/// \brief Meeting share controller interface.
///
class IMeetingShareController
{
public:
	/// \brief Set meeting share controller callback event handler.
	/// \param pEvent A pointer to the IMeetingShareCtrlEvent that receives sharing event. 
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	virtual SDKError SetEvent(IMeetingShareCtrlEvent* pEvent) = 0;
#if defined(WIN32)
	/// \brief Share the specified application.
	/// \param hwndSharedApp Specify the window handle of the application to be shared. If the hwndSharedApp can't be shared, the return value is the SDKERR_INVALID_PARAMETER error code. If the hwndSharedApp is nullptr, the primary monitor will be shared. 
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid for both ZOOM style and user custom interface mode.
	virtual SDKError StartAppShare(HWND hwndSharedApp) = 0;

	/// \brief Determine if the window handle can be shared.If the hwndSharedApp is nullptr, the return value is FALSE.
	/// \return True indicates the window handle can be shared. False means the app's window handle can't be shared.
	/// \remarks Valid for both ZOOM style and user custom interface mode.
	virtual bool IsShareAppValid(HWND hwndSharedApp) = 0;

	/// \brief Share the specified monitor.
	/// \param monitorID Specify the monitor ID to be shared. You may get the value via EnumDisplayMonitors System API. If the monitorID is nullptr, the primary monitor will be shared. For more details, see szDevice in MONITORINFOEX structure.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid for both ZOOM style and user custom interface mode.
	virtual SDKError StartMonitorShare(const zchar_t* monitorID) = 0;

	/// \brief A dialog box pops up that enable the user to choose the application or window to share.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid only for ZOOM style mode. 
	virtual SDKError ShowSharingAppSelectWnd() = 0;

	/// \brief Start sharing with mobile device. 
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid for both ZOOM style and user custom interface mode.
	virtual SDKError StartAirPlayShare() = 0;

	/// \brief Start sharing camera.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid for ZOOM style only.	
	virtual SDKError StartShareCamera() = 0;

	/// \brief Block the window when sharing in full screen.
	///Once the function is called, you need to redraw the window to take effect.
	/// \param bBlock TRUE indicates to block the window when sharing in full screen.
	/// \param hWnd Specify the window to be blocked.
	/// \param bChangeWindowStyle If it is FALSE, please call this function either after the StartMonitorShare is called or when you get the callback event of the onSharingStatus with Sharing_Self_Send_Begin. 
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid only for ZOOM style user interface mode.
	///It is not suggested to use this function for it will change the property of the window and leads to some unknown errors.
	///It won't work until the IMeetingShareController::StartMonitorShare() is called if the bChangeWindowStyle is set to FALSE. 
	///If you want to use the specified window during the share, you need to redraw the window.
	///Set the bBlock to FALSE before ending the share and call the function for the specified window to resume the property of the window.
	virtual SDKError BlockWindowFromScreenshare(bool bBlock, HWND hWnd, bool bChangeWindowStyle = true) = 0;
	
	/// \brief Switch to auto-adjust mode from sharing window by the function when watching the share on the specified view.
	/// \param type Specify the view you want to set, either primary or secondary. For more details, see \link SDKViewType \endlink enum.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid only for ZOOM style user interface mode.
	virtual SDKError SwitchToFitWindowModeWhenViewShare(SDKViewType type) = 0;

	/// \brief Switch the window size by the function when watching the share on the specified view.
	/// \param shareSourceID Specify the share scource ID that you want to switch zoom ratio.
	/// \param shareViewZoomRatio Specify the size you want to set. For more details, see \link ZMBShareViewZoomRatio \endlink enum.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	virtual SDKError SwitchZoomRatioWhenViewShare(unsigned int shareSourceID, SDKShareViewZoomRatio shareViewZoomRatio) = 0;

	/// \brief Enable follow presenter's pointer by the function when watching the share on the specified view.
	/// \param shareSourceID Specify the sharing source ID that you want to follow the presenter's pointer. 
	/// \param bEnable TRUE indicates to enable. FALSE not.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	virtual SDKError EnableFollowPresenterPointerWhenViewShare(unsigned int shareSourceID, bool bEnable) = 0;

	/// \brief Determine if the follow presenter's pointer can be enabled when watching the share on the specified view.
	/// \param shareSourceID Specify the share scource ID that you want to follow his pointer. 
	/// \param [out] bCan TRUE indicates that the pointer can be enabled. FALSE indicates that it can't.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise it fails. To get extended error information, see \link SDKError \endlink enum.
	virtual SDKError CanEnableFollowPresenterPointerWhenViewShare(unsigned int shareSourceID, bool& bCan) = 0;

	/// \brief View the share from the specified user.
	/// \param shareSourceID Specify the share scource ID that you want to view his share. 
	/// \param type Specify the view that you want to display the share, either primary or secondary. For more details, see \link SDKViewType \endlink enum.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid only for ZOOM style user interface mode.
	/// \deprecated This interface is marked as deprecated
	virtual SDKError ViewShare(unsigned int shareSourceID, SDKViewType type) = 0;

	/// \brief Start sharing with White board.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	///You need to draw your own annotation bar for custom mode when you get the onShareContentNotification with SHARE_TYPE_WB.
	/// \remarks Valid for both ZOOM style and user custom interface mode.
	virtual SDKError StartWhiteBoardShare() = 0;

	/// \brief Start sharing frame.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid for both ZOOM style and user custom interface mode.
	virtual SDKError StartShareFrame() = 0;

	/// \brief Start sharing only the computer audio.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid for both ZOOM style and user custom interface mode.	
	virtual SDKError StartSharePureComputerAudio() = 0;

	/// \brief Start sharing camera.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid for user custom interface mode only.	
	virtual SDKError StartShareCamera(const zchar_t* deviceID, HWND hWnd) = 0;

	/// \brief Display the dialog of sharing configuration.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid only for ZOOM style user interface mode.
	virtual SDKError ShowShareOptionDialog() = 0;
#endif
	
	/// \brief Determine if the specified ADVANCE SHARE OPTION is supported. 
	/// \param option_ The ADVANCE SHARE OPTION to be determined. For more information, see \link AdvanceShareOption \endlink enum.
	/// \return If it is supported, the return value is SDKERR_SUCCESS.
	///Otherwise not. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid for both ZOOM style and user custom interface mode.
	virtual SDKError IsSupportAdvanceShareOption(AdvanceShareOption option_) = 0;
	
	/// \brief Stop the current sharing.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid for both ZOOM style and user custom interface mode.
	virtual SDKError StopShare() = 0;

	/// \brief host / co - host can use this function to lock current meeting share.
	/// \param isLock TRUE means to lock the meeting share, FALSE not.
    /// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \deprecated This interface is marked as deprecated, and is replaced by SetMultiShareSettingOptions(MultiShareOption shareOption).
	virtual SDKError LockShare(bool isLock) = 0;

	/// \brief Pause the current sharing.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid for both ZOOM style and user custom interface mode.
	virtual SDKError PauseCurrentSharing() = 0;

	/// \brief Resume the current sharing.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid for both ZOOM style and user custom interface mode.
	virtual SDKError ResumeCurrentSharing() = 0;

	/// \brief Get the ID of users who are sharing
	/// \return If the function succeeds, the return value is a list of user ID of all users who are sharing.
	///If the function fails, the return value is nullptr.
	/// \remarks Valid for both ZOOM style and user custom interface mode.
	virtual IList<unsigned int>* GetViewableSharingUserList() = 0;

	/// \brief Get the sharing source information list from the specified sharer.
	/// \param userID The ID of the user who is sharing.
	/// \return If the function succeeds, the return value is the viewable sharing information list. For more details, see \link ZoomSDKSharingSourceInfo \endlink structure.
	/// \remarks Valid for both ZOOM style and user custom interface mode. 
	/// For custom interface mode, this interface is only valid after subscribing the sharing content from the specified user by calling ICustomizedShareRender::SetUserID(unsigned int userid) successfully.
	virtual IList<ZoomSDKSharingSourceInfo>* GetSharingSourceInfoList(unsigned int userID) = 0;

	/// \brief Determine if it is able to share. 
	/// \return Enable or disable to start sharing.
	/// \remarks Valid for both ZOOM style and user custom interface mode.
	/// \deprecated This interface is marked as deprecated, and is replaced by CanStartShare(CannotShareReasonType& reason).
	virtual bool CanStartShare() = 0;

	/// \brief Determine whether the current meeting can start sharing. 
	/// \param [out] reason The reason that no one can start sharing. See \link CannotShareReasonType \endlink enum.
	/// \return True indicates you can start sharing.
	virtual bool CanStartShare(CannotShareReasonType& reason) = 0;

	/// \brief Determine if it is able to share desktop in the current meeting.
	/// \return True indicates it is able to share desktop in the current meeting. False not.
	/// \remarks Valid for both ZOOM style and user custom interface mode.
	virtual bool IsDesktopSharingEnabled() = 0;

	/// \brief Determine if the sharing is locked. 
	/// \param bLocked TRUE indicates that the sharing is locked. 
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid for both ZOOM style and user custom interface mode.
	virtual SDKError IsShareLocked(bool& bLocked) = 0;

	/// \brief Determine if the sound of the computer in the current sharing or before share is supported. 
	/// \param [out] bCurEnableOrNot The parameter is valid only when the return value is TRUE. And TRUE indicates to sharing the sound of the computer for the moment.
	/// \return If it is TRUE, the value of bCurEnableOrNot can be used to check whether the computer sound is supported or not when sharing. FALSE not.
	/// \remarks Valid for both ZOOM style and user custom interface mode.
	/// \deprecated This interface is marked as deprecated.
	virtual bool IsSupportEnableShareComputerSound(bool& bCurEnableOrNot) = 0;

	/// \brief Determine whether to optimize the video fluidity when sharing in full screen mode. 
	/// \param bCurEnableOrNot This parameter is valid only when the return value is TRUE. And TRUE indicates to optimize video for the moment. 
	/// \return If it is TRUE, the value of bCurEnableOrNot can be used to check whether to support optimize video fluidity or not. FALSE not.
	/// \remarks Valid for both ZOOM style and user custom interface mode.
	/// \deprecated This interface is marked as deprecated.
	virtual bool IsSupportEnableOptimizeForFullScreenVideoClip(bool& bCurEnableOrNot) = 0;

	/// \brief Determine if the specified share type supports sharing with compute sound or not.
	/// \param type The type of sharing content.
	/// \return True indicates that this is supported.
	virtual bool IsSupportShareWithComputerSound(ShareType type) = 0;

	/// \brief Determine if the current share supports sharing with compute sound or not.
	/// \return True indicates that is supported.
	virtual bool IsCurrentSharingSupportShareWithComputerSound() = 0;

	// \brief Determine if the current meeting enabled sharing with compute sound or not before sharing. 
	/// \return True indicates that this is enabled.
	virtual bool IsEnableShareComputerSoundOn() = 0;

	/// \brief Enable or disable the computer audio before sharing.
	/// \param bEnable TRUE indicates to enable. FALSE not.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks It will be applied when starting share.
	virtual SDKError EnableShareComputerSound(bool bEnable) = 0;

	// \brief Determine if the current sharing content enabled sharing with compute sound or not. 
	/// \return True indicates that this is enabled.
	virtual bool IsEnableShareComputerSoundOnWhenSharing() = 0;

	/// \brief Set to enable or disable the computer audio when sharing.
	/// \param bEnable TRUE indicates to enable. FALSE not.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid for both ZOOM style and user custom interface mode.
	virtual SDKError EnableShareComputerSoundWhenSharing(bool bEnable) = 0;

	/// \brief Set the audio share mode before or during sharing. 
	/// \param mode The mode for audio share, see \link AudioShareMode \endlink enum.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid for both ZOOM style and user custom interface mode.
	virtual SDKError SetAudioShareMode(AudioShareMode mode) = 0;

	/// \brief Get the audio share mode. 
	/// \param mode The mode for audio share, see \link AudioShareMode \endlink enum.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid for both ZOOM style and user custom interface mode.
	virtual SDKError GetAudioShareMode(AudioShareMode& mode) = 0;

	// \brief Determine if the current meeting supports sharing with optimize video or not.
	/// \return True indicates this is supported.
	virtual bool IsSupportEnableOptimizeForFullScreenVideoClip() = 0;

	// \brief Determine if the current meeting enabled sharing with optimize video or not.
	/// \return True indicates this is enabled.
	virtual bool IsEnableOptimizeForFullScreenVideoClipOn() = 0;

	/// \brief Enable or disable the video optimization before sharing. 
	/// \param bEnable TRUE indicates to enable. FALSE not.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks It will be applied when starting share.
	virtual SDKError EnableOptimizeForFullScreenVideoClip(bool bEnable) = 0;

	// \brief Determine if the current sharing content enabled sharing with optimize video or not.
	/// \return True indicates this is enabled.
	virtual bool IsEnableOptimizeForFullScreenVideoClipOnWhenSharing() = 0;

	/// \brief Enable or disable the video optimization when sharing. 
	/// \param bEnable TRUE indicates to enable. FALSE not.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid for both ZOOM style and user custom interface mode.
	virtual SDKError EnableOptimizeForFullScreenVideoClipWhenSharing(bool bEnable) = 0;

	/// \brief Set the options for multi-participants share.
	/// \param [in] shareOption New options for sharing, see \link MultiShareOption \endlink enum.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	virtual SDKError SetMultiShareSettingOptions(MultiShareOption shareOption) = 0;

	/// \brief Get the options for multi-participants share.
	/// \param [out] shareOption Options for sharing, see \link MultiShareOption \endlink enum.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	virtual SDKError GetMultiShareSettingOptions(MultiShareOption& shareOption) = 0;

	/// \brief Determine whether can switch to next camera, when share camera. 
	/// \param [Out] bCan, if bCan is true it means you can switch, else can not.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	virtual SDKError CanSwitchToShareNextCamera(bool& bCan) = 0;

	/// \brief switch to next camera, when you are sharing the camera.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise failed. To get extended error information, see \link SDKError \endlink enum.
	virtual SDKError SwitchToShareNextCamera() = 0;

	/// \brief Determine whether the user can share video files.
	/// \return True indicates that the user can share video files. Otherwise False.
	virtual bool CanShareVideoFile() = 0;

#if defined(WIN32)
	/// \brief Determine whether the user can share to the breakout room.
	/// \return True indicates that the user can share to the breakout room.
	///Otherwise the function fails. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid for user custom interface mode only.	
	virtual SDKError CanEnableShareToBO(bool& bCan) = 0;

	/// \brief Set to enable sharing to the breakout room. 
	/// \param bEnable TRUE indicates to enable. FALSE indicates that sharing to the breakout room is not enabled.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise the function fails. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid for user custom interface mode only.	
	virtual SDKError EnableShareToBO(bool bEnable) = 0;

	/// \brief Determine if sharing to the breakout room is enabled. 
	/// \param bEnabled TRUE indicates that the sharing is locked. 
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise the function fails. To get extended error information, see \link SDKError \endlink enum.
	/// \remarks Valid for user custom interface mode only.	
	virtual SDKError IsShareToBOEnabled(bool& bEnabled) = 0;

	/// \brief Share the video file.
	/// \param filePath Specify the video file path. Only supports mov, mp4, or avi format.
	/// \return If the function succeeds, the return value is SDKERR_SUCCESS.
	///Otherwise the function fails and returns error. To get extended error information, see \link SDKError \endlink enum.
	virtual SDKError StartVideoFileShare(const zchar_t* filePath) = 0;


	/// \brief Determine whether the legal notice for white board is available
	/// \return True indicates the legal notice for white board is available. Otherwise False.
	virtual bool IsWhiteboardLegalNoticeAvailable() = 0;

	/// Get the white board legal notices prompt.
	virtual const zchar_t* getWhiteboardLegalNoticesPrompt() = 0;

	/// Get the white board legal notices explained.
	virtual const zchar_t* getWhiteboardLegalNoticesExplained() = 0;
#endif
};
END_ZOOM_SDK_NAMESPACE
#endif