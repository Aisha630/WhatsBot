from dynamo import UserData, ThreadData, ThreadLessData, ThreadDataSixHours
from openai import OpenAI
import os
from dotenv import load_dotenv
# the user data table has message_id, incoming_message and reply attributes
# the thread data table has phone_number and thread_ID attributes
# the thread less data table has phone_number, message_id, incoming_message, reply and thread_ID attribute
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

thread_data_phone_numbers = set()
thread_less_data_phone_numbers = set()
thread_six_hours_data_phone_numbers = set()
message_count = {}

# Here what I do is that for each of the thread ids in the table, i retreive the lsit of messages sent on that thread from open AI, and then I store in the dicitonary the number of messages sent by each user against their phone number
for item in ThreadData.scan(attributes_to_get=["phone_number", "thread_ID"]):
    thread_data_phone_numbers.add(item.phone_number)
    if item.phone_number not in message_count:
        message_count[item.phone_number] = len( client.beta.threads.messages.list(item.thread_ID).data)
    else:
        message_count[item.phone_number] += len( client.beta.threads.messages.list(item.thread_ID).data)


# Since this table already has only 1 message for each thread what I am doing here is that I am just counting the number of messages sent by each user and storing it in the dictionary
for item in ThreadLessData.scan(attributes_to_get=["phone_number"]):
    thread_less_data_phone_numbers.add(item.phone_number)
    if item.phone_number not in message_count:
        message_count[item.phone_number] = 1
    else:
        message_count[item.phone_number] += 1
        
        
for item in ThreadDataSixHours.scan(attributes_to_get=["phone_number"]):
    thread_six_hours_data_phone_numbers.add(item.phone_number)
    if item.phone_number not in message_count:
        message_count[item.phone_number] = 1
    else:
        message_count[item.phone_number] += 1
        


    
# Calculate the count of unique users across both tables
unique_users_count = len(thread_data_phone_numbers.union(thread_less_data_phone_numbers).union(thread_six_hours_data_phone_numbers))

print(f"The number of unique users for the assistant with thread context are {len(thread_data_phone_numbers)}")
print(f"The number of unique users for the assistant without context are {len(thread_less_data_phone_numbers)}")
print(f"The number of unique users for the assistant with 6 hour context are {len(thread_six_hours_data_phone_numbers)}")
print(f"The total number of unique users for the assistant is {unique_users_count}")

for key, value in message_count.items():
    print(f"The number of messages sent by {key} is {value}")



