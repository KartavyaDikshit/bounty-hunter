import subprocess
import os

def clone_repo(clone_url, target_dir):
    """Clones a git repository to a specific directory."""
    print(f"[*] Cloning {clone_url} into {target_dir}...")
    try:
        subprocess.run(['git', 'clone', clone_url, target_dir], check=True)
        print("[+] Clone complete.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[!] Git clone failed: {e}")
        return False

def sync_upstream_and_branch(repo_dir, upstream_url, branch_name):
    """Syncs the local clone with the upstream repo, then creates a new branch."""
    print(f"[*] Syncing with upstream and creating branch '{branch_name}'...")
    try:
        # Add upstream remote
        subprocess.run(['git', 'remote', 'add', 'upstream', upstream_url], cwd=repo_dir, stderr=subprocess.DEVNULL)
        # Fetch latest upstream
        subprocess.run(['git', 'fetch', 'upstream'], cwd=repo_dir, check=True)
        # Checkout main (or master)
        try:
            subprocess.run(['git', 'checkout', 'main'], cwd=repo_dir, check=True)
            default_branch = 'main'
        except subprocess.CalledProcessError:
            subprocess.run(['git', 'checkout', 'master'], cwd=repo_dir, check=True)
            default_branch = 'master'
        
        # Hard reset to upstream
        subprocess.run(['git', 'reset', '--hard', f'upstream/{default_branch}'], cwd=repo_dir, check=True)
        # Create and checkout new feature branch
        subprocess.run(['git', 'checkout', '-B', branch_name], cwd=repo_dir, check=True)
        print(f"[+] Successfully synced upstream and checked out '{branch_name}'.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to sync upstream and create branch: {e}")
        return False
