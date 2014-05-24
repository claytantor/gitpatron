from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', 'app.views.index',name='site_landing'),
    url(r'^oauth_redirect/$', 'app.views.oauth_redirect',name='oauth_redirect'),

    url(r'^index.html', 'app.views.index',name='site_landing'),
    url(r'^home.html', 'app.views.home', name='patron_home'),
    url(r'^logout.html', 'app.views.logout_user', name='logout'),
    url(r'^login.html', 'app.views.login_user', name='login'),
    url(r'^repos.html', 'app.views.repos',name='user_repos'),



    url(r'^repo/([-\w]+)/([-\w]+)/$', 'app.views.repo', name='repo'),

    #publish_repo_ajax
    url(r'^publish_repo_ajax/([-\w]+)/([-\w]+)/$',
        'app.views.publish_repo_ajax',name='publish_repo_ajax'),

    #sync_issues_ajax
    url(r'^sync_issues_ajax/([-\w]+)/([-\w]+)/$',
        'app.views.sync_issues_ajax',name='sync_issues_ajax'),

    #monetize_issue_ajax
    url(r'^monetize_issue_ajax/([\w]+)/$',
        'app.views.monetize_issue_ajax',name='monetize_issue_ajax'),

    #coin oauth
    url(r'^cbauthredirect.html', 'app.views.cb_auth_redirect',name='cb_auth_redirect'),

    #coin calls
    url(r'^coin_callback.html', 'app.views.coinbase_callback',name='coinbase_callback'),
    url(r'^cbcallback/([\w]+)/$', 'app.views.cbcallback',name='cbcallback'),

    #coin result pages
    url(r'^coin_success.html', 'app.views.coin_success',name='coin_success'),
    url(r'^coin_cancel.html', 'app.views.coin_cancel',name='coin_cancel'),
    url(r'^coin_info.html', 'app.views.coin_info',name='coin_info'),

    #admin
    url(r'^admin/', include(admin.site.urls)),
)
