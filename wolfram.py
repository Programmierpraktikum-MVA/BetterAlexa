import urllib.parse
import urllib.request
import json

wolfram_conv_id = None

def ask_wolfram_question(question):
    global wolfram_conv_id
    if wolfram_conv_id is None:
        answer, id = ask_wolfram_start(question)
        wolfram_conv_id = id
    else:
        answer = ask_wolfram_followup(question, wolfram_conv_id)
    return answer

def ask_wolfram_start(question):
    # Properly encode the URL parameters using urllib.parse.quote_plus
    query_params = urllib.parse.urlencode({'i': question})
    url = f'https://api.wolframalpha.com/v1/conversation.jsp?appid=KE5RJ3-K5XP79QU3E&{query_params}'
    #print("(DEBUG URL: " + url + ")")  # Debug output of the URL

    # Send request and retrieve response
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read()

        parsed_data = json.loads(html)
        if 'error' in parsed_data:
            raise ValueError(parsed_data['error'])

        result = parsed_data.get('result')
        conversation_id = parsed_data.get('conversationID')
        return result, conversation_id
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return error_message, -1


def ask_wolfram_followup(followup_question, conversation_id):
    # Update follow-up query with proper encoding
    followup_params = urllib.parse.urlencode({'i': followup_question, 'conversationid': conversation_id})
    followup_url = f'https://api.wolframalpha.com/v1/conversation.jsp?appid=KE5RJ3-K5XP79QU3E&{followup_params}'
    #print("DEBUG URL FOR FOLLOWUP Q: " + followup_url)

    try:
        with urllib.request.urlopen(followup_url) as response:
            html2 = response.read()
        followup_data = json.loads(html2)

        if 'error' in followup_data:
            raise ValueError(followup_data['error'])

        result = followup_data.get('result')
        if not result:
            result = "No result found.\n"
        return result
    except Exception as e:
        exception_message = f"An error occurred: {str(e)}"
        return exception_message


# Example usage
if __name__ == "__main__":
    print("You chose Wolfram Alpha\n")
    inp = input('Your question: \n').strip()
    answer, conv_id = ask_wolfram_question(inp)
    if conv_id:
        followup = input("Any followup questions? Type Y if yes, N if no\n").strip().upper()
        while followup == "Y":
            new_in = input('Your followup question:\n').strip()
            ask_wolfram_followup(new_in, conv_id)
            followup = input('Any more questions? Type Y if yes, N if no.\n').strip().upper()
        if followup == "N":
            goodbye_message = "I hope my answers helped you. See you soon :)"
            print(goodbye_message)
