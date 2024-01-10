


from flask import Flask, request
import requests
import openai
from openai import OpenAI
import jsonify
import os
from packaging import version
from decouple import config
import functions
import time

current_version = version.parse(openai.__version__)
OPENAI_API_KEY = config('OPENAI_API_KEY')

print("Current version: ", current_version)
app = Flask(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)

assistant_id = functions.create_assistant(client)
print("Assistant created with ID:", assistant_id)

# def start_conversation():
thread = client.beta.threads.create()
print("New conversation started with thread ID:", thread.id)
# return jsonify({"thread_id": thread.id})

# def chat(request):
#   data = request.json
#   thread_id = data.get('thread_id')
#   user_input = data.get('message', '')
#   if not thread_id:
#     print("Error: Missing thread_id in /chat")
#     return jsonify({"error": "Missing thread_id"}), 400
#   print("Received message for thread ID:", thread_id, "Message:", user_input)

#   # Start run and send run ID back to ManyChat
#   client.beta.threads.messages.create(thread_id=thread_id,
#                                       role="user",
#                                       content=user_input)
#   run = client.beta.threads.runs.create(thread_id=thread_id,
#                                         assistant_id=assistant_id)
#   print("Run started with ID:", run.id)
#   return jsonify({"run_id": run.id})


def check_run_status(run_id, thread_id):

  # Start timer ensuring no more than 9 seconds, ManyChat timeout is 10s
  start_time = time.time()
  print("In run status check, with start time:", start_time)
  while time.time() - start_time < 30:
    run_status = client.beta.threads.runs.retrieve(thread_id=thread_id,
                                                   run_id=run_id)
    print("Checking run status:", run_status.status)

    if run_status.status == 'completed':
      messages = client.beta.threads.messages.list(thread_id=thread_id)
      message_content = messages.data[0].content[0].text
      # Remove annotations
      annotations = message_content.annotations
      for annotation in annotations:
        message_content.value = message_content.value.replace(
            annotation.text, '')
      print("Run completed, returning response")
      send_msg(message_content.value)
    #   return
    #   return jsonify({
    #       "response": message_content.value,
    #       "status": "completed"
    #   })
    
    time.sleep(1)

  print("Run timed out")
  send_msg("Sorry, I'm having trouble understanding you. Please try again.")
#   return
#   return jsonify({"response": "timeout"})

 
@app.route('/')
def index():
   return "Hello"
 
def send_msg(msg, number):
   headers = {
       'Authorization': 'Bearer EAANESMGOCnkBOyqM7wy5b5xDHkUC9urmTz3vH6V7SYiZBxNnmianZARMpZCjqvZAnXVVN0Cp6TC0fSojyN86cg8ygk83TuHx3lZAt5wdqtjKCyYjhjdPyI82sZBG4oZCZAKyoEZCbkVZC9aWLVVkmiWtVrLAn6DdStZBUGcbg4wVYFNCmJjASBuVIJcpYw84ZAl7',
   }
   json_data = {
       'messaging_product': 'whatsapp',
       'to': number,
       'type': 'text',
       "text": {
           "body": msg
       }
   }
   response = requests.post('https://graph.facebook.com/v18.0/220890917766697/messages', headers=headers, json=json_data)
   print(response.text)
 
 
@app.route('/webhooks', methods=['POST','GET'])
def webhook():
   print(request)
   res = request.get_json()
   
   print(res)
   
   
   
   try:
       if res['entry'][0]['changes'][0]['value']['messages'][0]['id']:
            user_input = res['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
            client.beta.threads.messages.create(thread_id=thread.id,
                                      role="user",
                                      content=user_input)
            run = client.beta.threads.runs.create(thread_id=thread.id,
                                        assistant_id=assistant_id)
            print("Run started with ID:", run.id)
            print("Calling check_run_status")
            # check_run_status(run.id, thread.id)
            start_time = time.time()
            print("In run status check, with start time:", start_time)
            run_status = client.beta.threads.runs.retrieve(thread_id=thread.id,
                                                            run_id=run.id)
            while time.time() - start_time < 120:
                run_status = client.beta.threads.runs.retrieve(thread_id=thread.id,
                                                            run_id=run.id)
                print("Checking run status:", run_status.status)

                if run_status.status == 'completed':
                    messages = client.beta.threads.messages.list(thread_id=thread.id)
                    message_content = messages.data[0].content[0].text
                    # Remove annotations
                    annotations = message_content.annotations
                    for annotation in annotations:
                        message_content.value = message_content.value.replace(
                            annotation.text, '')
                    print("Run completed, returning response to ", res['entry'][0]['changes'][0]['value']['messages'][0]['from'])
                    send_msg(message_content.value, res['entry'][0]['changes'][0]['value']['messages'][0]['from'])
                    break
                    #   return
                    #   return jsonify({
                    #       "response": message_content.value,
                    #       "status": "completed"
                    #   })
                
                time.sleep(1)
            if run_status.status != 'completed':
                print("Run timed out")
                send_msg("Sorry, I'm having trouble understanding you. Please try again.", res['entry'][0]['changes'][0]['value']['messages'][0]['from'])
            
            # send_msg("Thank you for the response.")
   except:
       pass
   return '200 OK HTTPS.'
 
  
if __name__ == "__main__":
   app.run(debug=True, port=5002)