import ssl
from pyral import Rally

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

# Function to delete a Rally ticket by ID
def delete_ticket(rally, ticket_id):
    try:
        # Get the ticket reference by querying its FormattedID
        ticket = rally.get('HierarchicalRequirement', query=f'FormattedID = "{ticket_id}"', instance=True)
        if ticket:
            # Delete the ticket
            rally.delete('HierarchicalRequirement', ticket.ObjectID)
            print(f"Successfully deleted ticket {ticket_id} (ObjectID: {ticket.ObjectID})")
        else:
            print(f"Ticket with ID {ticket_id} not found.")
    except Exception as e:
        print(f"Error deleting ticket {ticket_id}: {e}")

# Get the ticket IDs from user input
ticket_ids = get_ticket_ids()

# Rally connection configuration
RALLY_SERVER = 'rally1.rallydev.com'
WORKSPACE = 'Main'

# Authenticate with Rally
try:
    rally = Rally(server=RALLY_SERVER, apikey=API_KEY, workspace=WORKSPACE)
    print("Successfully connected to Rally.")
except Exception as e:
    print(f"Error connecting to Rally: {e}")
    exit(1)

# Delete each ticket in the list
for ticket_id in ticket_ids:
    delete_ticket(rally, ticket_id)
