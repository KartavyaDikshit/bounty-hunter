import os
import time
from github_api import search_issues, claim_issue, fork_repo
from git_ops import clone_repo, create_branch

def main():
    print("🚀 Starting Open-Source Bounty Hunter...")
    
    # Check for token (for claiming and forking)
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("[!] WARNING: GITHUB_TOKEN environment variable not set.")
        print("[!] The bot will run in 'Discovery Only' mode (no claiming/forking).")
        print("[!] To enable full automation, run: export GITHUB_TOKEN='your_pat_here'\n")

    # 1. Discover an issue
    issue = search_issues(keyword="python")
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
        create_branch(target_dir, f"fix-issue-{issue['number']}")
        
    # 5. Hand off to Agent (Placeholder)
    print(f"\n🎉 PIPELINE COMPLETE!")
    print(f"The repository is ready for you (or an AI agent) at: {target_dir}")
    print(f"Branch 'fix-issue-{issue['number']}' is checked out.")
    print("Next step: Trigger Antigravity Agent to read the issue and write code!")

if __name__ == "__main__":
    main()
