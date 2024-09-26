import ssl
from pyral import Rally
from datetime import datetime, timedelta
from slack_poster import post_to_slack
 
# Disable SSL verification (for testing only)
ssl._create_default_https_context = ssl._create_unverified_context
 
# Get API key from user input
API_KEY = input("Please enter your Rally API Key: ")
 
# Function to prompt for ticket IDs
def get_ticket_ids():
    ticket_ids = []
    mode = input("Would you like to enter ticket IDs as a comma-separated list or one by one? (Enter 'list' or 'one by one'): ").strip().lower()
 
    if mode == 'list':
        ticket_ids_input = input("Enter the ticket IDs as a comma-separated list: ")
        ticket_ids = [ticket.strip() for ticket in ticket_ids_input.split(',')]
    elif mode == 'one by one':
        print("Enter the ticket IDs one by one. Type 'done' when you are finished:")
        while True:
            ticket_id = input("Enter ticket ID (or 'done' to finish): ").strip()
            if ticket_id.lower() == 'done':
                break
            ticket_ids.append(ticket_id)
    else:
        print("Invalid input. Please start again.")
        return get_ticket_ids()
 
    return ticket_ids
 
# Get the ticket IDs from user input
ticket_ids = get_ticket_ids()
 
# Rally connection configuration
RALLY_SERVER = 'rally1.rallydev.com'
WORKSPACE = 'Main'
PROJECT_NAME = 'Customer-Support-Tech'
EPIC_FORMATTED_ID = 'EPIC-32254'
STORY_TYPE = 'Operations Product Support'
PLAN_ESTIMATE = 2
 
# Function to get the next Thursday
def get_next_thursday():
    today = datetime.now()
    days_until_thursday = (3 - today.weekday() + 7) % 7
    next_thursday = today + timedelta(days=days_until_thursday)
    return next_thursday
 
def get_next_monday():
    today = datetime.now()
    days_until_monday = (7 - today.weekday()) % 7
    next_monday = today + timedelta(days=days_until_monday)
    return next_monday
 
def get_specific_day(requested_day):
    days_of_week = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }
 
    today = datetime.now()
    requested_day = requested_day.lower()
 
    if requested_day not in days_of_week:
        raise ValueError("Invalid day requested. Use: monday, tuesday, wednesday, thursday, friday, saturday, or sunday.")
     
    current_day = today.weekday()
    days_until_requested_day = (days_of_week[requested_day] - current_day + 7) % 7
    specific_day = today + timedelta(days=days_until_requested_day)
 
    return specific_day
 
# Function to get ticket details from Rally
def get_ticket_details(rally, ticket_ids):
    ticket_details = []
    for ticket_id in ticket_ids:
        ticket = rally.get('HierarchicalRequirement', query=f'FormattedID = "{ticket_id}"', instance=True)
        if ticket:
            ticket_details.append({
                'id': ticket.FormattedID,
                'name': ticket.Name,
                'url': f'https://rally1.rallydev.com/#/detail/userstory/{ticket.ObjectID}'
            })
    return ticket_details
 
# Configurable date
# date = get_next_thursday()
# Get the next Wednesday
date = get_specific_day("wednesday")
date_str = date.strftime("%m-%d-%Y")
 
# Function to get the name of the Release and the Iteration
def get_release_iteration(date):
    year = date.year
    quarter = (date.month - 1) // 3 + 1
    release = f"PI-{year}_Q{quarter}"
 
    # Find the corresponding iteration
    iteration_end_dates = {
        "Sprint_11_2024": datetime(2024, 6, 4),
        "Sprint_12_2024": datetime(2024, 6, 18),
        "Sprint_13_2024": datetime(2024, 7, 2),
        "Sprint_14_2024": datetime(2024, 7, 16),
        "Sprint_15_2024": datetime(2024, 7, 30),
        "Sprint_16_2024": datetime(2024, 8, 13),
        "Sprint_17_2024": datetime(2024, 8, 27),
        "Sprint_18_2024": datetime(2024, 9, 10),
        "Sprint_19_2024": datetime(2024, 9, 24),
        "Sprint_20_2024": datetime(2024, 10, 8),
        "Sprint_21_2024": datetime(2024, 10, 22),
        "Sprint_22_2024": datetime(2024, 11, 5),
        "Sprint_23_2024": datetime(2024, 11, 19),
        # Add more iterations here
    }
 
    iteration = min(iteration_end_dates, key=lambda k: abs(iteration_end_dates[k] - date))
 
    return release, iteration
 
