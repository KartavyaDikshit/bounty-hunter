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

def create_branch(repo_dir, branch_name):
    """Creates and checks out a new branch in the repo."""
    print(f"[*] Creating new branch '{branch_name}'...")
    try:
        subprocess.run(['git', 'checkout', '-b', branch_name], cwd=repo_dir, check=True)
        print("[+] Branch created.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to create branch: {e}")
        return False
