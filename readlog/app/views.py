from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Book, ReadingRecord
import requests


@login_required
def index(request):
    query = request.GET.get('q', '')
    section = request.GET.get('section', '')
    books_list = []

    # Google Books API検索（検索タブのみ）
    if query and section != 'books':
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

    # 本タブの処理
    category = request.GET.get('category', 'read')
    sort = request.GET.get('sort', 'created')
    page = request.GET.get('page', 1)
    book_q = query if section == 'books' else ''

    # 検索時は全カテゴリ横断でタイトル・著者を検索
    if book_q:
        my_books = Book.objects.filter(
            Q(user=request.user) &
            (Q(title__icontains=book_q) | Q(author__icontains=book_q))
        )
    else:
        my_books = Book.objects.filter(user=request.user, category=category)

    if sort == 'title':
        my_books = my_books.order_by('title')
    else:
        my_books = my_books.order_by('-created_at')

    paginator = Paginator(my_books, 12)
    page_obj = paginator.get_page(page)

    context = {
        'query': query,
        'books': books_list,
        'page_obj': page_obj,
        'category': category,
        'sort': sort,
        'q': book_q,
        'is_search': bool(book_q),
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

        from_edit = request.POST.get('from_edit', '')
        if not from_edit:
            if Book.objects.filter(user=request.user, google_book_id=google_book_id).exists():
                messages.error(request, 'この本はすでに登録済みです')
                return redirect('home')

        Book.objects.create(
            user=request.user,
            google_book_id=google_book_id,
            title=request.POST.get('title', ''),
            author=request.POST.get('author', ''),
            thumbnail_url=request.POST.get('thumbnail_url', ''),
            description=request.POST.get('description', ''),
            category='read',
        )

        ReadingRecord.objects.create(
            user=request.user,
            google_book_id=google_book_id,
            genre_id=request.POST.get('genre') or None,
            status_id=request.POST.get('status') or None,
            read_date=request.POST.get('read_date') or None,
            emotion=request.POST.get('emotion', 2),
            reread_flag=request.POST.get('reread_flag', 0),
            impressive_text=request.POST.get('impressive_text', ''),
            memo=request.POST.get('memo', ''),
        )
        return redirect('home')

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
                return redirect(f"/books/register/detail/?{params}")

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
        if reading_record:
            reading_record.genre_id = request.POST.get('genre') or None
            reading_record.status_id = request.POST.get('status') or None
            reading_record.read_date = request.POST.get('read_date') or None
            reading_record.emotion = request.POST.get('emotion', 2)
            reading_record.reread_flag = request.POST.get('reread_flag', 0)
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
