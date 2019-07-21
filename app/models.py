from django.contrib.auth.models import User
from django.db import models


# Create your models here
class Claim(models.Model):
    text = models.TextField()
    name = models.CharField(max_length=255)
    house = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=255)
    moder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moders', default=None, blank=True,
                              null=True)
    likes = models.ManyToManyField(User, related_name='likes')

    def countLikes(self):
        return self.likes.count()