# Get current Release and Iteration based on the date
release_name, iteration_name = get_release_iteration(date)
print(f"Release Name: {release_name}")
print(f"Iteration Name: {iteration_name}")
 
# Primary user's email
USER_EMAIL = 'jaguilar@ancestry.com'
 
# Additional user 1's email (configurable)
ADDITIONAL_USER_EMAIL_1 = 'AArias@ancestry.com'
 
# Additional user 2's email (configurable)
ADDITIONAL_USER_EMAIL_2 = 'slevita.contractor@ancestry.com'
 
# PAAP value (configurable)
paap_value = "TBD"
 
# Configuration of names and descriptions
user_story_1_name = f"[{date_str}] L1 Deployment Salesforce Release"
user_story_2_name = f"[{date_str}] Overarching L1 Deployment Salesforce Release"
description_1 = f"""
DEV:<br>
[{date_str}] Overarching L1 Deployment Salesforce Release<br><br>
QA:<br>
[QA-regression-{date_str}] PreProd regression<br>
[QA-regression-{date_str}] PreProd rollback<br>
[QA-regression-{date_str}] Production roll forward
"""
 
# Names of the three additional user stories
additional_story_names = [
    f"[QA-regression-{date_str}] PreProd regression",
    f"[QA-regression-{date_str}] PreProd rollback",
    f"[QA-regression-{date_str}] Production roll forward"
]
 
# Function to get a reference from Rally
def get_reference(rally, type, fetch, query, order=""):
    response = rally.get(type, fetch=fetch, query=query, order=order)
    for item in response:
        return item
    return None
 
# Authentication in Rally
try:
    rally = Rally(server=RALLY_SERVER, apikey=API_KEY, workspace=WORKSPACE)
    print("Successfully connected to Rally.")
except Exception as e:
    print(f"Error connecting to Rally: {e}")
    exit(1)
 
# Get the details of the tickets
ticket_details = get_ticket_details(rally, ticket_ids)
 
description_2_template = f"""
<b>Salesforce</b><br>
{date_str} Deployment Checklist<br><br>
<b>Stories Ready</b><br><br>
<b>Planned</b><br>
<ul>
"""
 
for ticket in ticket_details:
    description_2_template += f'<li><a href="{ticket["url"]}">{ticket["id"]}</a>: {ticket["name"]}</li>\n'
 
# Add the PAAP table and the pre-deployment and post-deployment steps
description_2_template += f"""
</ul>
<table border="1" cellpadding="5" cellspacing="0">
    <tr>
        <th>PAAP</th>
        <td>{paap_value}</td>
    </tr>
</table>
<b>Pre-Deployment Steps</b><br>
<ul>
    <li>Step 1</li>
    <li>Step 2</li>
</ul>
<b>Post-Deployment Steps</b><br>
<ul>
    <li>Step 1</li>
    <li>Step 2</li>
</ul>
"""
 
# Get Project reference
project = get_reference(rally, 'Project', "ObjectID,Name", f'Name = "{PROJECT_NAME}"')
if not project:
    print(f"Error: Project {PROJECT_NAME} not found.")
    exit(1)
project_ref = project._ref
print(f"Project Ref: {project_ref}")
 
# Get Epic reference
epic = get_reference(rally, 'PortfolioItem/EPIC', "ObjectID,FormattedID,Name,Project", f'FormattedID = "{EPIC_FORMATTED_ID}"')
if not epic:
    print(f"Error: Epic with FormattedID {EPIC_FORMATTED_ID} not found.")
    exit(1)
epic_ref = epic._ref
print(f"Epic Ref: {epic_ref}")
 
