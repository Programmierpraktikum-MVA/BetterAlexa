//GetVideoRawData

#include "rawdata/rawdata_video_source_helper_interface.h"
#include "rawdata/rawdata_renderer_interface.h"
#include "zoom_sdk.h"
#include "zoom_sdk_raw_data_def.h"

USING_ZOOM_SDK_NAMESPACE

class ZoomSDKRenderer :
	public IZoomSDKRendererDelegate
{
public:
	virtual void onRawDataFrameReceived(YUVRawDataI420* data);
	virtual void onRawDataStatusChanged(RawDataStatus	status);

	virtual void onRendererBeDestroyed();

	virtual void SaveToRawYUVFile(YUVRawDataI420* data);
};