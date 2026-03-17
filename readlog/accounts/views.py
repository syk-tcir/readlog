from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages

User = get_user_model()  # CustomUserを取得


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