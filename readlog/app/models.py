from django.db import models
from django.conf import settings

class Genre(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = "ジャンル"
        verbose_name_plural = "ジャンル"

    def __str__(self):
        return self.name

class Status(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = "状態タグ"
        verbose_name_plural = "状態タグ"

    def __str__(self):
        return self.name

class ReadingRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    genre = models.ForeignKey("Genre", on_delete=models.PROTECT)
    status = models.ForeignKey("Status", on_delete=models.PROTECT)
    google_book_id = models.CharField(max_length=255, blank=True, null=True)
    read_date = models.DateField()
    emotion = models.IntegerField(default=2) 
    reread_flag = models.IntegerField(default=0)
    
    impressive_text = models.TextField(blank=True, null=True)
    memo = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "読んだ本"
        verbose_name_plural = "読んだ本"

    def __str__(self):
        return f"{self.user.username} - {self.google_book_id}"
    


