from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Book, ReadingRecord
from datetime import date
import requests
import random


def build_search_query(query):
    """ISBNの場合はisbn:プレフィックスをつける"""
    digits = query.replace('-', '')
    if digits.isdigit() and len(digits) in [10, 13]:
        return f'isbn:{query}'
    return query


@login_required
def index(request):
    query = request.GET.get('q', '')
    section = request.GET.get('section', '')
    books_list = []

    # Google Books API検索（検索タブのみ）
    if query and section != 'books':
        url = "https://www.googleapis.com/books/v1/volumes"
        all_items = []
        search_query = build_search_query(query)

        for start_index in [0, 20]:
            params = {
                'q': search_query,
                'maxResults': 20,
                'startIndex': start_index,
                'key': settings.GOOGLE_BOOKS_API_KEY,
            }
            try:
                response = requests.get(url, params=params, timeout=5)
                response.raise_for_status()
                data = response.json()
                if 'items' in data:
                    all_items.extend(data['items'])
            except Exception as e:
                messages.error(request, f"検索中にエラーが発生しました: {e}")

        for item in all_items:
            info = item.get('volumeInfo', {})
            books_list.append({
                'title': info.get('title', 'タイトル不明'),
                'authors': info.get('authors', ['著者不明']),
                'thumbnail': info.get('imageLinks', {}).get('thumbnail', ''),
                'google_id': item.get('id'),
                'description': info.get('description', 'あらすじ情報がありません。'),
            })

    # ランダム本表示
    random_books = []
    random_keywords = [
        '人気小説', 'ベストセラー小説', '話題の本',
        '恋愛小説', 'ミステリー小説', '青春小説',
        '旅行エッセイ', '自己啓発', 'ビジネス書',
        '料理レシピ', '歴史小説', 'SF小説',
    ]
    try:
        rk = random.choice(random_keywords)
        r_response = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={
                'q': rk,
                'maxResults': 20,
                'langRestrict': 'ja',
                'key': settings.GOOGLE_BOOKS_API_KEY,
            },
            timeout=5
        )
        r_response.raise_for_status()
        r_data = r_response.json()
        if 'items' in r_data:
            items_with_thumb = [
                item for item in r_data['items']
                if item.get('volumeInfo', {}).get('imageLinks', {}).get('thumbnail')
                and item.get('volumeInfo', {}).get('authors')
                and item.get('volumeInfo', {}).get('publishedDate', '')[:4].isdigit()
                and int(item.get('volumeInfo', {}).get('publishedDate', '0')[:4]) >= 2000
            ]
            random_books = random.sample(items_with_thumb, min(6, len(items_with_thumb)))
    except Exception:
        random_books = []

    # 本タブの処理
    category = request.GET.get('category', 'read')
    sort = request.GET.get('sort', 'created')
    page = request.GET.get('page', 1)
    book_q = query if section == 'books' else ''

    # 詳細検索条件
    genre_id = request.GET.get('genre', '')
    emotion = request.GET.get('emotion', '')
    status_id = request.GET.get('status', '')
    reread_flag = request.GET.get('reread_flag', '')

    if book_q:
        my_books = Book.objects.filter(
            Q(user=request.user) &
            (Q(title__icontains=book_q) | Q(author__icontains=book_q))
        )
    else:
        my_books = Book.objects.filter(user=request.user, category=category)

    if genre_id:
        my_books = my_books.filter(
            google_book_id__in=ReadingRecord.objects.filter(
                user=request.user, genre_id=genre_id
            ).values('google_book_id')
        )
    if emotion != '':
        my_books = my_books.filter(
            google_book_id__in=ReadingRecord.objects.filter(
                user=request.user, emotion=emotion
            ).values('google_book_id')
        )
    if status_id:
        my_books = my_books.filter(
            google_book_id__in=ReadingRecord.objects.filter(
                user=request.user, status_id=status_id
            ).values('google_book_id')
        )
    if reread_flag != '':
        my_books = my_books.filter(
            google_book_id__in=ReadingRecord.objects.filter(
                user=request.user, reread_flag=reread_flag
            ).values('google_book_id')
        )

    if sort == 'title':
        my_books = my_books.order_by('title')
    else:
        my_books = my_books.order_by('-created_at')

    paginator = Paginator(my_books, 12)
    page_obj = paginator.get_page(page)

    from .models import Genre, Status
    context = {
        'query': query,
        'books': books_list,
        'page_obj': page_obj,
        'category': category,
        'sort': sort,
        'q': book_q,
        'is_search': bool(book_q) or bool(genre_id) or bool(emotion) or bool(status_id) or bool(reread_flag),
        'genre_id': genre_id,
        'emotion': emotion,
        'status_id': status_id,
        'reread_flag': reread_flag,
        'genres': Genre.objects.all(),
        'statuses': Status.objects.all(),
        'random_books': random_books,
        'count_read': Book.objects.filter(user=request.user, category='read').count(),
        'count_reading': Book.objects.filter(user=request.user, category='reading').count(),
        'count_stacked': Book.objects.filter(user=request.user, category='stacked').count(),
        'count_want': Book.objects.filter(user=request.user, category='want').count(),
    }
    return render(request, 'app/index.html', context)


