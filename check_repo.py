import requests

def check_repository_exists(repo_url):
    # Convert URL to API format
    api_url = repo_url.replace("github.com", "api.github.com/repos")
    
    # Make request to GitHub API
    response = requests.get(api_url)
    
    # Check if repository exists (status code 200)
    if response.status_code == 200:
        print("Yes")
        return True
    else:
        print("No")
        return False

if __name__ == "__main__":
    repo_url = "https://github.com/VonholtenCodes/home-io"
    check_repository_exists(repo_url)