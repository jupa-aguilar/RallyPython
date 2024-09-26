import ssl
from pyral import Rally
from datetime import datetime, timedelta
import re

# Disable SSL verification (for testing only)
ssl._create_default_https_context = ssl._create_unverified_context

# Get API key from user input
API_KEY = input("Please enter your Rally API Key: ")

# Function to get the next occurrence of a specific day based on user input (0 = Monday, 6 = Sunday)
def get_specific_day_by_number(day_number):
    if day_number < 0 or day_number > 6:
        raise ValueError("Invalid day number. Please enter a number between 0 (Monday) and 6 (Sunday).")

    today = datetime.now()
    days_until_requested_day = (day_number - today.weekday() + 7) % 7
    if days_until_requested_day == 0:
        days_until_requested_day = 7

    return today + timedelta(days=days_until_requested_day)

# Function to get the release and correct iteration based on the date
def get_release_iteration(date):
    year = date.year
    quarter = (date.month - 1) // 3 + 1
    release = f"PI-{year}_Q{quarter}"

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
    }

    # Find the correct iteration where the date falls in
    for iteration, end_date in iteration_end_dates.items():
        if date <= end_date:
            return release, iteration

    return release, list(iteration_end_dates.keys())[-1]  # Default to the last iteration if date exceeds all

# Connect to Rally
try:
    rally = Rally(server='rally1.rallydev.com', apikey=API_KEY, workspace='Main')
    print("Successfully connected to Rally.")
except Exception as e:
    print(f"Error connecting to Rally: {e}")
    exit(1)

# Get the main release ticket ID
main_ticket_id = input("Enter the main release ticket ID: ").strip()

# Option to choose date method
date_option = input("Enter '1' to choose a specific date (mm/dd/yy) or '2' to select a day of the week (0 = Monday, 6 = Sunday): ").strip()

# Determine the new date
try:
    if date_option == '1':
        specific_date = input("Enter the specific date in mm/dd/yy format: ").strip()
        new_date = datetime.strptime(specific_date, "%m/%d/%y")
    elif date_option == '2':
        day_number = int(input("Enter the day number for the new date (0 = Monday, 1 = Tuesday, 2 = Wednesday, 3 = Thursday, 4 = Friday, 5 = Saturday, 6 = Sunday): "))
        new_date = get_specific_day_by_number(day_number)
    else:
        print("Invalid option selected. Exiting.")
        exit(1)
except ValueError as e:
    print(e)
    exit(1)

new_date_str = new_date.strftime("%m-%d-%Y")

# Get the new release and iteration
new_release_name, new_iteration_name = get_release_iteration(new_date)
print(f"New Release Name: {new_release_name}")
print(f"New Iteration Name: {new_iteration_name}")

# Fetch the Release and Iteration references
new_release = next(rally.get('Release', fetch="ObjectID,Name", query=f'Name = "{new_release_name}"'), None)
new_iteration = next(rally.get('Iteration', fetch="ObjectID,Name", query=f'Name = "{new_iteration_name}"'), None)

if not new_release:
    print(f"Error: No Release found with name {new_release_name}.")
    exit(1)
if not new_iteration:
    print(f"Error: No Iteration found with name {new_iteration_name}.")
    exit(1)

# Fetch and update the main ticket
try:
    main_ticket_response = rally.get('HierarchicalRequirement', fetch="ObjectID,Name,Description", query=f'FormattedID = "{main_ticket_id}"')
    main_ticket = next(main_ticket_response, None)

    if main_ticket and hasattr(main_ticket, 'ObjectID'):
        print(f"Retrieved main ticket: {main_ticket.Name}")
        new_name = f"[{new_date_str}] {main_ticket.Name.split('] ', 1)[1]}"
        
        # Use the provided description template for the main ticket
        new_description = f"""
DEV:<br>
[{new_date_str}] Overarching L1 Deployment Salesforce Release<br><br>
QA:<br>
[QA-regression-{new_date_str}] PreProd regression<br>
[QA-regression-{new_date_str}] PreProd rollback<br>
[QA-regression-{new_date_str}] Production roll forward
"""

        update_data = {
            "ObjectID": main_ticket.ObjectID,
            'Name': new_name,
            'Description': new_description,
            'Release': {'_ref': new_release._ref},
            'Iteration': {'_ref': new_iteration._ref}
        }

        print(f"Updating main ticket with data: {update_data}")
        updated_ticket = rally.update('HierarchicalRequirement', update_data)
        print(f"Successfully updated main release ticket {main_ticket_id}: {updated_ticket.Name}")

    else:
        print(f"Main ticket with ID {main_ticket_id} not found or not in expected format.")
        exit(1)
except Exception as e:
    print(f"Error updating main ticket {main_ticket_id}: {e}")
    exit(1)

# Update successor tickets
try:
    if main_ticket and hasattr(main_ticket, 'ObjectID'):
        successors = rally.get('HierarchicalRequirement', fetch="FormattedID,ObjectID,Name,Description", query=f'Predecessors.ObjectID = {main_ticket.ObjectID}')
        for successor in successors:
            update_data = {
                'ObjectID': successor.ObjectID,
                'Release': {'_ref': new_release._ref},
                'Iteration': {'_ref': new_iteration._ref}
            }

            # If the successor has 'Overarching' in the name, update the description with replaced dates
            if 'Overarching' in successor.Name:
                # Replace all dates in mm/dd/yyyy format with the new date
                updated_description = re.sub(r'\d{2}/\d{2}/\d{4}', new_date_str, successor.Description)
                update_data['Description'] = updated_description

            print(f"Updating successor {successor.FormattedID} with data: {update_data}")
            rally.update('HierarchicalRequirement', update_data)
            print(f"Updated successor ticket {successor.FormattedID} with new release and iteration.")
    else:
        print("No successors found for the main ticket.")
except Exception as e:
    print(f"Error updating successor tickets: {e}")
