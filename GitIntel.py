import requests
import os
import sys
import subprocess
import time
import random
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
from colorama import Fore, init

init(autoreset=True)

def check_and_install_packages(packages):
    print(Fore.YELLOW + "Checking Requirements...\n")
    for package, version in packages.items():
        try:
            __import__(package)
            print(Fore.YELLOW + f"[+] {package} is already installed.")
        except ImportError:
            print(Fore.RED + f"[i] {package} not found. Installing...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', f"{package}=={version}"])
            print(Fore.GREEN + f"[+] {package} installed successfully.")

def get_file_path(prompt_text):
    completer = PathCompleter()
    return prompt(prompt_text, completer=completer).strip()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
    ]
    return random.choice(user_agents)

class GitHubEmailExtractor:
    def __init__(self, username):
        self.username = username
        self.base_url = "https://api.github.com/"  # Replace with your specific API path or key to have a longer rate limit. If you don't want to do that, you can keep using the default one.

        self.headers = {
            "User-Agent": get_random_user_agent()
        }
        self.user_info = {}

    def user_exists(self):
        response = requests.get(f"{self.base_url}/users/{self.username}", headers=self.headers)
        
        if response.status_code == 200:
            user_data = response.json()
            self.user_info = {
                'name': user_data.get('name', 'N/A'),
                'id': user_data.get('id', 'N/A'),
                'bio': user_data.get('bio', 'No bio available'),
                'html_url': user_data.get('html_url', 'N/A'),
                'profile_pic': user_data.get('avatar_url', 'N/A'),
                'created_at': user_data.get('created_at', 'N/A'),
                'company': user_data.get('company', 'N/A'),
                'location': user_data.get('location', 'N/A'),
                'followers': user_data.get('followers', 'N/A'),
                'following': user_data.get('following', 'N/A'),
                'type': user_data.get('type', 'N/A'),
                'email': user_data.get('email', 'N/A')
            }
            return True
        elif response.status_code == 404:
            print(Fore.RED + "[!] GitHub user does not exist.")
        elif response.status_code == 403:
            print(Fore.RED + "[!] GitHub API rate limit reached. Please try again later.")
            sys.exit(1)
        else:
            print(Fore.RED + f"[!] Failed to retrieve user: {response.text}")
        
        return False

    def get_repositories(self):
        response = requests.get(f"{self.base_url}/users/{self.username}/repos", headers=self.headers)
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                print(Fore.RED + "[!] Unexpected response format from repositories.")
                return []
        else:
            print(Fore.RED + f"[!] Failed to retrieve repositories: {response.text}")
            return []

    def get_commits(self, repo):
        response = requests.get(f"{self.base_url}/repos/{self.username}/{repo}/commits", headers=self.headers)
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                print(Fore.RED + "[!] Unexpected response format from commits.")
                return []
        else:
            print(Fore.RED + f"[!] Failed to retrieve commits for {repo}")
            return []

    def get_public_events(self):
        response = requests.get(f"{self.base_url}/users/{self.username}/events/public", headers=self.headers)
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                print(Fore.RED + "[!] Unexpected response format from public events.")
                return []
        else:
            print(Fore.RED + f"[!] Failed to retrieve public events: {response.text}")
            return []

    def collect_emails(self, include_hidden=False, user_specific=False):
        email_sources = {}

        repos = self.get_repositories()
        for repo in repos:
            if not repo.get("fork"):
                try:
                    commits = self.get_commits(repo.get('name', ''))
                    for commit in commits:
                        if commit:
                            email = commit.get('commit', {}).get('author', {}).get('email')
                            if email:
                                email_sources.setdefault(email, []).append(f"Repo: https://github.com/{self.username}/{repo['name']}, User: {commit.get('author', {}).get('login', 'unknown')}")
                except Exception as e:
                    print(Fore.RED + f"[!] Error processing repo {repo.get('name', 'unknown')}")

        events = self.get_public_events()
        for event in events:
            if event.get('type') == 'PushEvent':
                try:
                    for commit in event.get('payload', {}).get('commits', []):
                        if commit:
                            email = commit.get('author', {}).get('email')
                            if email:
                                email_sources.setdefault(email, []).append(f"Public Commit, User: {event.get('actor', {}).get('login', 'unknown')}")
                except Exception as e:
                    print(Fore.RED + f"[!] Error processing event: {e}")

        if not include_hidden:
            email_sources = {email: sources for email, sources in email_sources.items() if not email.endswith('@users.noreply.github.com')}

        if user_specific:
            email_sources = {email: sources for email, sources in email_sources.items() if any(f"User: {self.username}" in source for source in sources)}

        return email_sources
    
def get_user_input(prompt, default_value):
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in ['y', 'n', '']:
            return user_input if user_input else default_value
        else:
            print(Fore.RED + "Invalid input. Please enter 'y' or 'n'.")
            print(Fore.YELLOW + "[i] Press Enter to try again...")
            input()
            clear_screen()
            banner()

def banner():
    print(Fore.MAGENTA + r"""
                  _____ _ _   _____       _       _ 
                 / ____(_) | |_   _|     | |     | |
                | |  __ _| |_  | |  _ __ | |_ ___| |
                | | |_ | | __| | | | '_ \| __/ _ \ |
                | |__| | | |_ _| |_| | | | ||  __/ |
                 \_____|_|\__|_____|_| |_|\__\___|_|
    """)
    print(Fore.GREEN + "Unmasking GitHub’s Hidden Insights, One Repo at a Time - AnonKryptiQuz\n")

