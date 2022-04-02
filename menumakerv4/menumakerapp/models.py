from django.db import models
from django.contrib.auth.models import User


# Create your models here 
class Cuisine(models.Model):
	cuisine = models.CharField(max_length=30)
	item = models.CharField(max_length=40)
	role = models.CharField(max_length=30)

class ObjCount(models.Model):
	objuser = models.CharField(max_length=30)
	createDate = models.CharField(max_length=15, default="", editable=False)
	objcount = models.IntegerField()
	objlist = models.CharField(max_length=255)

class cart(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	items = models.ForeignKey(Cuisine, on_delete=models.CASCADE)

class CustomAdmin(models.Model):
	username = models.CharField(max_length = 30)
	password = models.CharField(max_length = 15)
