import urllib.request
import urllib.parse
import json
import ssl
import os

def get_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def search_issues(keyword="machine learning", labels="good first issue"):
    """Finds the most recent open, unassigned issue."""
    print(f"[*] Searching GitHub API for '{keyword}' with label '{labels}'...")
    query = f'is:issue is:open label:"{labels}" {keyword}'
    encoded_query = urllib.parse.quote(query)
    url = f'https://api.github.com/search/issues?q={encoded_query}&sort=created&order=desc&per_page=10'
    
    req = urllib.request.Request(url, headers={'User-Agent': 'BountyHunterBot/1.0'})
    
    try:
        with urllib.request.urlopen(req, context=get_ssl_context()) as response:
            data = json.loads(response.read().decode())
            items = data.get('items', [])
            
            for item in items:
                if item['assignee'] is None and item['comments'] == 0:
                    repo_url = item['repository_url']
                    repo_name = repo_url.split('repos/')[-1]
                    return {
                        'title': item['title'],
                        'issue_url': item['url'],
                        'html_url': item['html_url'],
                        'repo_name': repo_name,
                        'number': item['number']
                    }
    except Exception as e:
        print(f"[!] Search failed: {e}")
    return None

def claim_issue(repo_name, issue_number, token):
    """Posts a comment to claim the issue."""
    print(f"[*] Claiming issue #{issue_number} on {repo_name}...")
    url = f"https://api.github.com/repos/{repo_name}/issues/{issue_number}/comments"
    headers = {
        'User-Agent': 'BountyHunterBot/1.0',
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
    }
    data = json.dumps({"body": "Hi! I am taking a look at this issue right now."}).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, context=get_ssl_context()) as response:
            if response.status == 201:
                print("[+] Successfully claimed issue!")
                return True
    except Exception as e:
        print(f"[!] Failed to claim issue: {e}")
    return False

def fork_repo(repo_name, token):
    """Forks the repository to the authenticated user's account."""
    print(f"[*] Forking {repo_name}...")
    url = f"https://api.github.com/repos/{repo_name}/forks"
    headers = {
        'User-Agent': 'BountyHunterBot/1.0',
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    req = urllib.request.Request(url, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, context=get_ssl_context()) as response:
            data = json.loads(response.read().decode())
            fork_url = data['clone_url']
            print(f"[+] Successfully forked to {fork_url}")
            return fork_url
    except Exception as e:
        print(f"[!] Failed to fork repo: {e}")
    return None
