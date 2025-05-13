import requests
from datetime import datetime, timedelta
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='config.env')
api_key = os.getenv('API_KEY')

# Constants
INPUT_FILE = 'email.txt'
OUTPUT_FILE = os.getenv('OUTPUT_FILE', 'final.txt')
PROMPT_FILE = 'prompt.txt'
MAX_LINES = 10000

# Check API key
if not api_key:
    raise ValueError("Error: API key is not set in the config.env file.")

# Check input file
if not INPUT_FILE.endswith('.txt'):
    raise ValueError("Error: The input file must be a .txt file.")

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(f"Error: The input file '{INPUT_FILE}' does not exist.")

# Check input file size
with open(INPUT_FILE, 'r', encoding='utf-8') as file:
    line_count = sum(1 for _ in file)
    if line_count > MAX_LINES:
        raise ValueError(f"Error: The input file '{INPUT_FILE}' exceeds {MAX_LINES} lines.")

# Ensure output file exists
if not os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as file:
        file.write("")

# Check prompt file
if not os.path.exists(PROMPT_FILE):
    raise FileNotFoundError(f"Error: The prompt file '{PROMPT_FILE}' does not exist.")

# Read prompt content
with open(PROMPT_FILE, 'r', encoding='utf-8') as prompt_file:
    prompt_content = prompt_file.read().strip()

# Function to check if an email is recent
def is_recent(date_str):
    try:
        email_time = datetime.strptime(date_str, '%b %d, %Y, %I:%M %p')
        now = datetime.now()
        return now - timedelta(hours=24) <= email_time <= now
    except Exception as e:
        print(f"Date parsing error: {e}")
        return False

# Function to read the input file and extract emails from the last 24 hours
recent_emails = []
with open(INPUT_FILE, 'r', encoding='utf-8') as file:
    email_blocks = file.read().split('\n\nBody:')
    for block in email_blocks:
        date_match = re.search(r'Date:\s*(.+)', block)
        if date_match:
            date_str = date_match.group(1).strip()
            if is_recent(date_str):
                recent_emails.append(block.strip())

if not recent_emails:
    print("No emails from the last 24 hours.")
    exit()

# Combine recent emails into a single string
email_content = '\n\n'.join(recent_emails)

# API request details
url = 'https://openrouter.ai/api/v1/chat/completions'
payload = {
    "model": "mistralai/mistral-small-3.1-24b-instruct:free",
    "messages": [
        {"role": "system", "content": prompt_content},
        {"role": "user", "content": email_content}
    ],
    "temperature": 0.0,
    "top_p": 0.1,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# Send the request to the API
response = requests.post(url, json=payload, headers=headers)
response_data = response.json()

# Handle the API response
if response.status_code == 200:
    if 'choices' in response_data:
        summarized_content = response_data['choices'][0]['message']['content']
        cleaned_content = summarized_content.replace('*', '').replace('\u2061', '').strip()

        # Get the current date and time
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Prepare the log header
        log_header = (
            f"Summary generated on: {current_datetime}\n"
            f"Number of emails summarized: {len(recent_emails)}\n"
            "----------------------------------------\n"
        )

        # Append the log header and summary to the output file
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as output_file:  # Use 'a' to append
            output_file.write(log_header)
            output_file.write(cleaned_content)
            output_file.write("\n\n")
        print(f"Summary added to {OUTPUT_FILE}")
    else:
        print("Error: 'choices' key not found in the response.")
        print("Response content:", response_data)
else:
    print(f"Failed to summarize the email. Status code: {response.status_code}")
    print("Response text:", response.text)
