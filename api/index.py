from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from api.chatgpt import ChatGPT
from flask import Flask, request, abort ,redirect
from linebot.models import *
import os

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFALUT_TALKING", default = "true").lower() == "true"
LIFF_URL = 'https://liff.line.me/1660673627-bwvxxAzm'
web_url = 'https://chat.openai.com/chat'

app = Flask(__name__)
chatgpt = ChatGPT()

@app.route("/liff", methods=['GET'])
def liff():
    redirect_url = request.args.get('redirect_url')

    return redirect(redirect_url)
# domain root
@app.route('/')
def home():
    return 'Hello, World!'

@app.route("/webhook", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global working_status
    
    if event.message.type != "text":
        return
    
    if event.message.text == "啟動":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我是時下流行的AI智能，目前可以為您服務囉，歡迎來跟我互動~"))
        return

    if event.message.text == "安靜":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="感謝您的使用，若需要我的服務，請跟我說 「啟動」 謝謝~"))
        return
    
    if working_status:
        chatgpt.add_msg(f"Human:{event.message.text}?\n")
        reply_msg = chatgpt.get_response().replace("AI:", "", 1)
        chatgpt.add_msg(f"AI:{reply_msg}\n")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_msg))
        
    print("event.reply_token:", event.reply_token)
    print("event.message.text:", event.message.text)
   
    message = TemplateSendMessage(
            alt_text='使用ChatGPT',
            template=ButtonsTemplate(
                text='🌸🌸 我想使用ChatGPT 🌸🌸',
                thumbnail_image_url='https://i.imgur.com/2rt3YMq.png',
                actions=[
                    URIAction(label='ChatGPT',
                              uri=LIFF_URL)
                ]))

    line_bot_api.reply_message(event.reply_token, [message])
    

if __name__ == "__main__":
    app.run()
