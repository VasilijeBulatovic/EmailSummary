IMPORTANT_SENDERS = [
    'github.com',
    'techtalk.com',
    'digitalsolutions.com'
]

IMPORTANT_KEYWORDS = [
    'urgent',
    'important',
    'deadline',
    'asap',
    'meeting',
    'report'
]

TOPICS_OF_INTEREST = [
    'ai',
    'artificial intelligence',
    'machine learning',
    'python',
    'data science'
]

MIN_IMPORTANCE_LEVEL = 1

MAX_EMAIL_AGE = 1 # in days 

SUMMARY_PREFERENCES = {
    'max_length': 100,  # Maximum length one summarized email
    'include_subjects': True,
    'include_dates': True,
    'group_by_sender': True,
    'sort_by_importance': True
}