# Get current Release reference
release = get_reference(rally, 'Release', "ObjectID,Name", f'Project.Name = "{PROJECT_NAME}" and Name = "{release_name}"')
if not release:
    print(f"Error: No current Release found with name {release_name} for project {PROJECT_NAME}.")
    exit(1)
release_ref = release._ref
print(f"Release Ref: {release_ref}")
 
# Get current Iteration reference
iteration = get_reference(rally, 'Iteration', "ObjectID,Name", f'Project.Name = "{PROJECT_NAME}" and Name = "{iteration_name}"')
if not iteration:
    print(f"Error: No current Iteration found with name {iteration_name} for project {PROJECT_NAME}.")
    exit(1)
iteration_ref = iteration._ref
print(f"Iteration Ref: {iteration_ref}")
 
# Get main user's reference
try:
    user_response = rally.get('User', fetch="ObjectID,UserName,EmailAddress", query=f'EmailAddress = "{USER_EMAIL}"')
    user = next(user_response)
    user_ref = user._ref
    print(f"Owner Ref: {user_ref}, UserName: {user.UserName}")
except StopIteration:
    print(f"Error: User with EmailAddress = {USER_EMAIL} not found.")
    exit(1)
except Exception as e:
    print(f"Error getting User ID: {e}")
    exit(1)
 
# Get additional user 1's reference
try:
    additional_user_response_1 = rally.get('User', fetch="ObjectID,UserName,EmailAddress", query=f'EmailAddress = "{ADDITIONAL_USER_EMAIL_1}"')
    additional_user_1 = next(additional_user_response_1)
    additional_user_ref_1 = additional_user_1._ref
    print(f"Additional Owner Ref 1: {additional_user_ref_1}, UserName: {additional_user_1.UserName}")
except StopIteration:
    print(f"Error: User with EmailAddress = {ADDITIONAL_USER_EMAIL_1} not found.")
    exit(1)
except Exception as e:
    print(f"Error getting additional User ID 1: {e}")
    exit(1)
 
# Get additional user 2's reference
try:
    additional_user_response_2 = rally.get('User', fetch="ObjectID,UserName,EmailAddress", query=f'EmailAddress = "{ADDITIONAL_USER_EMAIL_2}"')
    additional_user_2 = next(additional_user_response_2)
    additional_user_ref_2 = additional_user_2._ref
    print(f"Additional Owner Ref 2: {additional_user_ref_2}, UserName: {additional_user_2.UserName}")
except StopIteration:
    print(f"Error: User with EmailAddress = {ADDITIONAL_USER_EMAIL_2} not found.")
    exit(1)
except Exception as e:
    print(f"Error getting additional User ID 2: {e}")
    exit(1)
 
# Create the first User Story with Release and Iteration as Unscheduled
user_story_1_data = {
    'Name': user_story_1_name,
    'Description': description_1,  # Specific description for the first User Story
    'Project': project_ref,
    'PortfolioItem': epic_ref,  # Use PortfolioItem instead of Parent
    'PlanEstimate': PLAN_ESTIMATE,
    'c_StoryType': STORY_TYPE,
    'Owner': user_ref  # Assign to your user
    # Do not include 'Release' or 'Iteration' to make it Unscheduled
}
 
try:
    user_story_1 = rally.put('HierarchicalRequirement', user_story_1_data)
    if user_story_1:
        print(f"First User Story created with ID: {user_story_1.ObjectID}")
        # Construct the URL for the User Story
        user_story_1_url = f'https://rally1.rallydev.com/#/detail/userstory/{user_story_1.ObjectID}'
    else:
        print("Error: Could not create the first User Story.")
        exit(1)
except Exception as e:
    print(f"Error creating the first User Story: {e}")
    exit(1)
 
# Create the second User Story with dependency on the first one
user_story_2_data = {
    'Name': user_story_2_name,
    'Description': description_2_template.format(story_1_id=user_story_1.ObjectID, story_2_id='placeholder', story_3_id='placeholder'),
    'Project': project_ref,
    'PortfolioItem': epic_ref,  # Use PortfolioItem instead of Parent
    'Release': release_ref,
    'Iteration': iteration_ref,
    'PlanEstimate': PLAN_ESTIMATE,
    'c_StoryType': STORY_TYPE,
    'Owner': user_ref,  # Assign to your user
    'Predecessors': [user_story_1._ref]  # Use the correct reference
}
 
