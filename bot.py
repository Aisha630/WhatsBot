import pytz
from datetime import datetime, timedelta
from dynamo import ThreadDataSixHours
from joblib import load
import os
from dotenv import load_dotenv
from waitress import serve
import queue
import threading
from pynamodb.models import Model
import pynamodb
import json
import time
from openai import OpenAI
import requests
from flask import Flask, request
import sys
sys.path.append(
    "c:\\users\\waleed arshad\\appdata\\local\\programs\\python\\python312\\lib\\site-packages")
sys.path.append(
    "c:\\users\\waleed arshad\\appdata\\local\\programs\\python\\python312\\lib\\site-packages\\decouple\\__init__.py")
# from decouple import config

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
WHATSAPP_TOKEN = os.getenv('WHATSAPP_PERMANENT_ACCESS_TOKEN')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')


res_q = queue.Queue()
res_id_list = []
model = load('./model.joblib')
vectorizer = load('./vectorizer.joblib')

# class User_data(Model):
#     class Meta:
#         table_name = "thread_less_data"
#         region = "us-east-1"
#         aws_access_key_id = "AKIA47CR2BY3NO7RAE43"
#         aws_secret_access_key = "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"
#     message_id = pynamodb.attributes.UnicodeAttribute(hash_key=True) ## hash key = True means this is the primary key
#     phone_number = pynamodb.attributes.UnicodeAttribute()
#     incoming_message = pynamodb.attributes.UnicodeAttribute()
#     reply = pynamodb.attributes.UnicodeAttribute()
#     thread_ID = pynamodb.attributes.UnicodeAttribute()

with open('assistant.json') as f:
    assistant_id = json.load(f)['assistant_id']

# Create a Flask app
app = Flask(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)
print("Using Assistant:", assistant_id)


def send_msg(msg, number):
    # headers for the response used for API authentication. The token is the permanent access token for the WhatsApp Cloud API
    headers = {
        'Authorization': 'Bearer EAANESMGOCnkBOyqM7wy5b5xDHkUC9urmTz3vH6V7SYiZBxNnmianZARMpZCjqvZAnXVVN0Cp6TC0fSojyN86cg8ygk83TuHx3lZAt5wdqtjKCyYjhjdPyI82sZBG4oZCZAKyoEZCbkVZC9aWLVVkmiWtVrLAn6DdStZBUGcbg4wVYFNCmJjASBuVIJcpYw84ZAl7',
    }
    # Create a dictionary with the message to be sent to the user
    json_data = {
        'messaging_product': 'whatsapp',
        'to': number,
        'type': 'text',
        "text": {
            "body": msg
        }
    }
    # Sending the POST request to the WhatsApp API endpoint. The /messages endpoint is used to send messages to the user
    response = requests.post(
        'https://graph.facebook.com/v18.0/220890917766697/messages', headers=headers, json=json_data)
    # print("\nResponse object\n", response.text)


def process_user_input(thread_id_client, user_input):

    client.beta.threads.messages.create(thread_id=thread_id_client, role="user",
                                        content=user_input)
    run = client.beta.threads.runs.create(thread_id=thread_id_client,
                                          assistant_id=assistant_id)
    print("Run started with ID:", run.id)
    return run


def get_run_status(thread_id_client, run_id):
    run_status = client.beta.threads.runs.retrieve(thread_id=thread_id_client,
                                                   run_id=run_id)
    print("Checking run status:", run_status.status)
    return run_status


def clean_message_content(message_content):
    annotations = message_content.annotations
    for annotation in annotations:
        message_content.value = message_content.value.replace(
            annotation.text, '')
    return message_content.value


def send_msg_with_retry(message, sender_phone, max_retries=8):
    for attempt in range(1, max_retries + 1):
        try:
            send_msg(message, sender_phone)
            break  # If successful, exit the loop
        except requests.exceptions.ConnectionError as e:
            print(f"Retry attempt {
                  attempt}/{max_retries} - Connection error: {e}")
            time.sleep(5)  # Wait for a few seconds before retrying
    else:
        print("Max retries exceeded. Unable to send the message.")


