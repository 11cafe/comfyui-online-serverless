import subprocess
import requests
import base64
import re

def get_first_image_url_from_readme(owner, repo):
    # Construct the URL for the README API
    readme_api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    
    # Make a request to get the README
    readme_response = requests.get(readme_api_url)
    if readme_response.status_code == 200:
        readme_data = readme_response.json()
        # Decode the content from base64
        readme_content = base64.b64decode(readme_data['content']).decode('utf-8')
        
        # Use regular expressions to find image URLs in markdown and HTML <img> tags
        markdown_image_urls = re.findall(r'!\[.*?\]\((.*?)\)', readme_content)
        html_img_urls = re.findall(r'<img.*?src="(.*?\.(jpg|jpeg|png|gif|bmp|svg))".*?>', readme_content)
        
        # Combine the lists, maintaining order and removing duplicates
        all_image_urls = list(dict.fromkeys(markdown_image_urls + html_img_urls))
        
        if all_image_urls:
            return all_image_urls[0]  # Return the first image URL
        else:
            return "No image found in README"
    else:
        return "Error: Unable to fetch README information"

######v2
def get_repo_user_and_name(module_path):
    command = ['git', 'config', '--get', 'remote.origin.url']
    try:
        result = subprocess.run(command, cwd=module_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        repo_url = result.stdout.strip()

        # Match both HTTPS and SSH URLs
        match = re.search(r'(?:https?://github.com/|git@github.com:)([^/]+)/([^/.]+)', repo_url)
        if match:
            username, repo_name = match.groups()
            # Attempt to get the default branch name
            branch_command = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
            branch_result = subprocess.run(branch_command, cwd=module_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            main_branch = branch_result.stdout.strip()

            # Get the latest commit hash
            commit_command = ['git', 'rev-parse', 'HEAD']
            commit_result = subprocess.run(commit_command, cwd=module_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            latest_commit = commit_result.stdout.strip()

            return username, repo_name, main_branch, latest_commit
        else:
            return "Could not parse URL", ""
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}", ""
