import random
import google.generativeai as genai 
import math
from dotenv import load_dotenv
import os


scam_templates = [
    "【國泰世華】您的銀行賬戶顯示異常，請立即登入綁定用戶資料，否則賬戶將凍結使用 www.cathay-bk.com",
    "我朋友參加攝影比賽麻煩幫忙投票 http://www.yahoonikk.info/page/vote.pgp?pid=51",
    "登入FB就投票成功了我手機當機 line用不了 想請你幫忙安全認證 幫我收個認證簡訊 謝謝 你LINE的登陸認證密碼記得嗎 認證要用到 確認是本人幫忙認證",
    "您的LINE已違規使用，將在24小時內註銷，請使用谷歌瀏覽器登入電腦網站並掃碼驗證解除違規 www.line-wbe.icu",
    "【台灣自來水公司】貴戶本期水費已逾期，總計新台幣395元整，務請於6月16日前處理繳費，詳情繳費：https://bit.ly/4cnMNtE 若再超過上述日期，將終止供水",
    "萬聖節快樂🎃 活動免費貼圖無限量下載 https://lineeshop.com",
    "【台灣電力股份有限公司】貴戶本期電費已逾期，總計新台幣1058元整，務請於6月14日前處理繳費，詳情繳費：(網址)，若再超過上述日期，將停止收費"
]

load_dotenv()

gemini_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=gemini_key)

def generate_examples():
    scam_template = random.choice(scam_templates)
    prompt_scam = (
        f"以下是一個詐騙訊息範例:\n\n{scam_template}\n\n"
        "請根據這個範例生成一個新的、類似的詐騙訊息。保持相似的結構和風格，"
        "但改變具體內容。請確保新生成的訊息具有教育性質，可以用於提高人們對詐騙的警惕性。"
        "只需要生成詐騙訊息本身，不要添加任何額外的說明或指示。"
    )
    prompt_correct = (
        f"請生成一個真實且正確的訊息範例，其風格和結構類似於以下的詐騙訊息範例，但內容是真實且正確的:\n\n{scam_template}"
    )

    model = genai.GenerativeModel('gemini-pro')
    choice=math.floor(random.random()*10%2)
    if choice ==0:
        scam_response = model.generate_content(prompt_scam)
        return scam_response.text.strip(), True
    else:
        correct_response = model.generate_content(prompt_correct)
        return correct_response.text.strip(), False #, correct_response.text.strip()

def analyze_response(text, is_scam):
    # 如果用户回答正确
    if is_scam:
        prompt = (
            f"以下是一個詐騙訊息:\n\n{text}\n\n"
            "請分析這條訊息，並提供詳細的辨別建議。包括以下幾點：\n"
            "1. 這條訊息中的可疑元素\n"
            "2. 為什麼這些元素是可疑的\n"
            "3. 如何識別類似的詐騙訊息\n"
            "4. 面對這種訊息時應該採取什麼行動\n"
            "請以教育性和提醒性的語氣回答，幫助人們提高警惕。"
            "不要使用任何粗體或任何特殊格式，例如＊或是-，不要使用markdown語法，只需使用純文本。不要使用破折號，而是使用數字列表。"
        )
    else:
        prompt = (
            f"以下是一個真實且正確的訊息:\n\n{text}\n\n"
            "請分析這條訊息，並提供詳細的辨別建議。包括以下幾點：\n"
            "1. 這條訊息中的真實元素\n"
            "2. 為什麼這些元素是真實的\n"
            "3. 如何識別類似的真實訊息\n"
            "4. 面對這種訊息時應該採取什麼行動\n"
            "請以教育性和提醒性的語氣回答，幫助人們提高辨別真實訊息的能力。"
            "不要使用任何粗體或任何特殊格式，例如＊或是-，不要使用markdown語法，只需使用純文本。不要使用破折號，而是使用數字列表。"
        )
  
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text.strip()