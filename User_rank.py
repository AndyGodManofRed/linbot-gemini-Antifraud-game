from firebase import firebase
import os
import pygame


# 取得環境變數中的Channel Access Token
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

def get_sorted_scores(firebase_url,path):

    fdb = firebase.FirebaseApplication(firebase_url, None)
    # 從 Firebase 獲取 score 節點下的所有資料
    scores = fdb.get(path, None)
    
    if scores:
        # 將資料轉換成 (user, score) 的列表
        score_list = [(user, score) for user, score in scores.items()]
        # 按照分數進行排序，從高到低
        sorted_score_list = sorted(score_list, key=lambda x: x[1], reverse=True)
        return sorted_score_list
    else:
        return []


from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import ImageSendMessage
import requests
import pygame

# 初始化LineBotApi
line_bot_api = LineBotApi(channel_access_token)
def get_user_profile(user_id):
    try:
        # 使用LineBotApi的get_profile方法來獲取使用者資料
        profile = line_bot_api.get_profile(user_id)
        return profile.display_name  # 返回使用者的顯示名稱
    except LineBotApiError as e:
        print("LineBotApiError:", e)
        return None


def get_rank(current_user_id,firebase_url):

    # 設定表格的欄位寬度
    rank_width = 7
    user_width = 14
    score_width = 11
    total_width = rank_width + user_width + score_width + 4  # 包括分隔符號

    sorted_scores = get_sorted_scores(firebase_url, 'scores/')

    # 初始化表格字串
    table_str = ''

    # 表格頂部邊界
    table_str += '+' + '-' * total_width + '+\n'
    table_str += '|' + "排行榜".center(total_width-3) + '|\n'
    table_str += '+' + '-' * total_width + '+\n'
    table_str += f"|{'排名'.center(rank_width)}|{'User'.center(user_width)}|{'Score'.center(score_width)}|\n"
    table_str += '+' + '-' * rank_width + '+' + '-' * user_width + '+' + '-' * score_width + '+\n'

    if sorted_scores:
        i = 1
        for user_id, score in sorted_scores:
            user_name = get_user_profile(user_id)
            if user_name is None:
                user_display = user_id[:5]  # 如果無法取得使用者名稱，顯示部分使用者 ID
            else:
                user_display = user_name[:user_width]

            # 標記當前使用者
            if user_id == current_user_id:
                user_display = f'{user_display}'

            table_str += f"|{str(i).center(rank_width)}|{user_display.center(user_width)}|{str(score).center(score_width)}|\n"
            table_str += '+' + '-' * rank_width + '+' + '-' * user_width + '+' + '-' * score_width + '+\n'
            i += 1
    else:
        table_str += '|' + '目前無人上榜'.center(total_width) + '|\n'
        table_str += '+' + '-' * total_width + '+\n'
    return table_str

def safe_table_as_file(table, user_id):
    pygame.init()
    font = pygame.font.Font("ChenYuluoyan-Thin-Monospaced.ttf", 16)

    lines = table.splitlines()
    line_height = font.size("Test")[1]
    image_height = len(lines) * line_height
    image = pygame.Surface((400, image_height))
    image.fill((0, 0, 0))

    y = 0
    for line in lines:
        ftext = font.render(line, True, (255, 255, 255))
        image.blit(ftext, (0, y))
        y += line_height

    image_path = "image.jpg"
    pygame.image.save(image, image_path)

    # 上傳圖片到 Imgur
    imgur_client_id = os.getenv('IMGUR_CLIENT_ID')
    headers = {"Authorization": f"Client-ID {imgur_client_id}"}
    with open(image_path, 'rb') as img:
        response = requests.post(
            "https://api.imgur.com/3/upload",
            headers=headers,
            files={"image": img}
        )
    
    if response.status_code == 200:
        image_url = response.json()['data']['link']
        send_image_to_user(user_id, image_url)
        # 刪除本地存儲的圖片
        # os.remove(image_path)
    else:
        print("Failed to upload image to Imgur")
        # 如果上傳失敗，可以根據需要選擇是否刪除圖片
        # os.remove(image_path)

def send_image_to_user(user_id, image_url):
    try:
        line_bot_api.push_message(
            user_id,
            ImageSendMessage(
                original_content_url=image_url,
                preview_image_url=image_url
            )
        )
    except LineBotApiError as e:
        print(f"LineBotApiError: {e}")



        

if __name__ == "__main__":
    user_id = 'U89390a25e48b5b42b2f789317291eb27'
    firebase_url=os.getenv("FIREBASE_URL")
    leaderboard_str=get_rank(user_id,firebase_url)
    safe_table_as_file(leaderboard_str,user_id)