from flask import Flask, request
app = Flask(__name__)
 
@app.route('/webhook', methods=['POST','GET'])
def webhook():
    print(request)
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        print(request.args)
        if not request.args.get("hub.verify_token")== "bejhgfhrufygyg2738764683heir849iuhfq849q38":
            return "Verification token missmatch", 403
        return request.args['hub.challenge'], 200
    return "Hello world", 200
 
if __name__ == "__main__":
   app.run(debug=True, port=5002)
