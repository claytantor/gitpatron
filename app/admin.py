from django.contrib import admin

from app.models import Patron,Repository,Issue,Reward,\
    Update,Comment,Question,CallbackMessage,\
    CoinOrder,CoinCustomer,CoinTransaction,CoinbaseButton, ClaimedIssue, \
    WatchedRepository,PullRequest

admin.site.register(Patron)
admin.site.register(Repository)
admin.site.register(Issue)
admin.site.register(Reward)
admin.site.register(Update)
admin.site.register(Comment)
admin.site.register(Question)
admin.site.register(CallbackMessage)
admin.site.register(CoinOrder)
admin.site.register(CoinCustomer)
admin.site.register(CoinTransaction)
admin.site.register(CoinbaseButton)
admin.site.register(ClaimedIssue)
admin.site.register(WatchedRepository)
admin.site.register(PullRequest)


