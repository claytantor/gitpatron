import json
import math
from datetime import datetime

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict

from app.util.githubv3 import GithubV3
from app.util.coinbasev1 import CoinbaseV1

from app.models import Patron, CallbackMessage, CoinbaseButton, \
    Issue, Repository

# Create your views here.

def index(request,
          template_name="index.html"):

    # projects = Project.objects.all()
    return render_to_response(template_name,
        {},
        context_instance=RequestContext(request))

@login_required()
def home(request,
          template_name="home.html"):

    patron = Patron.objects.get(github_login=request.user.username)
    published_repos = Repository.objects.filter(owner=patron)
    client = GithubV3()
    github_repos = client.get_oauth_user_repos(patron.github_access_token)
    print repos

    return render_to_response(template_name,
        {
            'patron':patron,
            'published_repos':published_repos,
            'github_repos':github_repos
        },
        context_instance=RequestContext(request))

@login_required()
def repos(request,
          template_name="repos.html"):

    # patron = Patron.objects.get(github_login=request.user.username)
    patron = Patron.objects.get(github_login=request.user.username)

    client = GithubV3()
    repos = client.get_oauth_user_repos(patron.github_access_token)

    return render_to_response(template_name,
        {'repos':repos},
        context_instance=RequestContext(request))

@login_required()
def browse_published_repos(request,
          template_name="repos.html"):

    # patron = Patron.objects.get(github_login=request.user.username)
    patron = Patron.objects.get(github_login=request.user.username)
    repos = Repository.objects.all()

    # client = GithubV3()
    # repos = client.get_oauth_user_repos(patron.github_access_token)

    return render_to_response(template_name,
        {'published_repos':repos},
        context_instance=RequestContext(request))


#http://gitpatron.com/cbcallback.html?secret=a8b693bf-668c-461d-9a91-78f4b083e288
@require_http_methods(["POST"])
@csrf_exempt
def cbcallback(request,github_username):

    if request.GET['secret'] and request.GET['secret']==settings.COINBASE_SECRET:
        # model = json.loads(request.body)
        # #print model
        CallbackMessage.objects.create(
            message=request.body)
        response = {'message':'SUCCEED'}
        return HttpResponse(json.dumps(response), mimetype='application/json')
    else:
        return render_to_response("error.html",
        {'repos':repos},
        context_instance=RequestContext(request))



def login_user(request):
    return redirect(
        'https://github.com/login/oauth/authorize?client_id={0}&redirect_uri={1}&scope={2}'.format(
            settings.GIT_APP_CLIENT_ID,
            settings.GIT_APP_REDIRECT,
            settings.GIT_OAUTH_SCOPES), foo='bar')


def oauth_redirect(request,
          template_name="home.html"):

    if request.method == 'GET':

        #use the code to POST and get an access_token
        client = GithubV3()
        response_obj = client.get_oauth_response(request.GET['code'])

        oauth_user = client.get_oauth_user(response_obj['access_token'])

        try:
            patron = Patron.objects.get(github_login=oauth_user['login'])
            patron.github_access_token = response_obj['access_token']
            patron.save()
        except ObjectDoesNotExist:
            user = \
                User.objects.create_user(
                    oauth_user['login'], None, '')
            patron =\
                Patron.objects.create(
                    github_access_token = response_obj['access_token'],
                    github_login = oauth_user['login'],
                    user = user
                )
        auth_user = authenticate(username=oauth_user['login'], password='')
        if auth_user is not None:
            if auth_user.is_active:
                login(request, auth_user)
                # Redirect to a success page.
                return render_to_response(template_name,
                    {'patron':patron},
                    context_instance=RequestContext(request))
            else:
                # # Return a 'disabled account' error message
                # context['message']=request.POST['username']+' account has been suspended.'
                return render_to_response('error.html',{},context_instance=RequestContext(request))
        else:
            return render_to_response('error.html',{},context_instance=RequestContext(request))


    else:
        return render_to_response('error.html',
            {},
            context_instance=RequestContext(request))

def logout_user(request):
    logout(request)
    return redirect('index.html', foo='bar')


def repo(request,git_username,repo_name,
          template_name="repo.html"):

    is_published = False
    issues = None
    try:
        repo = Repository.objects.get(owner__user__username=git_username,name=repo_name)
        is_published = True
        issues = repo.issue_set.all()
    except ObjectDoesNotExist:
        github_client = GithubV3()
        repo = github_client.get_repo(git_username,repo_name)

    return render_to_response(template_name,
        {'repo':repo, 'issues':issues, 'is_published':is_published },
        context_instance=RequestContext(request))