def handle_thread_id(phone_number):
    try:
        row = ThreadDataSixHours.get(phone_number)
        thread_id = row.thread_ID
        created_at = row.thread_created_at
        print(f"Thread ID: {thread_id} retrieved for {phone_number}")
        # retrieved_time = datetime.strptime(
        #     created_at, "%Y-%m-%d %H:%M:%S")
        retrieved_time = pytz.utc.localize(created_at)
        print(f"Thread created at: {retrieved_time}")

        current_time_utc = datetime.now(pytz.utc)
        print(f"Current time: {current_time_utc}")
        time_difference = current_time_utc - retrieved_time
        if time_difference > timedelta(hours=6):
            print("More than 6 hours have elapsed since this thread was created. Creating a new thread ID.")
            thread_id = client.beta.threads.create().id

            print(f"Thread ID: {thread_id} created for {phone_number}")
            return thread_id, True, datetime.now(pytz.utc)
        else:
            print("6 hours have not elapased since this thread was created. Using the same thread ID.")

            return thread_id, created_at
    except ThreadDataSixHours.DoesNotExist:
        thread_id = client.beta.threads.create().id

        print(f"\n\n We have a new user! Thread ID: {thread_id} created for {phone_number}")
        return thread_id, True, datetime.now(pytz.utc)


def handler():
    while True:
        res = res_q.get()
        sender_phone = res['entry'][0]['changes'][0]['value']['messages'][0]['from']
        send_msg_with_retry(
            "Please wait while I process your request.", sender_phone)
        user_input = res['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']

        test_vector = vectorizer.transform([user_input])
        prediction = model.predict(test_vector)

        thread_id_client, new_thread_created = handle_thread_id(sender_phone)

        if (prediction[0] == 0):
            user_input = "Answer in English. " + user_input
        else:
            user_input = "Answer in Roman Urdu. " + user_input

        print("\nGot message from ", sender_phone)
        print("The message is ", user_input, "\n")

        # thread_id_client = client.beta.threads.create().id
        run = process_user_input(thread_id_client, user_input)

        start_time = time.time()
        while time.time() - start_time < 120:
            run_status = get_run_status(thread_id_client, run.id)
            if run_status.status == 'completed':
                messages = client.beta.threads.messages.list(
                    thread_id=thread_id_client)
                message_content = clean_message_content(
                    messages.data[0].content[0].text)
                print("Run completed, returning response to ", sender_phone)
                print("\nResponse:", message_content)
                send_msg_with_retry(message_content, sender_phone)
                break
            time.sleep(1)

        if run_status.status != 'completed':
            print("Run timed out")
            send_msg_with_retry(
                "Sorry, I'm having trouble understanding you. Please try again.", sender_phone)

        ThreadDataSixHours(message_id=res['entry'][0]['changes'][0]['value']['messages'][0]['id'],
                           incoming_message=user_input, reply=message_content, thread_ID=thread_id_client, phone_number=sender_phone).save()


my_thread = threading.Thread(target=handler)
my_thread.daemon = True
my_thread.start()


@app.route('/webhooks', methods=['POST', 'GET'])
def webhook():
    res = request.get_json()
    try:
        message = res['entry'][0]['changes'][0]['value']['messages'][0]
        msg_type, msg_id, msg_timestamp = message['type'], message['id'], int(
            message['timestamp'])
        if msg_type == 'text' and msg_id not in res_id_list and time.time() - msg_timestamp < 100:
            print("\nCurrent time:", time.time())
            print("\nMessage time:", int(
                res['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']))
            res_id_list.append(res['entry'][0]['changes']
                               [0]['value']['messages'][0]['id'])
            res_q.put(res)
    except KeyError:
        pass
    return '200 OK HTTPS.'


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5002)


# the messages received from the user at the webhook endpoint have the following format:
# {
#   "object": "whatsapp_business_account",
#   "entry": [{
#     "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
#     "changes": [{
#       "value": {
#         "messaging_product": "whatsapp",
#         "metadata": {
#           "display_phone_number": PHONE_NUMBER,
#           "phone_number_id": PHONE_NUMBER_ID
#         },
#         "contacts": [{
#           "profile": {
#             "name": "NAME"
#           },
#           "wa_id": PHONE_NUMBER
#         }],
#         "messages": [{
#           "from": PHONE_NUMBER,
#           "id": "wamid.ID",
#           "timestamp": TIMESTAMP,
#           "text": {
#             "body": "MESSAGE_BODY"
#           },
#           "type": "text"
#         }]
#       },
#       "field": "messages"
#     }]
#   }]
# }
