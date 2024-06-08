import pytz
from datetime import datetime, timedelta
from joblib import load
import os
from dotenv import load_dotenv
from waitress import serve
import queue
import threading
import json
import time
from openai import OpenAI
import requests
from flask import Flask, request
import pymongo

# Load environment variables from .env file
load_dotenv()

# Connect to the MongoDB cluster
mongo_client = pymongo.MongoClient(os.getenv('MONGODB_URI'))

# Access the database and collections
db = mongo_client["Maternal_Health"]
# This collection stores the thread ID, incoming message, reply and phone number of the every message
collection_threads = db["Thread_info"]
# this collection stores the phone number and thread ID of the user along with the creation time of the thread. This is used to check if 6 hours have elapsed since the thread was created and renew the thread ID if necessary
collection_users = db["UserData"]

# Access the environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
WHATSAPP_TOKEN = os.getenv('WHATSAPP_PERMANENT_ACCESS_TOKEN')

# Create a queue to store the incoming messages so that they can be processed by the bot. This is necessary to make sure all messages are processed sequentially
res_q = queue.Queue()
res_id_list = []

# load the trained SVM model and the TfidfVectorizer to classify the user input as English or Roman Urdu and prompt the LLM to respond accordingly
model = load('./model.joblib')
vectorizer = load('./vectorizer.joblib')

# this file stores the assistant ID of the assistant being used
with open('assistant.json') as f:
    assistant_id = json.load(f)['assistant_id']

# Create a Flask app
app = Flask(__name__)

# Create an OpenAI client object 
client = OpenAI(api_key=OPENAI_API_KEY, default_headers={
                "OpenAI-Beta": "assistants=v2"})

print("Using Assistant:", assistant_id)

# Function to send a message to the user using the WhatsApp Cloud API
def send_msg(msg, number, status=False, message_id=None):
    # headers for the response used for API authentication. The token is the permanent access token for the WhatsApp Cloud API
    headers = {
        'Authorization': 'Bearer EAANESMGOCnkBOyqM7wy5b5xDHkUC9urmTz3vH6V7SYiZBxNnmianZARMpZCjqvZAnXVVN0Cp6TC0fSojyN86cg8ygk83TuHx3lZAt5wdqtjKCyYjhjdPyI82sZBG4oZCZAKyoEZCbkVZC9aWLVVkmiWtVrLAn6DdStZBUGcbg4wVYFNCmJjASBuVIJcpYw84ZAl7',
    }
    if not status:
        # Create a dictionary with the message to be sent to the user
        json_data = {
            'messaging_product': 'whatsapp',
            'to': number,
            'type': 'text',
            "text": {
                "body": msg
            }
        }
    else: 
        # send a read receipt to the user
        json_data = {
            'messaging_product': 'whatsapp',
            'status': "read",
            'message_id': message_id,
        }
    # Sending the POST request to the WhatsApp API endpoint. The /messages endpoint is used to send messages to the user
    response = requests.post(
        'https://graph.facebook.com/v18.0/220890917766697/messages', headers=headers, json=json_data)
    # print("\nResponse object\n", response.text)

# Function to process the user input and send it to the LLM for a response
def process_user_input(thread_id_client, user_input, name):
    # Create a message in the thread with the user input
    client.beta.threads.messages.create(thread_id=thread_id_client, role="user",
                                        content=user_input)
    # run the assistant with the user input and poll the response.
    run = client.beta.threads.runs.create_and_poll(thread_id=thread_id_client,
                                                   assistant_id=assistant_id, instructions=f"Embody a Pakistani menstrual health expert and provide accurate information on the user's query using the uploaded knowledge file and your own knowledge. Refer to this user as {name} and keep your responses short and concise without using formatting like bold, italics etc. Do not answer queries that are not related to menstrual or female health.")
    
    print("Run with ID:", run.id)
    return run

# This function is used to clean the message content by removing any annotations that are present in the message
def clean_message_content(message_content):
    annotations = message_content.annotations
    for annotation in annotations:
        message_content.value = message_content.value.replace(
            annotation.text, '')
    return message_content.value


# Function to send a message to the user with retries in case of a connection error
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

