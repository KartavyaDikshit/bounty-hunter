import os
import time
from github_api import search_issues, claim_issue, fork_repo
from git_ops import clone_repo, sync_upstream_and_branch

def main():
    print("🚀 Starting Open-Source Bounty Hunter...")
    
    # Check for token (for claiming and forking)
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("[!] WARNING: GITHUB_TOKEN environment variable not set.")
        print("[!] The bot will run in 'Discovery Only' mode (no claiming/forking).")
        print("[!] To enable full automation, run: export GITHUB_TOKEN='your_pat_here'\n")

    # 1. Discover an issue
    issue = search_issues(keyword="machine-learning")
    if not issue:
        print("[-] No new unclaimed issues found right now. Sleeping...")
        return
        
    print(f"\n🎯 FOUND TARGET:")
    print(f"Repository: {issue['repo_name']}")
    print(f"Issue #{issue['number']}: {issue['title']}")
    print(f"Link: {issue['html_url']}\n")

    if not token:
        print("[-] Stopping here. Set GITHUB_TOKEN to automate claiming and forking.")
        return

    # 2. Claim the issue
    claimed = claim_issue(issue['repo_name'], issue['number'], token)
    if not claimed:
        print("[-] Aborting pipeline due to claim failure.")
        return
        
    time.sleep(2) # Brief pause for GitHub API
        
    # 3. Fork the repository
    fork_url = fork_repo(issue['repo_name'], token)
    if not fork_url:
        print("[-] Aborting pipeline due to fork failure.")
        return
        
    # 4. Clone locally
    repo_basename = issue['repo_name'].split('/')[-1]
    target_dir = os.path.abspath(f"../{repo_basename}_bounty")
    
    if os.path.exists(target_dir):
        print(f"[-] Directory {target_dir} already exists. Skipping clone.")
    else:
        clone_repo(fork_url, target_dir)
    
    # SYNC WITH UPSTREAM AND BRANCH (Always run this, even if directory already existed!)
    upstream_url = f"https://github.com/{issue['repo_name']}.git"
    sync_upstream_and_branch(target_dir, upstream_url, f"fix-issue-{issue['number']}")
        
    # Generate PR template script for the AI to use later
    pr_script_path = os.path.join(target_dir, "create_pr.py")
    with open(pr_script_path, "w") as f:
        f.write(f'''import urllib.request, json, os, ssl
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
token = os.environ.get("GITHUB_TOKEN")
payload = {{"title": "Fix for issue #{issue['number']}", "body": "Closes #{issue['number']}\\n\\nImplemented automated fix.", "head": "KartavyaDikshit:fix-issue-{issue['number']}", "base": "main"}}
req = urllib.request.Request("https://api.github.com/repos/{issue['repo_name']}/pulls", data=json.dumps(payload).encode(), headers={{'Authorization': f'token {{token}}', 'Accept': 'application/vnd.github.v3+json', 'Content-Type': 'application/json'}}, method='POST')
try:
    with urllib.request.urlopen(req, context=ctx) as r: print("[+] PR Created:", json.loads(r.read())['html_url'])
except Exception as e: print("[!] PR Failed:", e)
''')
        
    # 5. Hand off to Agent
    print(f"\n🎉 PIPELINE COMPLETE!")
    print(f"The repository is ready for you (or an AI agent) at: {{target_dir}}")
    print(f"Branch 'fix-issue-{issue['number']}' is checked out.")
    print("CRITICAL: AGENT MUST NOW WRITE CODE, COMMIT IT, AND PUSH TO THE FORK!")
    print("Once pushed, run `python3 create_pr.py` to automatically open the Pull Request.")

if __name__ == "__main__":
    main()
