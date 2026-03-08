from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # メールアドレスを必須、かつ重複不可（unique=True）にする
    email = models.EmailField('メールアドレス', unique=True)
    
    # 【重要】ログインの「鍵」を email に変更する
    USERNAME_FIELD = 'email'
    
    # email以外で、登録時に必須にする項目（ユーザー名など）
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email