# this function is used to check if 6 hours have elapsed since the thread was created and renew the thread ID if necessary
def handle_thread_id(phone_number):
    row = collection_users.find_one({"phone_number": phone_number})

    if row is not None:
        thread_id = row["thread_ID"]
        print(f"Thread ID: {thread_id} retrieved for {phone_number}")
        
        created_at = row["thread_created_at"]
        # this is used to convert the created_at time to UTC time zone
        if created_at.tzinfo is None:
            created_at = pytz.UTC.localize(created_at)

        current_time_utc = datetime.utcnow().replace(tzinfo=pytz.UTC)

        print(f"Current time: {current_time_utc}")
        print(f"Created at time: {created_at}")

        time_difference = current_time_utc - created_at

        if time_difference > timedelta(hours=6):

            print(
                "More than 6 hours have elapsed since this thread was created. Creating a new thread ID.")
            
            
            thread_id = client.beta.threads.create().id

            print(f"Thread ID: {thread_id} created for {phone_number}")
            user_document = {
                "phone_number": phone_number,
                "thread_ID": thread_id,
                "thread_created_at": datetime.now(pytz.utc)
            }
            result = collection_users.insert_one(user_document)

        else:
            print(
                "6 hours have not elapased since this thread was created. Using the same thread ID.")
    else:
        thread_id = client.beta.threads.create().id
        user_document = {
            "phone_number": phone_number,
            "thread_ID": thread_id,
            "thread_created_at": datetime.now(pytz.utc)
        }
        result = collection_users.insert_one(user_document)
        print(f"\n\n We have a new user! Thread ID: {thread_id} created for {phone_number}")
    return thread_id

# this function gets the requests from the queue and processes them in a thread that keeps running
def handler():
    while True:
        # get an incoming message from the queue
        res = res_q.get()
        sender_phone = res['entry'][0]['changes'][0]['value']['messages'][0]['from']
        
        # send a read receipt to the user
        send_msg("", sender_phone, status=True, message_id=res['entry'][0]['changes'][0]['value']['messages'][0]['id'])

        print("\nGot message from ", sender_phone)
        user_input = res['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        print("The message is ", user_input, "\n")

        # classify the user input as English or Roman Urdu
        test_vector = vectorizer.transform([user_input])
        prediction = model.predict(test_vector)

        # get the thread ID for the user (old or new)
        thread_id_client = handle_thread_id(sender_phone)

        prompt = "System: You are a menstrual health expert based in Pakistan with great knowledge related to menstrual health. Make sure your answer is accurate, concise, aware of Pakistani context and less than 120 words. If the query is not related to menstrual health or female health, politely decline to answer. Use the provided knowledge file and your own knowledge as well to answer the following user query. \nUser: "

        if (prediction[0] == 0):
            user_input = "Answer in English. " + prompt + user_input
        else:
            user_input = "Answer in Roman Urdu. " + prompt + user_input

        name = res['entry'][0]['changes'][0]['value']['contacts'][0]["profile"]["name"]
        run = process_user_input(thread_id_client, user_input, name)

        if run.status == 'completed':
            messages = client.beta.threads.messages.list(
                thread_id=thread_id_client)
            message_content = clean_message_content(
                messages.data[0].content[0].text)
            send_msg_with_retry(message_content, sender_phone)
            print("Run completed, returning response to ", sender_phone)
            print("\nResponse:", message_content)
        else:
            print("Run not completed")
            send_msg_with_retry(
                "Sorry, I'm having trouble understanding you. Please try again.", sender_phone)

        # thread_document = {
        #     "message_id": res['entry'][0]['changes'][0]['value']['messages'][0]['id'],
        #     "incoming_message": user_input,
        #     "reply": message_content,
        #     "thread_ID": thread_id_client,
        #     "phone_number": sender_phone
        # }
        
        found = collection_threads.find_one({"thread_ID": thread_id_client})
        
        if found:
            collection_threads.update_one({"thread_ID": thread_id_client},{"$push": {"conversation": {"incoming_message": user_input, "reply": message_content}}})
            print("Inserted conversation in DB")
        else:
        
            thread_document = {
                "message_id": res['entry'][0]['changes'][0]['value']['messages'][0]['id'],
                "conversation": [{"incoming_message": user_input, "reply": message_content}],
                "thread_ID": thread_id_client,
                "phone_number": sender_phone
            }
            result = collection_threads.insert_one(thread_document)
            print("Inserted new thread document with ID:", result.inserted_id)
        
        






# Create a thread to handle the incoming messages
my_thread = threading.Thread(target=handler)
my_thread.daemon = True
my_thread.start()

# This endpoint is used to receive messages from the user at the webhook and store them in a queue for processing
@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    res = request.get_json()
    try:
        message = res['entry'][0]['changes'][0]['value']['messages'][0]
        msg_type, msg_id, msg_timestamp = message['type'], message['id'], int(
            message['timestamp'])
        
        # this is done to make sure the very old messages are not processed
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