def main():
    clear_screen()

    required_packages = {
        'requests': '2.28.1',
        'prompt_toolkit': '3.0.36',
        'colorama': '0.4.6'
    }
    check_and_install_packages(required_packages)

    time.sleep(3)
    clear_screen()

    while True:
        banner()

        username = get_file_path("[?] Enter GitHub username: ")
        if not username:
            print(Fore.RED + "Username cannot be empty.")
            print(Fore.YELLOW + "[i] Press Enter to try again...")
            input()
            clear_screen()
            continue
        else:
            break

    extractor = GitHubEmailExtractor(username)
    if not extractor.user_exists():
        print(Fore.RED + "\nGitHub user does not exist.")
        return
    
    user_choice = get_user_input(Fore.WHITE + "[?] Do you want to configure advanced options? (y/n, press Enter for n): ", 'n')

    if user_choice == 'y':
        include_hidden = get_user_input(Fore.WHITE + "[?] Include hidden emails (e.g., @users.noreply.github.com)? (y/n, press Enter for y): ", 'y')
        user_specific = get_user_input(Fore.WHITE + "[?] Filter emails by user activity? (y/n, press Enter for n): ", 'n')
    else:
        include_hidden = 'y'
        user_specific = 'n'

    include_hidden = include_hidden == 'y'
    user_specific = user_specific == 'y'

    print(Fore.YELLOW + "\nLoading, Please Wait...")
    time.sleep(3)
    clear_screen()

    print(Fore.BLUE + "[?] Starting Scan...\n")
    print(Fore.CYAN + f"[i] Profile URL: " + Fore.WHITE + f"{extractor.user_info['html_url']}")
    print(Fore.CYAN + f"[i] Username: " + Fore.WHITE + f"{username}")
    print(Fore.CYAN + f"[i] Name: " + Fore.WHITE + f"{extractor.user_info['name']}")
    print(Fore.CYAN + f"[i] Profile Picture: " + Fore.WHITE + f"{extractor.user_info['profile_pic']}")
    print(Fore.CYAN + f"[i] Bio: " + Fore.WHITE + f"{extractor.user_info['bio']}")
    print(Fore.CYAN + f"[i] Email: " + Fore.WHITE + f"{extractor.user_info['email']}")
    print(Fore.CYAN + f"[i] Company: " + Fore.WHITE + f"{extractor.user_info['company']}")
    print(Fore.CYAN + f"[i] Location: " + Fore.WHITE + f"{extractor.user_info['location']}")
    print(Fore.CYAN + f"[i] Account Type: " + Fore.WHITE + f"{extractor.user_info['type']}")
    print(Fore.CYAN + f"[i] Followers - Following: " + Fore.WHITE + f"{extractor.user_info.get('followers', 'N/A')} - {extractor.user_info.get('following', 'N/A')}")
    print(Fore.CYAN + f"[i] User ID: " + Fore.WHITE + f"{extractor.user_info['id']}")
    print(Fore.CYAN + f"[i] Account created on: " + Fore.WHITE + f"{extractor.user_info['created_at']}\n")
    print(Fore.BLUE + "[?] Extracting Email(s):\n")

    start_time = time.time()
    emails = extractor.collect_emails(include_hidden, user_specific)

    if not emails:
        print(Fore.RED + "No emails were found.\n")
        email_count = 0
    else:
        email_count = len(emails)
        for email, sources in emails.items():
            print(Fore.GREEN + f"Email: {email}")
            print(Fore.BLUE + "Sources:")
            for source in sources:
                print(Fore.MAGENTA + f"  - {source}")
            print()

    print(Fore.YELLOW + "[i] Email extraction completed.")
    print(Fore.YELLOW + f"[i] Number of emails found: {email_count}")
    print(Fore.YELLOW + f"[i] Time taken: {round(time.time() - start_time, 2)} seconds\n")

    save = input(Fore.BLUE + "[?] Do you want to save the results to a file? (y/n, press Enter for n): ").lower()
    if save == 'y':
        output_file = get_user_input(Fore.YELLOW + "[?] Enter the filename to save results (press Enter for 'results.txt'): ", 'results.txt')
        with open(output_file, 'w') as f:
            f.write(f"[i] Profile URL: {extractor.user_info['html_url']}\n")
            f.write(f"[i] Username: {username}\n")
            f.write(f"[i] Name: {extractor.user_info['name']}\n")
            f.write(f"[i] Profile Picture: {extractor.user_info['profile_pic']}\n")
            f.write(f"[i] Bio: {extractor.user_info['bio']}\n")
            f.write(f"[i] Email: {extractor.user_info['email']}\n")
            f.write(f"[i] Company: {extractor.user_info['company']}\n")
            f.write(f"[i] Location: {extractor.user_info['location']}\n")
            f.write(f"[i] Type: {extractor.user_info['type']}\n")
            f.write(f"[i] Followers - Following: {extractor.user_info.get('followers', 'N/A')} - {extractor.user_info.get('following', 'N/A')}\n")
            f.write(f"[i] User ID: {extractor.user_info['id']}\n")
            f.write(f"[i] Account created on: {extractor.user_info['created_at']}\n\n")

            for email, sources in emails.items():
                f.write(f"Email: {email}\n")
                f.write("Sources:\n")
                for source in sources:
                    f.write(f"  - {source}\n")
                f.write("\n")
        print(Fore.GREEN + f"[i] Results have been saved to {output_file}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Program terminated by the user!")
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"[!] An unexpected error occurred: {e}")
        sys.exit(1)
