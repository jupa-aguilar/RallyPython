from slack_sdk import WebClient
import certifi
import ssl

def post_to_slack(user_id, message, slack_token):
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    client = WebClient(token=slack_token, ssl=ssl_context)
    response = client.chat_postMessage(
        channel=user_id,
        text=message
    )
    print(response)

message = """
*L1 Deployment plan for this Thursday*
<https://example.com/US297794|US297794>: [06-13-2024] Overarching L1 Deployment Salesforce Release
*Checklist*: <https://example.com/checklist|06-13-2024 Deployment Checklist>
*PR*: Sprint_12_2024_06_13 (TBD)
*PAAP*: TBD

*Stories Ready*
● Planned
  ○ <https://example.com/US290690|US290690>: [L1 DEPLOY] Upsell - Currency Picklist
  ○ <https://example.com/US296010|US296010>: [L1 DEPLOY] DNA Tool Dates Update
  ○ <https://example.com/US294920|US294920>: [L1 DEPLOY] Remove Phone Number Pop-up Window (DEPLOYED ON Sprint 11 2024 05 23)

*next steps*:
(0) - make sure all stories ready to deploy are listed on the checklist
(1) - deploy to preprod: regression testing
(2) - validate checklist
(3) - deploy to preprod: test after roll-forward
(4) - file PAAP ticket
(5) - deploy to production: test after roll-forward
"""

user_id = 'UU0BWMHDH'
slack_token = 'xoxb-2176122839-7352415803520-UsJQSE6wUlBeOYEpB5yth48B'

post_to_slack(user_id, message, slack_token)
