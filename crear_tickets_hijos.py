import ssl
from pyral import Rally

# Disable SSL verification (for testing purposes only)
ssl._create_default_https_context = ssl._create_unverified_context

# Interactive input for the script configuration
API_KEY = input("Enter your Rally API Key: ")
TICKET_PARENT_ID = input("Enter the Parent Ticket ID: ")

# Function to display and get QA Owner selection
def select_qa_owner():
    print("Select the QA Owner Email:")
    print("1 - Alfredo Arias > email = AArias@ancestry.com")
    print("2 - Santorino Levita > email = slevita.contractor@ancestry.com")
    print("3 - Maitrey Patel > email = mpatel@ancestry.com")
    print("0 - None (leave blank)")

    while True:
        selection = input("Enter the number corresponding to the QA Owner: ").strip()
        if selection == '1':
            return 'AArias@ancestry.com'
        elif selection == '2':
            return 'slevita.contractor@ancestry.com'
        elif selection == '3':
            return 'mpatel@ancestry.com'
        elif selection == '0':
            return ''
        else:
            print("Invalid selection, please choose a valid option.")

# Get the QA Owner Email based on user selection
QA_OWNER_EMAIL = select_qa_owner()

# Convert input to boolean
create_l1_deploy_ticket = input("Create L1 DEPLOY ticket? (yes/no): ").strip().lower() == 'yes'

# Rally connection configuration
RALLY_SERVER = 'rally1.rallydev.com'
WORKSPACE = 'Main'
PROJECT_NAME = 'Customer-Support-Tech'

# Function to get a Rally reference
def get_reference(rally, type, fetch, query):
    response = rally.get(type, fetch=fetch, query=query)
    for item in response:
        return item
    return None

# Function to create a tag
def create_tag(rally, tag_name):
    tag_data = {'Name': tag_name}
    tag = rally.put('Tag', tag_data)
    return tag

# Authentication in Rally
try:
    rally = Rally(server=RALLY_SERVER, apikey=API_KEY, workspace=WORKSPACE)
    print("Successfully connected to Rally.")
except Exception as e:
    print(f"Error connecting to Rally with the provided API Key: {e}")
    exit(1)

# Get Project reference
project = get_reference(rally, 'Project', "ObjectID,Name", f'Name = "{PROJECT_NAME}"')
if not project:
    print(f"Error: Project {PROJECT_NAME} not found")
    exit(1)
project_ref = project._ref
print(f"Project Ref: {project_ref}")

# Validate Parent Ticket ID
parent_ticket = get_reference(rally, 'HierarchicalRequirement', "ObjectID,Name,PlanEstimate,Release,Iteration,Owner,Description", f'FormattedID = "{TICKET_PARENT_ID}"')
if not parent_ticket:
    print(f"Error: Parent ticket with ID {TICKET_PARENT_ID} not found")
    exit(1)

# Handle possible absence of the 'c_Color' field
color_parent = getattr(parent_ticket, 'c_Color', None)

parent_ticket_ref = parent_ticket._ref
parent_ticket_name = parent_ticket.Name
plan_estimate_parent = parent_ticket.PlanEstimate
release_ref = parent_ticket.Release._ref if parent_ticket.Release else None
iteration_ref = parent_ticket.Iteration._ref if parent_ticket.Iteration else None
owner_ref = parent_ticket.Owner._ref if parent_ticket.Owner else None
description_parent = parent_ticket.Description

print(f"Parent Ticket Ref: {parent_ticket_ref}, Name: {parent_ticket_name}")

# Validate QA Owner Email (if provided)
qa_user_ref = None 
if QA_OWNER_EMAIL:
    try:
        qa_user_response = rally.get('User', fetch="ObjectID,UserName,EmailAddress", query=f'EmailAddress = "{QA_OWNER_EMAIL}"')
        qa_user = next(qa_user_response)
        qa_user_ref = qa_user._ref
        print(f"QA Owner Ref: {qa_user_ref}, UserName: {qa_user.UserName}")
    except StopIteration:
        print(f"Error: User with EmailAddress = {QA_OWNER_EMAIL} not found")
        exit(1)
    except Exception as e:
        print(f"Error obtaining QA User ID: {e}")
        exit(1)

