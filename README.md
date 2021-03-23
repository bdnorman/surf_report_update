# Surf Status Text Bot
This repo provides the code and setup instructions for an SMS bot that sends
users surf updates on their desired locations and conditions.


# Setup

## Create Twilio Account with SMS number
Sign up for a Twilio account and create an SMS enabled phone number. You can sign up for
a free trial [here](https://www.twilio.com/try-twilio). Some important 
limitations of the Twilio trial account:
* You can only send and receive texts from your personal number
* You only have $15 worth of SMS messages

After creating your Twilio account and phone number create the following
environment variables:
* `TWILIO_ACCOUNT_SID`
* `TWILIO_AUTH_TOKEN`
* `TWILIO_PHONE_NUMBER`

## Create python virtual environment
Create a fresh python virutalenv (with >=python 3.6) and install the
requirements.txt file
```bash
pip install -r requirements.txt
```

The current requirements.txt file could probably benefit from a bit of clean up.

## Run signup flask server
Running the user sign up texting requires two processes:

1. Run the flask application via `python surf_bot/app.py`. This will create a 
private service on your machine. To make it public, we use `ngrok`.

2. Make sure `ngrok` is installed on your machine and then run `ngrok http 5000`.
This redirects the Flask application's HTTP requests to a *temporary* URL.
*NOTE*: this URL will expire after 2 hours. You can pay for a public URL if you
would like to run this service for longer.
    * Navigate to the Twilio phone numbers console and change the `A MESSAGE COMES IN`
    Webhook to the outputed URL from `ngrok`. This [blog post](https://www.twilio.com/blog/build-a-sms-chatbot-with-python-flask-and-twilio)
    has more in depth instructions for this.

## Run status checker cron job
The user sign up will populate the "database" for what locations to check and
numbers to send updates to. In order to actually check spots for status updates,
the `surf_bot/send_updates.py` script should be run in a cron job with desired update
frequency.
```
*/5 * * * * source /path/to/surf/bot/virutalenv/bin/activate && python /path/to/cloned/repo/surf_bot/send_updates.py
```
Make sure to activate your `surf_bot` environment in the cron job.