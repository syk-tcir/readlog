from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings  # ← 追加
import requests

@login_required
def index(request):
    query = request.GET.get('q', '')  # ← 追加
    books_list = []                    # ← 追加

    if query:                          # ← 追加（ここから）
        url = "https://www.googleapis.com/books/v1/volumes"
        params = {
            'q': query,
            'maxResults': 10,
            'key': settings.GOOGLE_BOOKS_API_KEY,
        }
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            if 'items' in data:
                for item in data['items']:
                    info = item.get('volumeInfo', {})
                    books_list.append({
                        'title': info.get('title', 'タイトル不明'),
                        'authors': info.get('authors', ['著者不明']),
                        'thumbnail': info.get('imageLinks', {}).get('thumbnail', ''),
                        'google_id': item.get('id'),
                        'description': info.get('description', 'あらすじ情報がありません。'),
                    })
        except Exception as e:
            messages.error(request, f"検索中にエラーが発生しました: {e}")
                                       # ← ここまで追加

    context = {
        'query': query,                # ← 追加
        'books': books_list,           # ← 追加
    }
    return render(request, 'app/index.html', context)

def api_test(request):
    query = request.GET.get('q', '')
    books_list = []

    if query:
        url = "https://www.googleapis.com/books/v1/volumes"
        params = {
            'q': query,
            'maxResults': 10,
            'key': settings.GOOGLE_BOOKS_API_KEY,  # ← APIキーを追加
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if 'items' in data:
                for item in data['items']:
                    info = item.get('volumeInfo', {})
                    books_list.append({
                        'title': info.get('title', 'タイトル不明'),
                        'authors': info.get('authors', ['著者不明']),
                        'thumbnail': info.get('imageLinks', {}).get('thumbnail', ''),
                        'google_id': item.get('id'),
                        'description': info.get('description', 'あらすじ情報がありません。'),
                    })
        except Exception as e:
            messages.error(request, f"検索中にエラーが発生しました: {e}")

    context = {
        'query': query,
        'books': books_list,
    }
    return render(request, 'app/includes/search.html', context)