from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

from taggit.managers import TaggableManager

class UserProfile(models.Model):
    user = models.OneToOneField(User)

    cseaccountname = models.CharField(max_length=50)
    pwnablekraccountname = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    score = models.IntegerField()
    pwnablekrscore = models.IntegerField()

    def __str__(self):
        return "%s - %s" % (self.user.username, self.cseaccountname)


class CTF(models.Model):
    name = models.TextField()
    url = models.CharField(max_length=100, default=False)

    def __str__(self):
        return "%s" % (self.name)


class CTFLevel(models.Model):
    ctf = models.ForeignKey(CTF)  # which ctf this question belongs to
    name = models.TextField()
    points = models.IntegerField(default=0)
    flag = models.CharField(max_length=100, default=False)
    tags = TaggableManager()

    def __str__(self):
        return "CTFLEvel %s from %s, worth %d" % (self.name, self.ctf.name, self.points)


class WriteUp(models.Model):
    ctflevel = models.ForeignKey(CTFLevel)
    user = models.ForeignKey(UserProfile)
    text = models.TextField()
    flag = models.TextField(max_length=100, default=False)

    def __str__(self):
        return "Writeup by %s for %s from %s" % (self.user.user.username,
                                                 self.ctflevel.name,
                                                 self.ctflevel.ctf.name)
