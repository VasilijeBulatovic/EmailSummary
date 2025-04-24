import requests
from datetime import datetime, timedelta
import re

# Replace with your OpenRouter API key
api_key = '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'

# Path to your input and output files
input_file_path = 'email.txt'
output_file_path = 'final.txt'

# Read the content of the email.txt file
# Function to check if the email date is within the last 24 hours
def is_recent(date_str):
    try:
        email_time = datetime.strptime(date_str, '%b %d, %Y, %I:%M %p')
        now = datetime.now()
        return now - timedelta(hours=24) <= email_time <= now
    except Exception as e:
        print("Date parsing error:", e)
        return False

# Read and filter recent emails
recent_emails = []
with open(input_file_path, 'r', encoding='utf-8') as file:
    email_blocks = file.read().split('\n\nBody:')

    for block in email_blocks:
        date_match = re.search(r'Date:\s*(.+)', block)
        if date_match:
            date_str = date_match.group(1).strip()
            if is_recent(date_str):
                recent_emails.append(block.strip())

# If no recent emails, exit early
if not recent_emails:
    print("No emails from the last 24 hours.")
    exit()

# Join recent emails into a single string
email_content = '\n\n'.join(recent_emails)


# Define the OpenRouter API endpoint for summarization
url = 'https://openrouter.ai/api/v1/chat/completions'

# Define the payload for summarizing the email content
payload = {
    "model": "nvidia/llama-3.1-nemotron-nano-8b-v1:free",
    "messages": [
        {"role": "system", "content": "Here’s what you need to do:- Analyze the content of the provided emails.- Group them by meaningful, relevant topics.- Write a concise, professional summary for each topic in clear, polished business English.- At the end of each topic summary, list the email subjects (or IDs if subjects are not provided) that contributed to that topic.**Format the output like this:**Topic 1: [Topic Title]Summary: [Well-structured, professional, clear summary of this topic based on relevant emails.]Emails Used:- [Email Subject or ID]- [Email Subject or ID]- [Email Subject or ID]Topic 2: [Topic Title]Summary: [Well-structured, professional, clear summary of this topic based on relevant emails.]Emails Used:- [Email Subject or ID]- [Email Subject or ID](…continue for all topics)**Important requirements:**- The summaries must be logically grouped by topics.- The tone should be professional and highly readable.- Avoid including irrelevant details. Add list of senders at the end- Make sure every topic clearly lists the emails it is based on."},
        {"role": "user", "content": email_content}
    ]
}

# Define the headers with your API key
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# Send the request to the API
response = requests.post(url, json=payload, headers=headers)
response_data = response.json()
# print(response_data)

# Check if the response is successful
if response.status_code == 200:
    # Check if 'choices' is in the response before accessing it
    if 'choices' in response_data:
        summarized_content = response_data['choices'][0]['message']['content']
        cleaned_content = summarized_content.replace('*', '').replace('\u2061', '').strip()

        # Write to final.txt
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(cleaned_content)
        print("Summary saved to final.txt.")
    else:
        print("Error: 'choices' key not found in the response.")
        print("Response content:", response_data)  # Print the full response content for debugging
else:
    print(f"Failed to summarize the email. Status code: {response.status_code}")
    print("Response text:", response.text)  # Print the error response text
