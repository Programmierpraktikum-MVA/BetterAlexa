//GetVideoRawData

#include "rawdata/rawdata_video_source_helper_interface.h"
#include "ZoomSDKRenderer.h"
#include "zoom_sdk_def.h" 
#include <iostream>


#include <fstream>
#include <cstring>
#include <string>
#include <cstdlib>
#include <cstdint>
#include <cstdio>




void ZoomSDKRenderer::onRawDataFrameReceived(YUVRawDataI420* data)
{
	std::cout << "onRawDataFrameReceived." << std::endl;

	std::cout << "width." << data->GetStreamWidth() << std::endl;
	std::cout << "height." << data->GetStreamHeight() << std::endl;
	//std::cout << "sourceID." << data->GetSourceID() << std::endl;

	if (data->GetStreamHeight() == 720) {
		SaveToRawYUVFile(data);
	}


}
void ZoomSDKRenderer::onRawDataStatusChanged(RawDataStatus status)
{
	std::cout << "onRawDataStatusChanged." << std::endl;
}

void ZoomSDKRenderer::onRendererBeDestroyed()
{
	std::cout << "onRendererBeDestroyed ." << std::endl;
}

void ZoomSDKRenderer::SaveToRawYUVFile(YUVRawDataI420* data) {

	//method 1

	//// Open the file for writing
	//std::ofstream outputFile("output.yuv", std::ios::out | std::ios::binary | std::ios::app);
	//if (!outputFile.is_open())
	//{
	//	//error opening file
	//	return;
	//}


	//char* _data = new char[data->GetStreamHeight() * data->GetStreamWidth() * 3 / 2];

	//memset(_data, 0, data->GetStreamHeight() * data->GetStreamWidth() * 3 / 2);

	//// Copy Y buffer
	//memcpy(_data, data->GetYBuffer(), data->GetStreamHeight() * data->GetStreamWidth());

	//// Copy U buffer
	//size_t loc = data->GetStreamHeight() * data->GetStreamWidth();
	//memcpy(&_data[loc], data->GetUBuffer(), data->GetStreamHeight() * data->GetStreamWidth() / 4);


	//// Copy V buffer
	//loc = (data->GetStreamHeight() * data->GetStreamWidth()) + (data->GetStreamHeight() * data->GetStreamWidth() / 4);
	//memcpy(&_data[loc], data->GetVBuffer(), data->GetStreamHeight() * data->GetStreamWidth() / 4);



	////outputFile.write((char*)data->GetBuffer(), data->GetBufferLen());
	//// Write the Y plane
	//outputFile.write(_data, data->GetStreamHeight() * data->GetStreamWidth() * 3 / 2);


	//// Close the file
	//outputFile.close();
	//outputFile.flush();
	////cout << "YUV420 buffer saved to file." << endl;
	//std::cout << "Saving Raw Data" << std::endl;


	//method 2

	// Open the file for writing
	std::ofstream outputFile("output.yuv", std::ios::out | std::ios::binary | std::ios::app);
	if (!outputFile.is_open())
	{
		std::cout << "Error opening file." << std::endl;
		return;
	}
	// Calculate the sizes for Y, U, and V components
	size_t ySize = data->GetStreamWidth() * data->GetStreamHeight();
	size_t uvSize = ySize / 4;



	// Write Y, U, and V components to the output file
	outputFile.write(data->GetYBuffer(), ySize);
	outputFile.write(data->GetUBuffer(), uvSize);
	outputFile.write(data->GetVBuffer(), uvSize);


	// Close the file
	outputFile.close();
	outputFile.flush();
	//cout << "YUV420 buffer saved to file." << endl;




}

