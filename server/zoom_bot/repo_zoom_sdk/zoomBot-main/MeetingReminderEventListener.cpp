#include "MeetingReminderEventListener.h" // Include the header file you've created
#include <stdlib.h>
#include <iostream>

// You might need to include additional headers here if required

// Implement any necessary functions or methods

// This is just a placeholder implementation to show how the header might be used

    MeetingReminderEventListener::MeetingReminderEventListener(){}

     void MeetingReminderEventListener::onReminderNotify(ZOOMSDK::IMeetingReminderContent* content, ZOOMSDK::IMeetingReminderHandler* handle) 
    {
        if (content)
        {
            // Handle the reminder dialog content
            ZOOMSDK::MeetingReminderType type = content->GetType();
            const zchar_t* title = content->GetTitle();
            const zchar_t* dialogContent = content->GetContent();
            bool isBlocking = content->IsBlocking();
            std::cerr << "title :"  << title<< std::endl;
             std::cerr << "dialogContent :"  << dialogContent<< std::endl;
            // You can implement your logic here based on the reminder type, title, content, and whether it's blocking
            
            // For demonstration, let's print the reminder details
          
            // wprintf(L"Reminder Type: %d\n", type);
            // wprintf(L"Title: %ls\n", title);
            // wprintf(L"Content: %ls\n", dialogContent);
            // wprintf(L"Is Blocking: %s\n", isBlocking ? L"Yes" : L"No");
            
            // Handle the reminder actions (ignore, accept, decline) if needed
            if (handle)
            {
                // For demonstration, let's accept the reminder
                handle->Accept();
            }
        }
    }

     void MeetingReminderEventListener::onEnableReminderNotify(IMeetingReminderContent* content, IMeetingEnableReminderHandler* handle)
     {
     }
