# from flask import Flask, request
# app = Flask(__name__)
 
# @app.route('/webhooks', methods=['POST','GET'])
# def webhook():
#    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
#        print(request.args)
#        if not request.args.get("hub.verify_token")== "bejhgfhrufygyg2738764683heir849iuhfq849q38":
#            return "Verification token missmatch", 403
#        return request.args['hub.challenge'], 200
#    return "Hello world", 200
 
# if __name__ == "__main__":
#    app.run(debug=True, port=5002)


from flask import Flask, request
import requests
 
app = Flask(__name__)
 
@app.route('/')
def index():
   return "Hello"
 
def send_msg(msg):
   headers = {
       'Authorization': 'Bearer EAANESMGOCnkBO97EXF3EwHmPWEnSDJCuW6Xkd0RVVSJ5zcA8jPWA2fZAWSpd3gsCHfawIZBDZAHlhbaxRdaR7AOZBAuq1Jpg9PCyyeJKEOCJxAeL7USP9BYY7ZBSeVRbvWDsRZCgTUIwfkqJP6O4ZARp6ZBSFIMDVcR12f66ekS0DNcb7jUi5uli4nzrP3JAemCiMdnkJ56ufstsV24ZD',
   }
   json_data = {
       'messaging_product': 'whatsapp',
       'to': '923357848396',
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
           send_msg("Thank you for the response.")
   except:
       pass
   return '200 OK HTTPS.'
 
  
if __name__ == "__main__":
   app.run(debug=True, port=5002)