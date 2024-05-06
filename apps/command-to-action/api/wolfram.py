import urllib.parse
import urllib.request
import json
import os
from gtts import gTTS
import playsound  # This module helps in playing sound files

print("You chose Wolfram Alpha\n")
inp = input('Your question: \n').strip()

def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    playsound.playsound("response.mp3")
    os.remove("response.mp3")  # Deletes the mp3 file after playing it

# Properly encode the URL parameters using urllib.parse.quote_plus
query_params = urllib.parse.urlencode({'i': inp})
url = f'https://api.wolframalpha.com/v1/conversation.jsp?appid=KE5RJ3-K5XP79QU3E&{query_params}'
print("(DEBUG URL:" + url + ")")

# Send request and retrieve response
try:
    with urllib.request.urlopen(url) as response:
        html = response.read()

    parsed_data = json.loads(html)
    if 'error' in parsed_data:
        raise ValueError(parsed_data['error'])

    result = parsed_data.get('result')
    conversation_id = parsed_data.get('conversationID')

    print(result + '\n')
    speak(result)  # Text-to-Speech output of the result

    followup = input("Any followup questions? Type Y if yes, N if no\n").strip().upper()
    while followup == "Y":
        newin = input('Your followup question:\n').strip()

        # Update follow-up query with proper encoding
        followup_params = urllib.parse.urlencode({'i': newin, 'conversationid': conversation_id})
        followup_url = f'https://api.wolframalpha.com/v1/conversation.jsp?appid=KE5RJ3-K5XP79QU3E&{followup_params}'
        print("DEBUG URL FOR FOLLOWUP Q:" + followup_url)

        with urllib.request.urlopen(followup_url) as response:
            html2 = response.read()
        followup_data = json.loads(html2)

        if 'error' in followup_data:
            raise ValueError(followup_data['error'])

        result = followup_data.get('result')
        if result:
            print(result + '\n')
            speak(result)  # Text-to-Speech output of the followup result
        else:
            message = "No result found.\n"
            print(message)
            speak(message)  # Also read aloud when no result is found

        followup = input('Any more questions? Type Y if yes, N if no.\n').strip().upper()

    if followup == "N":
        goodbye_message = "I hope my answers helped you. See you soon :)"
        print(goodbye_message)
        speak(goodbye_message)  # Goodbye message spoken out loud

    print("Okay, BYE.")

except ValueError as e:
    error_message = f"Couldn't find an answer. Please try again.\nError: {str(e)}"
    print(error_message)
    speak(error_message)  # Speaking out the error message
except Exception as e:
    exception_message = f"An error occurred: {str(e)}"
    print(exception_message)
    speak(exception_message)  # Speaking out the exception message
