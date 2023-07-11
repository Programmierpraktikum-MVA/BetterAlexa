#tutorial Using Python Requests to Retrieve/Scrape Discord Messages (Discord Token): https://www.youtube.com/watch?v=xh28F6f-Cds&ab_channel=Codium

import requests
import json

#retrieving last messages the amount of last messages from all three chats is defined in the variable "limit"
#to retrieve only unread messages a bot is required  #i do not have enough time to learn the bot api
json_list = []

def retrieve_discord_messages(channelId,limit):
    headers = {
        'Authorization' : "MTEyODMyNjkzODgzNTAyNjA1MQ.GwooDd.fn_ulqVJLVx3U-_T2Ojv4rwoO4Enj56t8n02vs"
    }

    r = requests.get(f"https://discord.com/api/v9/channels/{channelId}/messages?limit={limit}", headers=headers)
    jsonn = json.loads(r.text)
    for value in jsonn:
        if not value["content"]:
            continue 
        print(value["content"])
        json_list.append(value["content"])


channel_ids = []

channel_id_allgemein = 1128327363416035343
channel_id_meeting_plaene = 1128327363416035344
channel_id_user_eduard = 1128328166944014468

def append_id(channel_id):
    channel_ids.append(channel_id)

def remove_id(channel_id):
    channel_ids.remove(channel_id)
append_id(channel_id_allgemein)
append_id(channel_id_meeting_plaene)
append_id(channel_id_user_eduard)

def retrieve_all_discord_messages(limit): #limit gives the max number of messages
    for channel_id in channel_ids:
        retrieve_discord_messages(channel_id,limit)
    #result = json.dumps(json_list)    # to send to speach to text module
    #return result
    return json_list

