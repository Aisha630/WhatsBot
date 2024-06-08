# WhatsBot

This project connects an OpenAI assistant to Whatsapp and uses a locally running flask app to do so while using tailscale to expose the localhost to the WhatsApp Cloud API.

# Requirements

An OpenAI API key

Whatsapp Permanent Access Token

A MONGODB connection URI

A valid phone number that is already connected to the WhatsApp Cloud API

# To run

First create a python virtual env

`python3 -m venv venv`

Source the virtual environment by using

`source venv/bin/activate`

Then download all required packages using the requirements.txt

`pip3 install -r ./requirements.txt`

Then set up a tailscale url. We do this to expose our server running on the localhost to the internet so Whatsapp can access it and send messages to it which we can then process and respond to.

If you are running tailscale for the first time, you will need to install the CLI. After that run

`tailscale up`

and then authenticate yourself.

Then set up the actual tunnel to expose your localhost to the internet by running this command (on macos you will need to install the tailscale app)

`sudo tailscale funnel 5002`

This command will return a url that will redirect traffic to a server running on your localhost on port 5002.
If you are running this command for the first time you need to first visit the returned URL and Enable funneling (make sure to check all options).

Then, you need to run the file webhook_verification.py
`python3 webhook_verification.py`

To make sure the link is working, visit the link/webhook. This should print Hello world on the screen if working correctly and if webhook_verification.py is running.

Now, you need to go to [WhatsApp Developer]([https://developers.facebook.com/apps/919504205777529/whatsapp-business/wa-settings/?business_id=912529367141548]()) ([https://developers.facebook.com/apps/919504205777529/whatsapp-business/wa-settings/?business_id=912529367141548]())

And add in the cloudflared URL as the callback URL and the verify token in the webhook_verification.py and verify the callback URL.

Now, you can stop running webhook_verification.py and run bot.py

`python3 bot.py`
This sets up our project and now any messages sent to our number +1 551 344 0219 will be processed and replied to using OpenAI.

# Other files

The text.py file has our SVM model which was trained to identify text as English or Roman Urdu.

The stats.py file has code that gives us statistics about the data collected yet, like the number of unique users etc.

The joblib files are just our saved models so we do not have to train the model again.

## The knowledge file

The knowledge file consists of question answer pairs approved from a doctor. Each question, apart form its original phrasing in Roman Urdu, has 5 rephrasings in Roman Urdu and 5 in English (Total 11). Then the answer has a phrasing in both English and Roman Urdu.

There are also some sample answer, but these are all in plain English.

This knowledge file is uploaded in the **MH with rephrasings** Vector Store in Open AI. While uploading this file, the chosen chunk size was kept at 550 and the overlap was set at 100. This is because each question answer pair, along with all its rephrasings, is almost 500 tokens on average.
I set the number of top-k chunks retrieved to be 3.