@login_required()
def publish_repo_ajax(request, git_username,repo_name,
          template_name="publish_ajax.html"):

    #make sure the user is the owner
    is_published = False
    github_client = GithubV3()
    repo_response = github_client.get_repo(git_username,repo_name)
    if repo_response['owner']['login'] == request.user.username:

        patron = Patron.objects.get(user__username=request.user.username)

        repo_created = Repository.objects.create(
            name=repo_response['name'],
            fullname = repo_response['full_name'],
            github_description=repo_response['description'],
            owner = patron
        )

        #get the issues and add those
        issues_response = github_client.get_repo_issues(git_username,repo_name)
        for issue_response in issues_response:
            issue = Issue.objects.create(
                    github_api_url=issue_response['url'],
                    github_html_url=issue_response['html_url'],
                    github_id=issue_response['id'],
                    title=issue_response['title'],
                    github_issue_no=issue_response['number'],
                    json_body=json.dumps(issue_response),
                    description=issue_response['body'],
                    repository=repo_created
                )
        is_published = True

    else:
        template_name="error_ajax.html"

    return render_to_response(template_name,
            {'repo':repo_created, 'issues':repo_created.issue_set.all(),'is_published':is_published  },
            context_instance=RequestContext(request))

@login_required()
def sync_issues_ajax(request, git_username,repo_name,
          template_name="issues_ajax.html"):

    #the repo has to be linked and published for the sync to occur
    try:
        repo_saved = Repository.objects.get(owner__user__username=git_username,name=repo_name)

        github_client = GithubV3()
        issues_response = github_client.get_repo_issues(git_username,repo_name)
        issues = []

        for issue_response in issues_response:
             #try to look up the issue
            try:
                issue = Issue.objects.get(github_id=issue_response['id'])
                issues.append(issue)
            except ObjectDoesNotExist:
                issue = Issue.objects.create(
                    github_api_url=issue_response['url'],
                    github_html_url=issue_response['html_url'],
                    github_id=issue_response['id'],
                    title=issue_response['title'],
                    github_issue_no=issue_response['number'],
                    json_body=json.dumps(issue_response),
                    repository=repo_saved
                )
                issues.append(issue)

    except ObjectDoesNotExist:
        template_name="error_ajax.html"

    return render_to_response(template_name,
        {'issues':issues },
        context_instance=RequestContext(request))

@login_required()
def monetize_issue_ajax(request, issue_id,
          template_name="button_ajax.html"):

    patron = Patron.objects.get(user__username=request.user.username)

    client_coinbase = CoinbaseV1()

    issue  = get_object_or_404(Issue, pk=issue_id)

    button_request = {
        'button':{
            'name':'{0} {1}'.format(issue.github_id, issue.title),
            'custom':issue.github_api_url,
            'description':issue.title,
            'price_string':10.00,
            'price_currency_iso':'USD',
            'button_type':'donation',
            'style':'donation_small',
            'choose_price':True,
            'price1':5.00,
            'price2':10.00,
            'price3':25.00,
            'price4':100.00
        }
    }

    button_response = client_coinbase.post_button(button_request,patron.coinbase_access_token)

    button_created = CoinbaseButton.objects.create(
        code=button_response['button']['code'],
        external_id=issue.github_api_url,
        button_response=json.dumps(button_response),
        issue=issue)

    return render_to_response(template_name,
        { 'issue':issue },
        context_instance=RequestContext(request))

def cb_auth_redirect(request):
    coinbase_client = CoinbaseV1()
    return HttpResponseRedirect(coinbase_client.get_oauth_redirect())





# the login is required because we want to make
# sure we know what user to lookup for callback
@login_required()
def coinbase_callback(request,template_name="coinbase_auth.html"):

    if request.method == 'GET':

        context = {}

        #use the code to POST and get an access_token
        coinbase_client = CoinbaseV1()
        response_obj = coinbase_client.get_oauth_response(request.GET['code'])
        # {
        #     u'access_token': u'76af04cab8413dc39e7affe408673fbb75d4a02143a6cc21732af6d470bbab8b',
        #     u'token_type': u'bearer',
        #     u'expires_in': 7200,
        #     u'refresh_token': u'4deb04b689ae38165af92edb1077e07ef0eba692107cb97796260b9f56be0899',
        #     u'scope': u'all'
        # }
        #update the Patron object

        patron = Patron.objects.get(user__username=request.user.username)

        if patron:
            context = {}
            context['access_token']=response_obj['access_token']
            patron.coinbase_access_token=response_obj['access_token']
            patron.coinbase_refresh_token=response_obj['refresh_token']
            patron.save()

        else:
            context['message'] = 'error finding patron account.'
            template_name="error.html"


        print response_obj


    return render_to_response(template_name,
        context,
        context_instance=RequestContext(request))

def coin_success(request,
          template_name="coin_success.html"):

    return render_to_response(template_name,
        {},
        context_instance=RequestContext(request))

def coin_cancel(request,
          template_name="coin_cancel.html"):

    return render_to_response(template_name,
        {},
        context_instance=RequestContext(request))

def coin_info(request,
          template_name="coin_info.html"):

    return render_to_response(template_name,
        {},
        context_instance=RequestContext(request))