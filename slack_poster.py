from slack_sdk import WebClient
import certifi
import ssl

def post_to_slack(message):
    user_id = 'UU0BWMHDH'
    slack_token = 'xoxb-2176122839-7352415803520-UsJQSE6wUlBeOYEpB5yth48B'

    ssl_context = ssl.create_default_context(cafile=certifi.where())
    client = WebClient(token=slack_token, ssl=ssl_context)
    response = client.chat_postMessage(
        channel=user_id,
        text=message
    )
    print(response)
