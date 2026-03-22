from django.db import models
from django.conf import settings

class Genre(models.Model):

    class Meta:
        verbose_name = "ジャンル"
        verbose_name_plural = "ジャンル"

    name = models.CharField(max_length=50)

    

    def __str__(self):
        return self.name

class Status(models.Model):

    class Meta:
        verbose_name = "状態タグ"
        verbose_name_plural = "状態タグ"

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class ReadingRecord(models.Model):

    class Meta:
        verbose_name = "読んだ本"
        verbose_name_plural = "読んだ本"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    genre = models.ForeignKey("Genre", on_delete=models.PROTECT, null=True, blank=True)
    status = models.ForeignKey("Status", on_delete=models.PROTECT, null=True, blank=True)
    google_book_id = models.CharField(max_length=255, blank=True, null=True)
    read_date = models.DateField(null=True, blank=True)
    emotion = models.IntegerField(default=2, null=True, blank=True) 
    reread_flag = models.IntegerField(default=0, null=True, blank=True)
    
    impressive_text = models.TextField(blank=True, null=True)
    memo = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.google_book_id}"
    
class Book(models.Model):
    CATEGORY_CHOICES = [
        ('read', '読んだ本'),
        ('reading', '読んでる本'),
        ('stacked', '積読本'),
        ('want', '読みたい本'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    google_book_id = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200, blank=True)
    thumbnail_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "書籍"
        verbose_name_plural = "書籍"

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"