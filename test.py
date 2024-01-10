from flask import Flask, request
import requests
import openai

openai.api_key = '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'

app = Flask(__name__)
 
def send_msg(msg,receiver_number):

   headers = {
       'Authorization': 'Bearer EAANESMGOCnkBO97EXF3EwHmPWEnSDJCuW6Xkd0RVVSJ5zcA8jPWA2fZAWSpd3gsCHfawIZBDZAHlhbaxRdaR7AOZBAuq1Jpg9PCyyeJKEOCJxAeL7USP9BYY7ZBSeVRbvWDsRZCgTUIwfkqJP6O4ZARp6ZBSFIMDVcR12f66ekS0DNcb7jUi5uli4nzrP3JAemCiMdnkJ56ufstsV24ZD',
   }
   json_data = {
       'messaging_product': 'whatsapp',
       'to': receiver_number,
       'type': 'text',
       "text": {
           "body": msg
       }
   }
   response = requests.post('https://graph.facebook.com/LATEST-API-VERSION/PHONE_NUMBER_ID/messages', headers=headers, json=json_data)
   print(response.text)
 

@app.route('/receive_msg', methods=['POST','GET'])
# @app.route('/receive_msg', methods=['POST','GET'])
def webhook():
   res = request.get_json()
   print(res)
   try:
       if res['entry'][0]['changes'][0]['value']['messages'][0]['id']:
            chat_gpt_input=res['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
            completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": chat_gpt_input}]
            )
            response = completion['choices'][0]['message']['content']
            print("ChatGPT Response=>",response)
            receiver_number=res['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
            send_msg(response,receiver_number)
   except:
       pass
   return '200 OK HTTPS.'
 
  
if __name__ == "__main__":
   app.run(debug=True)