from django.db import models
from django.contrib.auth.models import User

import re

reply_re = re.compile("^@(\w+)")

#from django.core.management import call_command
#call_command('syncdb', interactive=True)
#call_command('migrate', interactive=True)

class Patron(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=250, unique=False)
    img = models.URLField(default="", verbose_name='Image URL', blank=True)
    bio = models.TextField( default="", verbose_name='Patron Bio')

    # "login": "claytantor",
    github_login = models.CharField(max_length=250, unique=False)

    #   "id": 407854,
    github_id = models.BigIntegerField(unique=True, null=True)

    #   "avatar_url": "https://avatars.githubusercontent.com/u/407854?",
    github_avatar_url = models.CharField(max_length=250, unique=False)

    #   "gravatar_id": "c88d7ef134a9779657d7d63257b5f725",
    #   "url": "https://api.github.com/users/claytantor",

    #   "html_url": "https://github.com/claytantor",
    #   "followers_url": "https://api.github.com/users/claytantor/followers",
    #   "following_url": "https://api.github.com/users/claytantor/following{/other_user}",
    #   "gists_url": "https://api.github.com/users/claytantor/gists{/gist_id}",
    #   "starred_url": "https://api.github.com/users/claytantor/starred{/owner}{/repo}",
    #   "subscriptions_url": "https://api.github.com/users/claytantor/subscriptions",
    #   "organizations_url": "https://api.github.com/users/claytantor/orgs",
    #   "repos_url": "https://api.github.com/users/claytantor/repos",
    #   "events_url": "https://api.github.com/users/claytantor/events{/privacy}",
    #   "received_events_url": "https://api.github.com/users/claytantor/received_events",

    #   "type": "User",
    github_type = models.CharField(max_length=16, unique=False)

    #   "site_admin": false



    def __unicode__(self):
        return self.name


class Repository(models.Model):
    name = models.CharField(max_length=250)
    markdown = models.TextField( default="", verbose_name='Repository Description')
    owner = models.ForeignKey('Patron',null=True,blank=True)

    def __unicode__(self):
        return self.name


class Issue(models.Model):
    
    # # "url": "https://api.github.com/repos/claytantor/grailo/issues/4",
    # name = models.CharField(max_length=250, unique=False)

    # "html_url": "https://github.com/claytantor/grailo/issues/4",
    github_html_url = models.CharField(max_length=250, unique=False)
    
    # "id": 8657138,
    github_id = models.BigIntegerField(unique=True, null=True)
    
    # "number": 4,
    github_issue_no = models.BigIntegerField(unique=True, null=True)
    
    # "title": "Message length check",  
    title = models.CharField(max_length=250, unique=False)


class Reward(models.Model):
    name = models.CharField(max_length=255, default="", verbose_name='Reward Name')
    amount = models.DecimalField(max_digits=8, decimal_places=2, default="", verbose_name="Minimum Amount")
    desc = models.TextField( default="", verbose_name='Reward Description')
    short_desc = models.CharField(max_length=255, default="", verbose_name='Short Reward Description')
    patron = models.ForeignKey('Patron',null=True,blank=True)
    issue = models.ForeignKey('Issue',null=True,blank=True)
    def __unicode__(self):
        return self.name

class Update(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    subject = models.CharField(max_length=255)
    text = models.TextField()
    repository = models.ForeignKey('Repository',null=True,blank=True)
    def __unicode__(self):
        return self.subject

class Comment(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    subject = models.CharField(max_length=255)
    text = models.TextField()
    patron = models.ForeignKey('Patron',null=True,blank=True)
    repository = models.ForeignKey('Repository',null=True,blank=True)
    def __unicode__(self):
        return self.subject

class Question(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    subject = models.CharField(max_length=255)
    patron = models.ForeignKey('Patron',null=True,blank=True)
    text = models.TextField()