try:
    user_story_2 = rally.put('HierarchicalRequirement', user_story_2_data)
    if user_story_2:
        print(f"Second User Story created with ID: {user_story_2.ObjectID}")
    else:
        print("Error: Could not create the second User Story.")
except Exception as e:
    print(f"Error creating the second User Story: {e}")
 
# Update the description of the second story with the correct ID
description_2 = description_2_template.format(story_1_id=user_story_1.ObjectID, story_2_id=user_story_2.ObjectID, story_3_id='placeholder')
user_story_2_data_update = {
    'Description': description_2
}
 
try:
    rally.update('HierarchicalRequirement', user_story_2.ObjectID, user_story_2_data_update)
    print("Second User Story description updated.")
except Exception as e:
    print(f"Error updating the description of the second User Story: {e}")
 
# Create the three additional User Stories for user 1
for story_name in additional_story_names:
    additional_story_data = {
        'Name': story_name,
        'Description': "",  # Empty description
        'Project': project_ref,
        'PortfolioItem': epic_ref,  # Use PortfolioItem instead of Parent
        'Release': release_ref,
        'Iteration': iteration_ref,
        'PlanEstimate': PLAN_ESTIMATE,
        'c_StoryType': STORY_TYPE,
        'Owner': additional_user_ref_1,  # Assign to additional user 1
        'Predecessors': [user_story_1._ref]  # Dependency on the first User Story
    }
    try:
        additional_story = rally.put('HierarchicalRequirement', additional_story_data)
        if additional_story:
            print(f"Additional User Story created with ID: {additional_story.ObjectID}")
        else:
            print(f"Error: Could not create the User Story {story_name}.")
    except Exception as e:
        print(f"Error creating the User Story {story_name}: {e}")
 
# Create the three additional User Stories for user 2
for story_name in additional_story_names:
    additional_story_data = {
        'Name': story_name,
        'Description': "",  # Empty description
        'Project': project_ref,
        'PortfolioItem': epic_ref,  # Use PortfolioItem instead of Parent
        'Release': release_ref,
        'Iteration': iteration_ref,
        'PlanEstimate': PLAN_ESTIMATE,
        'c_StoryType': STORY_TYPE,
        'Owner': additional_user_ref_2,  # Assign to additional user 2
        'Predecessors': [user_story_1._ref]  # Dependency on the first User Story
    }
    try:
        additional_story = rally.put('HierarchicalRequirement', additional_story_data)
        if additional_story:
            print(f"Additional User Story created with ID: {additional_story.ObjectID}")
        else:
            print(f"Error: Could not create the User Story {story_name}.")
    except Exception as e:
        print(f"Error creating the User Story {story_name}: {e}")
 
# Message to post on Slack
 
# Format the list of tickets
planned_tickets = ""
for ticket in ticket_details:
    formatted_ticket = f'<{ticket["url"]}|{ticket["id"]}>: {ticket["name"]}'
    planned_tickets += f"  - {formatted_ticket}\n"
 
# Create the complete message
# Now replace the placeholder in the message with the actual URL
message = f"""
*L1 Deployment plan for this Thursday*
<{user_story_1_url}|{user_story_1.FormattedID}>: [{date_str}] Overarching L1 Deployment Salesforce Release
*Checklist*: <https://example.com/checklist|{date_str} Deployment Checklist>
*PR*: {iteration_name}_{date.month}_{date.day} (TBD)
*PAAP*: TBD
 
*Stories Ready*
*Planned*
{planned_tickets}
*next steps*:
  1. make sure all stories ready to deploy are listed on the checklist
  2. deploy to preprod: regression testing
  3. validate checklist
  4. deploy to preprod: test after roll-forward
  5. file PAAP ticket
  6. deploy to production: test after roll-forward
"""
 
# Call the function to post the message
post_to_slack(message)