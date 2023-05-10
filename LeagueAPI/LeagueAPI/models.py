from django.db import models

# Create your models here.
class Summoner(models.Model):
	summonerName = models.CharField(max_length = 255);
	encryptedSummonerId = models.CharField(max_length = 255);
	puuId = models.CharField(max_length = 255);
	summonerLevel = models.IntegerField(null = True);