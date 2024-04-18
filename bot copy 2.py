import sys
sys.path.append("c:\\users\\waleed arshad\\appdata\\local\\programs\\python\\python312\\lib\\site-packages")
sys.path.append("c:\\users\\waleed arshad\\appdata\\local\\programs\\python\\python312\\lib\\site-packages\\decouple\\__init__.py")
from flask import Flask, request
import requests
from openai import OpenAI
# from decouple import config
import time
import json
import pynamodb
from pynamodb.models import Model
import threading
import queue
from waitress import serve
from dotenv import load_dotenv
import os
from joblib import load

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

class User_data(Model):
    class Meta:
        table_name = 'User_data_IML_DRP'
        region = 'us-east-1'
        aws_access_key_id = AWS_ACCESS_KEY_ID
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY
    # hash key = True means this is the primary key
    message_id = pynamodb.attributes.UnicodeAttribute(hash_key=True)
    incoming_message = pynamodb.attributes.UnicodeAttribute()
    reply = pynamodb.attributes.UnicodeAttribute()

class User_threads(Model):
    class Meta:
        table_name = 'thread_data_IML_DRP'
        region = 'us-east-1'
        aws_access_key_id = AWS_ACCESS_KEY_ID
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY
    phone_number = pynamodb.attributes.UnicodeAttribute(hash_key=True)
    thread_ID = pynamodb.attributes.UnicodeAttribute()

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

def handle_thread_id(phone_number):
    try:
        thread_id = User_threads.get(phone_number).thread_ID
        print(f"Thread ID: {thread_id} retrieved for {phone_number}")
        return thread_id
    except User_threads.DoesNotExist:
        thread_id = client.beta.threads.create().id
        User_threads(phone_number=phone_number, thread_ID=thread_id).save()
        print(f"Thread ID: {thread_id} created for {phone_number}")
        return thread_id

def process_user_input(thread_id_client, user_input):
    client.beta.threads.messages.create(thread_id=thread_id_client,
                                        role="user",
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
        message_content.value = message_content.value.replace(annotation.text, '')
    return message_content.value


def send_msg_with_retry(message, sender_phone, max_retries=8):
    for attempt in range(1, max_retries + 1):
        try:
            send_msg(message, sender_phone)
            break  # If successful, exit the loop
        except requests.exceptions.ConnectionError as e:
            print(f"Retry attempt {attempt}/{max_retries} - Connection error: {e}")
            time.sleep(5)  # Wait for a few seconds before retrying
    else:
        print("Max retries exceeded. Unable to send the message.")

def handler():
    while True:
        # print("In handler ")
        res = res_q.get()
        # print("Got request ")
        # print("Got request ")
        sender_phone = res['entry'][0]['changes'][0]['value']['messages'][0]['from']
        send_msg_with_retry("Please wait while I process your request.", sender_phone)
        send_msg_with_retry("Please wait while I process your request.", sender_phone)

        thread_id_client = handle_thread_id(sender_phone)
        user_input = res['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        
        test_vector = vectorizer.transform([user_input])
        prediction = model.predict(test_vector)
        
        if (prediction[0] == 0):
            user_input = "Answer in English. " + user_input
        else:
            user_input = "Answer in Roman Urdu. " + user_input
            
        print("\nGot message from ", sender_phone)
        print("The message is ", user_input, "\n")
        
        run = process_user_input(thread_id_client, user_input)
        
        

        start_time = time.time()
        while time.time() - start_time < 120:
            run_status = get_run_status(thread_id_client, run.id)
            if run_status.status == 'completed':
                messages = client.beta.threads.messages.list(thread_id=thread_id_client)
                message_content = clean_message_content(messages.data[0].content[0].text)
                print("Run completed, returning response to ", sender_phone)
                print("\nResponse:", message_content)
                send_msg_with_retry(message_content, sender_phone)
                break
            time.sleep(1)

        if run_status.status != 'completed':
            print("Run timed out")
            send_msg_with_retry("Sorry, I'm having trouble understanding you. Please try again.", sender_phone)
        
        User_data(message_id=res['entry'][0]['changes'][0]['value']['messages'][0]['id'],
                  incoming_message=user_input, reply=message_content).save()


my_thread = threading.Thread(target=handler)
my_thread.daemon = True
my_thread.start()

@app.route('/webhooks', methods=['POST', 'GET'])
def webhook():
    # print("\nRequest object\n", request)
    res = request.get_json()

    # print("\nPayload\n", res)
    try:
        message = res['entry'][0]['changes'][0]['value']['messages'][0]
        msg_type, msg_id, msg_timestamp = message['type'], message['id'], int(message['timestamp'])
        if msg_type == 'text' and msg_id not in res_id_list and time.time() - msg_timestamp < 100:
            print("\nCurrent time:", time.time())
            print("\nMessage time:", int(
                res['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']))
            res_id_list.append(res['entry'][0]['changes']
                               [0]['value']['messages'][0]['id'])
            res_q.put(res)
            # print("\nRes Queue\n", res_q.queue)
            # for i in list(res_q.queue):
            #     print(i)
            # print("\nRes id list\n", res_id_list)

    except KeyError:
        # print("Key error")
        pass
    return '200 OK HTTPS.'


if __name__ == "__main__":
    # app.run(debug=True, port=5002)
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
