from firebase import firebase
import os
import io

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



def get_rank(current_user_id,firebase_url):
        # 設定表格的欄位寬度
        rank_width = 7
        user_width = 11
        score_width = 11
        total_width = rank_width + user_width + score_width + 4  # 包括分隔符號

        sorted_scores = get_sorted_scores(firebase_url,'scores/')

        # 使用 StringIO 模擬字串緩衝區
        output = io.StringIO()

        # 表格頂部邊界
        output.write('+' + '-' * total_width + '+\n')
        output.write('|' + "排行榜".center(total_width) + '|\n')
        output.write('+' + '-' * total_width + '+\n')
        output.write(f"|{'排名'.center(rank_width)}|{'User'.center(user_width)}|{'Score'.center(score_width)}|\n")
        output.write('+' + '-' * rank_width + '+' + '-' * user_width + '+' + '-' * score_width + '+\n')

        if sorted_scores:
            i = 1
            for user, score in sorted_scores:
                # 標記當前使用者
                if user == current_user_id:
                    user_display = f'*{user[:user_width]}*'
                else:
                    user_display = user[:user_width]

                output.write(f"|{str(i).center(rank_width)}|{user_display.center(user_width)}|{str(score).center(score_width)}|\n")
                output.write('+' + '-' * rank_width + '+' + '-' * user_width + '+' + '-' * score_width + '+\n')
                i += 1
        else:
            output.write('|' + '目前無人上榜'.center(total_width) + '|\n')
            output.write('+' + '-' * total_width + '+\n')

        # 獲取字串內容
        leaderboard_str = output.getvalue()
        output.close()

        return leaderboard_str
        

if __name__ == "__main__":
    firebase_url=os.getenv("FIREBASE_URL")
    leaderboard_str=get_rank("U89390a25e",firebase_url)
    print(leaderboard_str)