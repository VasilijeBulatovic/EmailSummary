# EmailSummary

<<<<<<< HEAD
EmailSummary is a Python-based tool that summarizes emails received in the last 24 hours. It uses the OpenRouter API to generate concise, professional summaries of email content, grouped by meaningful topics.

## Features

- Filters emails received in the last 24 hours.
- Groups emails into meaningful topics.
- Generates professional summaries for each topic.
- Outputs the summary to a file (`final.txt`).
- Ensures consistent and structured AI responses using OpenRouter models.
- Handles large input files and validates file formats.

## Requirements

- Python 3.13.3
- An OpenRouter API key
- The following Python libraries:
  - `requests`
  - `python-dotenv`
- Run pip install -r requirements.txt in the EmailSummary/backend

## Installation

1. Clone the repository:
     git clone https://github.com/your-username/EmailSummary.git
     cd EmailSummary
     Installl requeried libraries
        -`pip install` ...

2.  Create the config.env file
      In that file add API_KEY=YOUR_OPENROUTER_API_KEY
      and OUTPUT_FILE = YOUR_OUTPUT_FILE_NAME

Ensure that the `email.txt` and `prompt.txt` are present in the project


# Emails folder holds list of emails used in this example 

# PrepareEmails exstracts important info from list of emails based on user preferences, after that they are sent to ai for further summary

# FormatSummarizedEmails cleans the response from ai (openRouter in this case), removes *,#,@ ...

# PromptSettings is used to adjust response from ai (openRouter in this case) so it is reliable and accurate every time.