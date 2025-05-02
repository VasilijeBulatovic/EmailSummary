import requests
from datetime import datetime, timedelta
import re
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='config.env')
api_key = os.getenv('API_KEY')

if not api_key:
    print("Error: API key is not set in the config.env file")
    exit()


input_file_path = 'email.txt'
output_file_path = os.getenv('OUTPUT_FILE')
prompt_file_path = 'prompt.txt'


if not input_file_path.endswith('.txt'):
    print("Error: The input file must be a .txt file.")
    exit()

with open(input_file_path, 'r', encoding='utf-8') as file:
    line_count = sum(1 for line in file)
    if line_count > 10000:
        print("Error: The input file '{input_file_path}' exceeds 10,000 lines.")
        exit()

if not os.path.exists(output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write("")


if not os.path.exists(prompt_file_path):
    print("Error: The prompt file 'prompt.txt' does not exist.")
    exit()


with open(prompt_file_path, 'r', encoding='utf-8') as prompt_file:
    prompt_content = prompt_file.read().strip()


def is_recent(date_str):
    try:
        email_time = datetime.strptime(date_str, '%b %d, %Y, %I:%M %p')
        now = datetime.now()
        return now - timedelta(hours=24) <= email_time <= now
    except Exception as e:
        print("Date parsing error:", e)
        return False

recent_emails = []
with open(input_file_path, 'r', encoding='utf-8') as file:
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


email_content = '\n\n'.join(recent_emails)


url = 'https://openrouter.ai/api/v1/chat/completions'

temperature = 0.0  # 0.0 je najbolje za sažimanje
top_p = 0.1        # Vece vrednosti daju kreativnije odgovore
frequency_penalty = 0.0  # Fraze koje se ponavljaju
presence_penalty = 0.0   # Dodavanje Nove Teme

payload = {
    "model": "mistralai/mistral-small-3.1-24b-instruct:free",
    "messages": [
        {"role": "system", "content": prompt_content},
        {"role": "user", "content": email_content}
    ],
    "temperature": temperature,
    "top_p": top_p,
    "frequency_penalty": frequency_penalty,
    "presence_penalty": presence_penalty
}
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

response = requests.post(url, json=payload, headers=headers)
response_data = response.json()


if response.status_code == 200:
    if 'choices' in response_data:
        summarized_content = response_data['choices'][0]['message']['content']
        cleaned_content = summarized_content.replace('*', '').replace('\u2061', '').strip()
        
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        log_header = (
            f"Summary generated on: {current_datetime}\n"
            f"Number of emails summarized: {len(recent_emails)}\n"
            "----------------------------------------\n"
        )

        with open(output_file_path, 'a', encoding='utf-8') as output_file:  # Use 'a' to append
            output_file.write(log_header)
            output_file.write(cleaned_content)
            output_file.write("\n\n")
        print("Summary saved to", output_file_path)
    else:
        print("Error: 'choices' key not found in the response.")
        print("Response content:", response_data)
else:
    print(f"Failed to summarize the email. Status code: {response.status_code}")
    print("Response text:", response.text)
