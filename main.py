import requests
from datetime import datetime, timedelta
import re


api_key = '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'


input_file_path = 'email.txt'
output_file_path = 'final.txt'


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


payload = {
    "model": "nvidia/llama-3.1-nemotron-nano-8b-v1:free",
    "messages": [
        {"role": "system", "content": "Here’s what you need to do:- Analyze the content of the provided emails.- Group them by meaningful, relevant topics.- Write a concise, professional summary for each topic in clear, polished business English.- At the end of each topic summary, list the email subjects (or IDs if subjects are not provided) that contributed to that topic.**Format the output like this:**Topic 1: [Topic Title]Summary: [Well-structured, professional, clear summary of this topic based on relevant emails.]Emails Used:- [Email Subject or ID]- [Email Subject or ID]- [Email Subject or ID]Topic 2: [Topic Title]Summary: [Well-structured, professional, clear summary of this topic based on relevant emails.]Emails Used:- [Email Subject or ID]- [Email Subject or ID](…continue for all topics)**Important requirements:**- The summaries must be logically grouped by topics.- The tone should be professional and highly readable.- Avoid including irrelevant details. Add list of senders at the end- Make sure every topic clearly lists the emails it is based on."},
        {"role": "user", "content": email_content}
    ]
}


headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}


response = requests.post(url, json=payload, headers=headers)
response_data = response.json()
# print(response_data)


if response.status_code == 200:
    
    if 'choices' in response_data:
        summarized_content = response_data['choices'][0]['message']['content']
        cleaned_content = summarized_content.replace('*', '').replace('\u2061', '').strip()

        
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(cleaned_content)
        print("Summary saved to final.txt.")
    else:
        print("Error: 'choices' key not found in the response.")
        print("Response content:", response_data)
else:
    print(f"Failed to summarize the email. Status code: {response.status_code}")
    print("Response text:", response.text) 