# Proceed only if both the Parent Ticket ID and QA Owner Email (if provided) are valid# Create 'L1 Deploy' tag only if the L1 DEPLOY ticket is to be created
if create_l1_deploy_ticket:
    try:
        tag = create_tag(rally, 'L1 Deploy')
        tag_ref = tag._ref
        print(f"'L1 Deploy' tag created with Ref: {tag_ref}")
    except Exception as e:
        print(f"Error creating 'L1 Deploy' tag: {e}")
        exit(1)

# Create the three child tickets
child_tickets = {
    'DEV': None,
    'QA': None,
    'L1 DEPLOY': None
}

# Adjust PlanEstimate for the DEV child if the parent's is not set
plan_estimate_dev = plan_estimate_parent if plan_estimate_parent is not None else None

# Prepare ticket data
ticket_data = {
    'DEV': {
        'PlanEstimate': plan_estimate_dev,
        'Release': release_ref,
        'Iteration': iteration_ref,
        'Owner': owner_ref,
        'c_Color': color_parent,
        'Description': description_parent
    },
    'QA': {
        'Release': release_ref,
        'Iteration': iteration_ref,
        'Owner': qa_user_ref if qa_user_ref else None,
        'c_Color': color_parent,
        'Description': description_parent
    },
    'L1 DEPLOY': {
        'PlanEstimate': 1,
        'Owner': owner_ref,
        'Tags': [{"_ref": tag_ref}] if create_l1_deploy_ticket else None,
        'c_Color': color_parent,
        'Description': "PRE-DEPLOYMENT STEPS\n•\n\nPOST-DEPLOYMENT STEPS\n•"
    }
}

def create_child_ticket(type, name, parent_ticket_ref, additional_data):
    ticket_data = {
        'Name': name,
        'Project': project_ref,
        'Parent': parent_ticket_ref
    }
    ticket_data.update(additional_data)
    if'c_Color'in ticket_data and ticket_data['c_Color'] is None:
        del ticket_data['c_Color']
    if'Tags'in ticket_data and ticket_data['Tags'] is None:
        del ticket_data['Tags']
    if'Owner'in ticket_data and ticket_data['Owner'] is None:
        del ticket_data['Owner']
    return rally.put('HierarchicalRequirement', ticket_data)

# Create the DEV ticket
try:
    dev_ticket = create_child_ticket('DEV', f"[DEV] {parent_ticket_name}", parent_ticket_ref, ticket_data['DEV'])
    child_tickets['DEV'] = dev_ticket
    print(f"Child ticket 'DEV' created with ID: {dev_ticket.ObjectID}")
except Exception as e:
    print(f"Error creating child ticket 'DEV': {e}")

# Create the QA ticket with dependency on the DEV ticket
try:
    if child_tickets['DEV']:
        qa_ticket_data = ticket_data['QA']
        qa_ticket_data['Predecessors'] = [child_tickets['DEV']._ref]
        qa_ticket = create_child_ticket('QA', f"[QA] {parent_ticket_name}", parent_ticket_ref, qa_ticket_data)
        child_tickets['QA'] = qa_ticket
        print(f"Child ticket 'QA' created with ID: {qa_ticket.ObjectID}")
except Exception as e:
    print(f"Error creating child ticket 'QA': {e}")

# Create the L1 DEPLOY ticket with dependency on the QA ticket if the flag is set
if create_l1_deploy_ticket:
    try:
        if child_tickets['QA']:
            l1_deploy_ticket_data = ticket_data['L1 DEPLOY']
            l1_deploy_ticket_data['Predecessors'] = [child_tickets['QA']._ref]
            l1_deploy_ticket = create_child_ticket('L1 DEPLOY', f"[L1 DEPLOY] {parent_ticket_name}", parent_ticket_ref, l1_deploy_ticket_data)
            child_tickets['L1 DEPLOY'] = l1_deploy_ticket
            print(f"Child ticket 'L1 DEPLOY' created with ID: {l1_deploy_ticket.ObjectID}")
    except Exception as e:
        print(f"Error creating child ticket 'L1 DEPLOY': {e}")
