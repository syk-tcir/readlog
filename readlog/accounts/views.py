from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
import requests as http_requests

User = get_user_model()


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not email or not password1:
            messages.error(request, 'すべての項目を入力してください')
            return render(request, 'accounts/register.html')

        if password1 != password2:
            messages.error(request, 'パスワードが一致しません')
            return render(request, 'accounts/register.html')

        if len(password1) < 8:
            messages.error(request, 'パスワードは8文字以上で入力してください')
            return render(request, 'accounts/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'この名前はすでに使われています')
            return render(request, 'accounts/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'このメールアドレスはすでに使われています')
            return render(request, 'accounts/register.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
        )
        login(request, user)
        messages.success(request, 'アカウントを登録しました！')  # ← 追加
        return redirect('home')

    return render(request, 'accounts/register.html')


@login_required
def mypage(request):
    return render(request, 'accounts/mypage.html')


@login_required
def account_edit(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()

        if not username or not email:
            messages.error(request, 'すべての項目を入力してください')
            return render(request, 'accounts/account_edit.html')

        if User.objects.filter(username=username).exclude(id=request.user.id).exists():
            messages.error(request, 'この名前はすでに使われています')
            return render(request, 'accounts/account_edit.html')

        if User.objects.filter(email=email).exclude(id=request.user.id).exists():
            messages.error(request, 'このメールアドレスはすでに使われています')
            return render(request, 'accounts/account_edit.html')

        request.user.username = username
        request.user.email = email
        request.user.save()
        messages.success(request, 'アカウント情報を更新しました')
        return redirect('mypage')

    return render(request, 'accounts/account_edit.html')


def password_change_done_view(request):
    messages.success(request, 'パスワードを変更しました')
    return redirect('mypage')


def custom_password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            domain = request.get_host()
            reset_url = f"https://{domain}/accounts/reset/{uid}/{token}/"
            api_key = settings.BREVO_API_KEY
            response = http_requests.post(
                'https://api.brevo.com/v3/smtp/email',
                headers={
                    'api-key': api_key,
                    'Content-Type': 'application/json',
                },
                json={
                    'sender': {'name': 'ReadLog', 'email': 'sykt.819@gmail.com'},
                    'to': [{'email': email}],
                    'subject': 'ReadLog パスワード再設定',
                    'textContent': f'''
パスワード再設定のリクエストを受け付けました。

以下のURLからパスワードを再設定してください：

{reset_url}

このメールに心当たりがない場合は無視してください。

ReadLog
                    ''',
                }
            )
            return redirect('custom_password_reset_done')

        except User.DoesNotExist:
            messages.error(request, '入力されたメールアドレスは登録されていません')
            return render(request, 'registration/password_reset_form.html')

    return render(request, 'registration/password_reset_form.html')


def custom_password_reset_done(request):
    return render(request, 'registration/password_reset_done.html')


def custom_password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('new_password1', '')
            password2 = request.POST.get('new_password2', '')
            if password1 != password2:
                messages.error(request, 'パスワードが一致しません')
                return render(request, 'registration/password_reset_confirm.html', {'validlink': True})
            if len(password1) < 8:
                messages.error(request, 'パスワードは8文字以上で入力してください')
                return render(request, 'registration/password_reset_confirm.html', {'validlink': True})
            user.set_password(password1)
            user.save()
            return redirect('password_reset_complete')
        return render(request, 'registration/password_reset_confirm.html', {'validlink': True})
    else:
        return render(request, 'registration/password_reset_confirm.html', {'validlink': False})


def custom_password_reset_complete(request):
    return render(request, 'registration/password_reset_complete.html')