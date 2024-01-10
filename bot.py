from flask import Flask, request
import requests
import openai
from openai import OpenAI
import os
from packaging import version
from decouple import config
import functions
import time
import json
import pynamodb
from pynamodb.models import Model
import threading
import queue


OPENAI_API_KEY = config('OPENAI_API_KEY')
WHATSAPP_TOKEN = config('WHATSAPP_PERMANENT_ACCESS_TOKEN')
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
res_q = queue.Queue()
res_id_list = []






class User(Model):
    class Meta:
        table_name = 'User_data_IML_DRP'
        region = 'us-east-1'
        aws_access_key_id=AWS_ACCESS_KEY_ID
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        
    message_id = pynamodb.attributes.UnicodeAttribute(hash_key=True) ## hash key = True means this is the primary key
    incoming_message = pynamodb.attributes.UnicodeAttribute()
    reply = pynamodb.attributes.UnicodeAttribute()



with open('assistant.json') as f:
    assistant_id = json.load(f)['assistant_id']

# Create a Flask app
app = Flask(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)

print("Using Assistant:", assistant_id)

thread = client.beta.threads.create()
print("New conversation started with thread ID:", thread.id)

@app.route('/')
def index():
    return '200 OK HTTPS.'

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
    print("\nResponse object\n", response.text)
    
    
def handler():
    try:
        while True:
            res = res_q.get()
            
            user_input = res['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
            client.beta.threads.messages.create(thread_id=thread.id,
                                                role="user",
                                                content=user_input)
            run = client.beta.threads.runs.create(thread_id=thread.id,
                                                  assistant_id=assistant_id)
            print("Run started with ID:", run.id)
            # print("Calling check_run_status")
            start_time = time.time()
            # print("In run status check, with start time:", start_time)
            run_status = client.beta.threads.runs.retrieve(thread_id=thread.id,
                                                           run_id=run.id)
            
            send_msg("Please wait while I process your request.",
                     res['entry'][0]['changes'][0]['value']['messages'][0]['from'])
            
            while time.time() - start_time < 120:
                run_status = client.beta.threads.runs.retrieve(thread_id=thread.id,
                                                               run_id=run.id)
                print("Checking run status:", run_status.status)

                if run_status.status == 'completed':
                    messages = client.beta.threads.messages.list(
                        thread_id=thread.id)
                    message_content = messages.data[0].content[0].text
                    # Remove annotations
                    annotations = message_content.annotations
                    for annotation in annotations:
                        message_content.value = message_content.value.replace(
                            annotation.text, '')
                        
                    print("Run completed, returning response to ",
                          res['entry'][0]['changes'][0]['value']['messages'][0]['from'])
                    print("Response:", message_content.value)
                    send_msg(
                        message_content.value, res['entry'][0]['changes'][0]['value']['messages'][0]['from'])
                    break
                time.sleep(1)
            if run_status.status != 'completed':
                print("Run timed out")
                send_msg("Sorry, I'm having trouble understanding you. Please try again.",
                         res['entry'][0]['changes'][0]['value']['messages'][0]['from'])
                
            User(message_id=res['entry'][0]['changes'][0]['value']['messages'][0]['id'], incoming_message=user_input, reply=message_content.value).save()
    except:
        pass


my_thread = threading.Thread(target=handler)
my_thread.daemon = True
my_thread.start()

@app.route('/webhooks', methods=['POST', 'GET'])
def webhook():
    print("\nRequest object\n",request)
    res = request.get_json()
    print("\nPayload\n",res)
    try:
        if res['entry'][0]['changes'][0]['value']['messages'][0]['type'] == 'text' and res['entry'][0]['changes'][0]['value']['messages'][0]['id'] not in res_id_list:
            # my_thread = threading.Thread(target=handler, args=(res,))
            # my_thread.start()
            res_id_list.append(res['entry'][0]['changes'][0]['value']['messages'][0]['id'])
            res_q.put(res)
            print("\nRes Queue\n",res_q)
            # print the queue
            for i in list(res_q.queue):
                print(i)
            print("\nRes id list\n",res_id_list)
            
    except KeyError:
        print("Key error")
        pass
    return '200 OK HTTPS.'
# def webhook():
#     print("\nRequest object\n",request)
#     res = request.get_json()
#     print("\nPayload\n",res)
#     try:
#         if res['entry'][0]['changes'][0]['value']['messages'][0]['type'] == 'text' and res['entry'][0]['changes'][0]['value']['messages'][0]['id'] not in res_id_list:
#             my_thread = threading.Thread(target=handler, args=(res,))
#             my_thread.start()
#     except KeyError:
#         pass
#     return '200 OK HTTPS.'
        
        
    # res_list.append(res)
    # print("\nRes list\n",res_list)
    


if __name__ == "__main__":
    app.run(debug=True, port=5002)


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