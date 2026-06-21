import os
import time
from github_api import search_issues, claim_issue, fork_repo
from git_ops import clone_repo, sync_upstream_and_branch

import os
import time
from github_api import search_issues, claim_issue, fork_repo
from git_ops import clone_repo, sync_upstream_and_branch

def run_pipeline():
    # Check for token
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("[!] WARNING: GITHUB_TOKEN not set. Exiting loop.")
        return False

    # Search for high-quality ML, Data Science, and AI issues 
    # (Perfect for Werkstudent ML roles in Europe/Germany)
    print("\n[*] Scanning GitHub for fresh AI/ML/Data Science 'good first issues'...")
    issue = search_issues(keyword="machine-learning OR deep-learning OR data-science")
    if not issue:
        print("[-] No new unclaimed issues found right now. Sleeping for 10 minutes...")
        return True
        
    print(f"\n🎯 FOUND TARGET:")
    print(f"Repository: {issue['repo_name']}")
    print(f"Issue #{issue['number']}: {issue['title']}")
    print(f"Link: {issue['html_url']}\n")

    # Claim the issue
    claimed = claim_issue(issue['repo_name'], issue['number'], token)
    if not claimed:
        print("[-] Aborting pipeline due to claim failure.")
        return True
        
    time.sleep(2)
        
    # Fork the repository
    fork_url = fork_repo(issue['repo_name'], token)
    if not fork_url:
        print("[-] Aborting pipeline due to fork failure.")
        return True
        
    # Clone locally
    repo_basename = issue['repo_name'].split('/')[-1]
    target_dir = os.path.abspath(f"../{repo_basename}_bounty")
    
    if os.path.exists(target_dir):
        print(f"[-] Directory {target_dir} already exists. Skipping clone.")
    else:
        clone_repo(fork_url, target_dir)
    
    # SAFE SYNC: Prevents all Git conflicts and rebases by wiping local state
    upstream_url = f"https://github.com/{issue['repo_name']}.git"
    success = sync_upstream_and_branch(target_dir, upstream_url, f"fix-issue-{issue['number']}")
    if not success:
        return True
        
    # Generate auto-cleanup PR script
    pr_script_path = os.path.join(target_dir, "create_pr.py")
    with open(pr_script_path, "w") as f:
        f.write(f'''import urllib.request, json, os, ssl, shutil
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
token = os.environ.get("GITHUB_TOKEN")
payload = {{"title": "Fix for issue #{issue['number']}", "body": "Closes #{issue['number']}\\n\\nImplemented automated fix.", "head": "KartavyaDikshit:fix-issue-{issue['number']}", "base": "main"}}
req = urllib.request.Request("https://api.github.com/repos/{issue['repo_name']}/pulls", data=json.dumps(payload).encode(), headers={{'Authorization': f'token {{token}}', 'Accept': 'application/vnd.github.v3+json', 'Content-Type': 'application/json'}}, method='POST')
try:
    with urllib.request.urlopen(req, context=ctx) as r: 
        print("[+] PR Created:", json.loads(r.read())['html_url'])
        print("[*] Cleaning up local repository to save storage...")
        os.chdir("..")
        shutil.rmtree("{target_dir}", ignore_errors=True)
except Exception as e: print("[!] PR Failed:", e)
''')
        
    print(f"\n🎉 PIPELINE COMPLETE!")
    print(f"Branch 'fix-issue-{issue['number']}' is ready at {target_dir}.")
    print("CRITICAL: AGENT MUST NOW WRITE CODE AND PUSH TO THE FORK!")
    return False # Pause loop so Agent can write code

def main():
    print("🚀 Starting Infinite Open-Source Bounty Hunter Daemon...")
    while True:
        continue_loop = run_pipeline()
        if not continue_loop:
            break
        time.sleep(600)

if __name__ == "__main__":
    main()
