import requests
import time
import argparse
from argparse import RawTextHelpFormatter
import sys

'''
	get message history
    https://api.slack.com/methods/conversations.history
	curl -X GET -H 'Authorization: Bearer YOUR_USER_OR_BOT_API_TOKEN' 'https://slack.com/api/conversations.history?channel=DM_CHANNEL_ID&cursor=NEXT_CURSOR_VALUE'
	
    -----------------------------------------------------------------------------
    
    delete message 
    https://api.slack.com/methods/chat.delete
	curl -X POST -H 'Authorization: Bearer YOUR_USER_OR_BOT_API_TOKEN' -H 'Content-type: application/json' -d '{"channel": "$channel", "ts": "$ts"}' https://slack.com/api/chat.delete
    
	'''
 
 # Create the parser
parser = argparse.ArgumentParser(description='Delete Slack messages from a specified channel.\n'
                                 'Example:\n   python3 main.py -u xoxp-xxxxxxx -m U0xxxxxxx -c D0xxxxxxx',formatter_class=RawTextHelpFormatter)

# Add the arguments
parser.add_argument('-u', '--user_token', type=str, required=True, help='User OAuth token starting with "xoxp-"')
parser.add_argument('-b', '--bot_token', type=str, required=False, default='', help='Bot user OAuth token starting with "xoxb-"')
parser.add_argument('-m', '--my_user_id', type=str, required=True, help='Your Slack user ID')
parser.add_argument('-o', '--other_user_id', type=str, default='',help='Other Slack user ID whose messages you want to delete')
parser.add_argument('-c', '--channel_id', type=str, required=True, help='Channel ID where messages will be deleted')
# Check if no arguments were provided
if len(sys.argv) <= 1:
    parser.print_help(sys.stderr)
    sys.exit(1)
    
args = parser.parse_args()
USER_TOKEN = args.user_token
BOT_TOKEN = args.bot_token
MY_USER_ID = args.my_user_id
OTHER_USER_ID = args.other_user_id
CHANNEL_WITH_OTHER_ID = args.channel_id
NEXT_CURSOR_VALUE = ""
    
conversation_history_url = 'https://slack.com/api/conversations.history?channel=%s' % CHANNEL_WITH_OTHER_ID
chat_delete_url = 'https://slack.com/api/chat.delete'
deleted_stat = {"deleted": 0,"failed": 0, "http_error": 0}

# Making a GET request with a token in the header
headers = {'Authorization': f'Bearer {USER_TOKEN}','Content-type': 'application/json'}
'''
    This code defines a function called delete_message that takes in a list of messages as input. 
    It iterates over each message in the list and checks if the user of the message matches a global variable called MY_USER_ID. 
    If it does, it prints the text of the message and sends a POST request to a specified URL (chat_delete_url) with the channel ID and timestamp of the message to delete it. 
    The response from the request is checked for success and the appropriate counters are incremented. 
    Finally, there is a 1-second delay between each message deletion.

    Deletes the specified messages from the chat.

    Parameters:
        messages (list): A list of messages to be deleted.

    Returns:
        None
'''
def	delete_message(messages):
    global MY_USER_ID,CHANNEL_WITH_OTHER_ID,chat_delete_url,deleted_stat
    for m in messages:
        if m.get('user') == MY_USER_ID:
            print(m.get('text'))
            resp = requests.post(chat_delete_url, json={'channel': CHANNEL_WITH_OTHER_ID, 'ts': m.get('ts')}, headers=headers)
            if resp.status_code == 200:
                if resp.json().get('ok') == True:
                    deleted_stat["deleted"] += 1
                else:
                    deleted_stat["failed"] += 1
                print(resp.json())
            else:
                deleted_stat["http_error"] += 1
                print(resp.text)
            time.sleep(1)

    
'''
    This code defines a function called get_messages that retrieves messages from a conversation history using a given cursor.
    It makes a GET request to the conversation_history_url with a parameter cursor to paginate through the messages.
    If the response status code is 200, it checks if there are any messages in the response. 
    If there are, it calls the delete_message function to delete those messages and recursively calls get_messages with the next cursor for pagination.
    If the response status code is not 200, it prints an error message.
    Retrieves messages from the conversation history using the provided cursor.

    Parameters:
        cursor (str): A string representing the cursor for pagination.

    Returns:
        None

    Raises:
        None
'''
def get_messages(cursor):
    global conversation_history_url
    time.sleep(1)
    response = requests.get("%s%s" % (conversation_history_url, '' if cursor == '' else '&cursor=%s' % cursor), headers=headers)
    if response.status_code == 200:
        if len(response.json().get('messages')) > 0:
            delete_message(response.json().get('messages'))
            get_messages(response.json().get('response_metadata').get('next_cursor'))
    else:
        print(f"Failed to retrieve data: {response.status_code}")

get_messages('')
print("Result: Deleted Message Count: %d, Failed Message Count: %d, HTTP Error Count: %d" % (deleted_stat["deleted"], deleted_stat["failed"], deleted_stat["http_error"]))
