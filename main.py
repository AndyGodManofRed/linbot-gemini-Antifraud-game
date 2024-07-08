from fastapi import FastAPI, HTTPException, Request
import logging
import os
import sys
from dotenv import load_dotenv
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ConfirmTemplate, MessageAction, TemplateSendMessage
)
from firebase import firebase
import random
import uvicorn
import google.generativeai as genai
from User_rank import *
from gemini_g_respond import *

logging.basicConfig(level=os.getenv('LOG', 'WARNING'))
logger = logging.getLogger(__file__)

app = FastAPI()

load_dotenv()
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None or channel_access_token is None:
    logger.error('Specify LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN as environment variables.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

firebase_url = os.getenv('FIREBASE_URL')



@app.get("/health")
async def health():
    return 'ok'

@app.post("/webhooks/line")
async def handle_callback(request: Request):
    signature = request.headers['X-Line-Signature']
    body = await request.body()
    body = body.decode()

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if not isinstance(event, MessageEvent) or not isinstance(event.message, TextMessage):
            continue

        user_id = event.source.user_id
        fdb = firebase.FirebaseApplication(firebase_url, None)
        user_score_path = f'scores/{user_id}'
        user_score = fdb.get(user_score_path, None) or 0

        if event.message.text == '出題':
            #scam_example, correct_example = generate_examples()
            example, is_scam = generate_examples()
            messages = [{'role': 'bot', 'parts': example,'scam':is_scam}]
            fdb.put_async(f'chat/{user_id}', None, messages)
            reply_msg = f"{example}\n\n請判斷這是否為詐騙訊息"
            confirm_template = ConfirmTemplate(
                text='請判斷是否為詐騙訊息。',
                actions=[
                    MessageAction(label='是', text='是'),
                    MessageAction(label='否', text='否')
                ]
            )
            template_message = TemplateSendMessage(alt_text='出題', template=confirm_template)
            line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=reply_msg), template_message])
        elif event.message.text == '分數':
            reply_msg = f"你的當前分數是：{user_score}分"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))

        elif event.message.text in ['是', '否']:
            chatgpt = fdb.get(f'chat/{user_id}', None)
            if chatgpt and chatgpt[-1]['role'] == 'bot':
                #scam_message, correct_message = chatgpt[-1]['parts']
                scam_message = chatgpt[-1]['parts']
                is_scam = chatgpt[-1]['scam']
                user_response = event.message.text

                if (user_response == '是' and is_scam == True) or (user_response == "否" and is_scam == False):
                    user_score += 50
                    fdb.put_async(user_score_path, None, user_score)
                    reply_msg = f"你好棒！你的當前分數是：{user_score}分"
                else:
                    user_score -= 50
                    if user_score < 50:
                        user_score = 0
                    fdb.put_async(user_score_path, None, user_score)
                    reply_msg = f"這是{'詐騙' if is_scam else '正確'}訊息。\n\n你的當前分數是：{user_score}分"
            else:
                reply_msg = '請先輸入「出題」生成一個範例。'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))

        elif event.message.text == "解析":
            chatgpt = fdb.get(f'chat/{user_id}', None)
            example = chatgpt[-1]['parts']
            is_scam = chatgpt[-1]['scam']
            user_response = event.message.text
            
            if chatgpt and chatgpt[-1]['role'] == 'bot':
                advice = analyze_response(example , is_scam)
                reply_msg = f"這是{'詐騙' if is_scam else '正確'}訊息。分析如下:\n\n{advice}"

            else:
                reply_msg = '目前沒有可供解析的訊息，請先輸入「出題」生成一個範例。'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))

        elif event.message.text == "排行榜":
            leaderboard = get_rank(user_id, firebase_url)
            safe_table_as_file(leaderboard,user_id)
        

    return 'OK'


if __name__ == "__main__":
    uvicorn.run(app, port=8080)