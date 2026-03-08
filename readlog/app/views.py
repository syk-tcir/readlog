from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests

@login_required
def index(request):

    return render(request, 'app/index.html')

def api_test(request):
    # Google Books APIにリクエストを送る
    url = "https://www.googleapis.com/books/v1/volumes?q=Python"
    
    try:
        response = requests.get(url, timeout=5) # 5秒待ってダメなら諦める設定
        data = response.json()
        
        # 'items' がデータの中に存在するかチェック
        if 'items' in data and len(data['items']) > 0:
            # 1冊目のタイトルを取得
            book_title = data['items'][0]['volumeInfo'].get('title', 'タイトル情報なし')
        else:
            book_title = "Googleで本が見つかりませんでした"
            
    except Exception as e:
        # 通信自体に失敗した場合
        book_title = f"通信エラーが発生しました: {e}"
    
    return render(request, 'app/api_test.html', {'title': book_title})