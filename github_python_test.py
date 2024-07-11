import requests

# Define the owner, repo, and pull request number
owner = "Ancestry"
repo = "salesforce-dc"
pull_number = 3118  # Replace with the actual pull request number

# Define the URL and headers
url = f"https://github.ancestry.com/api/v3/repos/{owner}/{repo}/pulls/{pull_number}/commits"
headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": "Bearer c02e4f228d9661610e0a298907c1882cb9345273",  # Replace <TOKEN> with your actual token
    "X-GitHub-Api-Version": "2022-11-28"
}

# Make the GET request
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Print the JSON response
    commits = response.json()
    for commit in commits:
        print(commit)
else:
    # Print the error
    print(f"Request failed with status code {response.status_code}")
