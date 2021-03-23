import os

from twilio.rest import Client

CONDITIONS = [
    "FLAT",
    "VERY POOR",
    "POOR",
    "POOR TO FAIR",
    "FAIR",
    "FAIR TO GOOD",
    "GOOD",
    "VERY GOOD",
    "GOOD TO EPIC",
    "EPIC",
]
SURFLINE_SEARCH_URL = "https://www.surfline.com/search/"

FPATH_CONDITION_DATA_DICT = "surf_bot/condition_data_dict.pickle"

# Your Account SID from twilio.com/console
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
# Your Auth Token from twilio.com/console
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TWILIO_CLIENT = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
