from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def get_user_id_by_email(email, slack_token):
    client = WebClient(token=slack_token)

    try:
        response = client.users_list()
        users = response['members']
        for user in users:
            if user['profile']['email'] == email:
                return user['id']
        return None
    except SlackApiError as e:
        print(f"Error fetching users: {e.response['error']}")
        return None

if __name__ == "__main__":
    slack_token = 'xoxb-2176122839-7352415803520-UsJQSE6wUlBeOYEpB5yth48B'
    email = 'jaguilar@ancestry.com'
    user_id = get_user_id_by_email(email, slack_token)
    print(f"User ID: {user_id}")