def api_test(request):
    query = request.GET.get('q', '')
    books_list = []

    if query:
        url = "https://www.googleapis.com/books/v1/volumes"
        params = {
            'q': query,
            'maxResults': 20,
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

    context = {
        'query': query,
        'books': books_list,
    }
    return render(request, 'app/includes/search.html', context)


@login_required
def register_book(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        google_book_id = request.POST.get('google_book_id')

        if Book.objects.filter(user=request.user, google_book_id=google_book_id).exists():
            return JsonResponse({'status': 'error', 'message': 'すでに登録済みです'})

        Book.objects.create(
            user=request.user,
            google_book_id=google_book_id,
            title=request.POST.get('title', ''),
            author=request.POST.get('author', ''),
            thumbnail_url=request.POST.get('thumbnail_url', ''),
            description=request.POST.get('description', ''),
            category=category,
        )
        return JsonResponse({'status': 'ok', 'message': f"「{request.POST.get('title')}」を登録しました！"})

    return JsonResponse({'status': 'error', 'message': '不正なリクエストです'})


@login_required
def book_register_detail(request):
    if request.method == 'POST':
        google_book_id = request.POST.get('google_book_id', '')
        print("google_book_id:", google_book_id)
        print("title:", request.POST.get('title'))

        # 重複チェック
        from_edit = request.POST.get('from_edit', '')
        if not from_edit:
            if Book.objects.filter(user=request.user, google_book_id=google_book_id).exists():
                messages.error(request, 'この本はすでに登録済みです')
                return redirect(f"{'/'}?section=books&category=read")

        # 日付バリデーション
        read_date = request.POST.get('read_date')
        if read_date:
            try:
                read_date_obj = date.fromisoformat(read_date)
                if read_date_obj > date.today():
                    messages.error(request, '読んだ日付は今日以前の日付を入力してください')
                    from .models import Genre, Status
                    context = {
                        'google_book_id': request.POST.get('google_book_id', ''),
                        'title': request.POST.get('title', ''),
                        'author': request.POST.get('author', ''),
                        'thumbnail_url': request.POST.get('thumbnail_url', ''),
                        'description': request.POST.get('description', ''),
                        'from_edit': request.POST.get('from_edit', ''),
                        'genres': Genre.objects.all(),
                        'statuses': Status.objects.all(),
                    }
                    return render(request, 'app/book_register_detail.html', context)
            except ValueError:
                pass

        # Book を保存
        Book.objects.create(
            user=request.user,
            google_book_id=google_book_id,
            title=request.POST.get('title', ''),
            author=request.POST.get('author', ''),
            thumbnail_url=request.POST.get('thumbnail_url', ''),
            description=request.POST.get('description', ''),
            category='read',
        )

        # ReadingRecord を保存
        emotion_val = request.POST.get('emotion', '')
        ReadingRecord.objects.create(
            user=request.user,
            google_book_id=google_book_id,
            genre_id=request.POST.get('genre') or None,
            status_id=request.POST.get('status') or None,
            read_date=request.POST.get('read_date') or None,
            emotion=int(emotion_val) if emotion_val != '' else None,
            reread_flag=1 if request.POST.get('reread_flag') else 0,
            impressive_text=request.POST.get('impressive_text', ''),
            memo=request.POST.get('memo', ''),
        )
        book = Book.objects.filter(user=request.user, google_book_id=google_book_id).last()
        messages.success(request, f'「{book.title}」を登録しました！')
        return redirect('book_detail', book_id=book.id)

    from .models import Genre, Status
    context = {
        'google_book_id': request.GET.get('google_book_id', ''),
        'title': request.GET.get('title', ''),
        'author': request.GET.get('author', ''),
        'thumbnail_url': request.GET.get('thumbnail_url', ''),
        'description': request.GET.get('description', ''),
        'from_edit': request.GET.get('from_edit', ''),
        'genres': Genre.objects.all(),
        'statuses': Status.objects.all(),
    }
    return render(request, 'app/book_register_detail.html', context)


@login_required
def check_book_exists(request):
    if request.method == 'POST':
        google_book_id = request.POST.get('google_book_id', '')
        exists = Book.objects.filter(
            user=request.user,
            google_book_id=google_book_id
        ).exists()
        return JsonResponse({'exists': exists})
    return JsonResponse({'exists': False})


@login_required
def book_list(request):
    category = request.GET.get('category', 'read')
    sort = request.GET.get('sort', 'created')
    q = request.GET.get('q', '')
    page = request.GET.get('page', 1)

    books = Book.objects.filter(user=request.user, category=category)

    if q:
        books = books.filter(
            Q(title__icontains=q) | Q(author__icontains=q)
        )

    if sort == 'title':
        books = books.order_by('title')
    else:
        books = books.order_by('-created_at')

    paginator = Paginator(books, 12)
    page_obj = paginator.get_page(page)

    context = {
        'page_obj': page_obj,
        'category': category,
        'sort': sort,
        'q': q,
    }
    return render(request, 'app/includes/book_list.html', context)


@login_required
def book_detail(request, book_id):
    book = Book.objects.get(id=book_id, user=request.user)
    reading_record = None
    if book.category == 'read':
        reading_record = ReadingRecord.objects.filter(
            user=request.user,
            google_book_id=book.google_book_id
        ).first()
    context = {
        'book': book,
        'reading_record': reading_record,
    }
    return render(request, 'app/book_detail.html', context)


@login_required
def book_edit(request, book_id):
    book = Book.objects.get(id=book_id, user=request.user)

    if book.category != 'read':
        if request.method == 'POST':
            new_category = request.POST.get('category')

            if new_category == 'read':
                from urllib.parse import urlencode
                google_book_id = book.google_book_id
                title = book.title
                author = book.author
                thumbnail_url = book.thumbnail_url
                description = book.description
                book.delete()
                params = urlencode({
                    'google_book_id': google_book_id,
                    'title': title,
                    'author': author,
                    'thumbnail_url': thumbnail_url,
                    'description': description,
                    'from_edit': '1',
                })
                return redirect("home")

            if new_category:
                book.category = new_category
                book.save()
            return redirect('book_detail', book_id=book.id)

        return render(request, 'app/book_edit_simple.html', {'book': book})

    reading_record = ReadingRecord.objects.filter(
        user=request.user,
        google_book_id=book.google_book_id
    ).first()

    if request.method == 'POST':
        # 日付バリデーション
        read_date = request.POST.get('read_date')
        if read_date:
            try:
                read_date_obj = date.fromisoformat(read_date)
                if read_date_obj > date.today():
                    messages.error(request, '読んだ日付は今日以前の日付を入力してください')
                    from .models import Genre, Status
                    context = {
                        'book': book,
                        'reading_record': reading_record,
                        'genres': Genre.objects.all(),
                        'statuses': Status.objects.all(),
                    }
                    return render(request, 'app/book_edit.html', context)
            except ValueError:
                pass

        if reading_record:
            reading_record.genre_id = request.POST.get('genre') or None
            reading_record.status_id = request.POST.get('status') or None
            reading_record.read_date = request.POST.get('read_date') or None
            emotion_val = request.POST.get('emotion', '')
            reading_record.emotion = int(emotion_val) if emotion_val != '' else None
            reading_record.reread_flag = 1 if request.POST.get('reread_flag') else 0
            reading_record.impressive_text = request.POST.get('impressive_text', '')
            reading_record.memo = request.POST.get('memo', '')
            reading_record.save()
        return redirect('book_detail', book_id=book.id)

    from .models import Genre, Status
    context = {
        'book': book,
        'reading_record': reading_record,
        'genres': Genre.objects.all(),
        'statuses': Status.objects.all(),
    }
    return render(request, 'app/book_edit.html', context)


@login_required
def book_delete(request, book_id):
    if request.method == 'POST':
        book = Book.objects.get(id=book_id, user=request.user)
        ReadingRecord.objects.filter(
            user=request.user,
            google_book_id=book.google_book_id
        ).delete()
        book.delete()
        return redirect('home')
    return redirect('book_detail', book_id=book_id)

def top(request):
    return render(request, 'top.html')