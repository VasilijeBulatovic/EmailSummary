import re
import json
import os
from . import userPreferences as pref

def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: Could not find file at {file_path}")
        return None

def split_into_emails(content):
    emails = re.split(r'\d+\.\s*\n+', content)[1:]
    return [email for email in emails if email.strip()]

def get_email_info(email_text):
    email_info = {}
    

    from_match = re.search(r'From: (.*)', email_text)
    email_info['from'] = from_match.group(1) if from_match else "Unknown"
    
    to_match = re.search(r'To: (.*)', email_text)
    email_info['to'] = to_match.group(1) if to_match else "Unknown"
    
    date_match = re.search(r'Date: (.*)', email_text)
    email_info['date'] = date_match.group(1) if date_match else "Unknown"
    
    subject_match = re.search(r'Subject: (.*)', email_text)
    email_info['subject'] = subject_match.group(1) if subject_match else "No Subject"
    
    body_match = re.search(r'Body:\n(.*?)(?=\n\n|\Z)', email_text, re.DOTALL)
    email_info['body'] = body_match.group(1).strip() if body_match else ""
    
    return email_info

def check_importance(email_info):
    importance = 1
    
    # Convert text to lowercase for easier searching
    subject = email_info['subject'].lower()
    body = email_info['body'].lower()
    sender = email_info['from'].lower()
    
    # Check for important senders
    if any(sender in email_info['from'].lower() for sender in pref.IMPORTANT_SENDERS):
        importance += 2
    
    # Check for important keywords
    for word in pref.IMPORTANT_KEYWORDS:
        if word in subject or word in body:
            importance += 1
    
    # Check for topics of interest
    for topic in pref.TOPICS_OF_INTEREST:
        if topic in subject or topic in body:
            importance += 1
    
    # Make sure importance doesn't go above 5
    return min(importance, 5)

def add_extra_info(email_info):
    # Add length of the email
    email_info['length'] = len(email_info['body'])
    
    # Check if email contains topics of interest
    email_info['topics_found'] = [
        topic for topic in pref.TOPICS_OF_INTEREST 
        if topic in email_info['body'].lower()
    ]
    
    # Add importance level
    email_info['importance'] = check_importance(email_info)
    
    return email_info

def save_to_json(emails, output_file='processed_emails.json'):
    try:
        # Ensure the directory exists
        output_dir = "backend/prepareEmails"
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, output_file)
        
        # Create empty JSON file if it doesn't exist
        if not os.path.exists(output_path):
            with open(output_path, 'w') as file:
                json.dump([], file)
            print(f"Created new file: {output_file}")
        
        with open(output_path, 'w') as file:
            json.dump(emails, file, indent=2)
        print(f"Successfully saved to {output_file}")
    
    except Exception as e:
        print(f"Error saving file: {e}")

def process_emails(file_path):
    content = read_file(file_path)
    if not content:
        return
    
    email_list = split_into_emails(content)
    
    processed_emails = []
    for email in email_list:
        email_info = get_email_info(email)
        email_info = add_extra_info(email_info)
        processed_emails.append(email_info)
    
    save_to_json(processed_emails)
    print(f"Processed {len(processed_emails)} emails successfully!")

if __name__ == "__main__":
    process_emails('backend/emails/email.txt')