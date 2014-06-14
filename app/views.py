import json
import string
import random
import uuid

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from app.util.githubv3 import GithubV3
from app.util.coinbasev1 import CoinbaseV1
from app.util.gitpatronhelper import GitpatronHelper

from app.models import Patron, CallbackMessage, CoinbaseButton, \
    Issue, Repository, ClaimedIssue, CoinOrder
from app.forms import FixForm

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
            'repos':published_repos,
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
def public_repos(request,
          template_name="repos.html"):


    repos = Repository.objects.all()

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

	print "order callback received"
	patron = Patron.objects.get(user__username=github_username)
		

	if request.GET['secret'] and request.GET['secret']==patron.coinbase_callback_secret:

		callback_message = json.loads(request.body)

		order_message = callback_message['order']

            	#find the button related to this order
            	order_button = CoinbaseButton.objects.get(code=order_message['button']['id'])

            	order = CoinOrder.objects.create(
                	# external_id = models.CharField(max_length=12)
                	external_id = order_message['id'],
                	# status = models.CharField(max_length=12)
                	status = order_message['status'],
                	# total_coin_cents = models.DecimalField(max_digits=8, decimal_places=8, default="", verbose_name="Order BTC Amount")
                	total_coin_cents = order_message['total_btc']['cents'],
                	# total_coin_currency_iso = models.CharField(max_length=3)
                	total_coin_currency_iso = order_message['total_btc']['currency_iso'],
                	# receive_address = models.CharField(max_length=36)
                	receive_address = order_message['receive_address'],
                	# refund_address = models.CharField(max_length=36)
                	refund_address = order_message['refund_address'],
                	button = order_button
            	)

		CallbackMessage.objects.create(
			is_processed = True,
                        owner=patron,
			processed_at = timezone.now(),
                        message=request.body)



        	response = {'message':'SUCCEED'}
        	return HttpResponse(json.dumps(response), mimetype='application/json')
	else:
        	return render_to_response("error.html",
        		{'message':'could not find secret in response callback.'},
        		context_instance=RequestContext(request))



def login_user(request):
	print 'https://github.com/login/oauth/authorize?client_id={0}&redirect_uri={1}&scope={2}'.format(
		settings.GIT_APP_CLIENT_ID,
		settings.GIT_APP_REDIRECT,
		settings.GIT_OAUTH_SCOPES)        
	return redirect(
		'https://github.com/login/oauth/authorize?client_id={0}&redirect_uri={1}&scope={2}'.format(
		settings.GIT_APP_CLIENT_ID,
        	settings.GIT_APP_REDIRECT,
        	settings.GIT_OAUTH_SCOPES), foo='bar')


def oauth_redirect(request,
          template_name="home.html"):
          
    print 'oauth_redirect'
 
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
                    oauth_user['login'], None, settings.GITPATRON_PW_SECRET_KEY)
            patron =\
                Patron.objects.create(
                    github_access_token = response_obj['access_token'],
                    github_login = oauth_user['login'],
                    user = user
                )

        auth_user = authenticate(username=oauth_user['login'], password=settings.GITPATRON_PW_SECRET_KEY)
        if auth_user is not None:
            if auth_user.is_active:
                login(request, auth_user)
                # Redirect to a success page.
                # return render_to_response(template_name,
                #     {'patron':patron},
                #     context_instance=RequestContext(request))

                return HttpResponseRedirect('/home.html')
            else:
                # # Return a 'disabled account' error message
                # context['message']=request.POST['username']+' account has been suspended.'
                print 'oauth_redirect error1'
                return render_to_response('error.html',{'message':'auth user is not empty but us unactive'},context_instance=RequestContext(request))
        else:
            print 'oauth_redirect error2'
            return render_to_response('error.html',{'message':'auth user is empty'},context_instance=RequestContext(request))


    else:
    	print 'oauth_redirect error3'
        return render_to_response('error.html',
            {'message':'response is not GET'},
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

        #calculate all patronage
        #get all orders for the specifc repo
        repo_patronage_orders = CoinOrder.objects.filter(
            button__issue__repository = repo,
            button__type='patronage'
        )
        #sum order values
        if len(repo_patronage_orders)>1:
            sum_patronage_cents = reduce(lambda x,y: x.total_coin_cents+y.total_coin_cents, repo_patronage_orders.all())
        elif len(repo_patronage_orders)==1:
            sum_patronage_cents = repo_patronage_orders[0].total_coin_cents
        else:
            sum_patronage_cents=0

        #calculate all fixes
        repo_fix_orders = CoinOrder.objects.filter(
            button__issue__repository = repo,
            button__type='fix'
        )

        if len(repo_fix_orders)>1:
            sum_fix_cents = reduce(lambda x,y: x.total_coin_cents+y.total_coin_cents, repo_fix_orders.all())
        elif len(repo_fix_orders)==1:
            sum_fix_cents = repo_fix_orders[0].total_coin_cents
        else:
            sum_fix_cents=0



    except ObjectDoesNotExist:
        github_client = GithubV3()
        repo = github_client.get_repo(git_username,repo_name)

    return render_to_response(template_name,
        {
            'repo':repo,
            'issues':issues,
            'is_published':is_published,
            'settings':settings,
            'sum_patronage_cents':sum_patronage_cents,
            'sum_fix_cents':sum_fix_cents
            },
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
            private= repo_response['private'] in ['true', 'True'],
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
                    repository=repo_created,
                    status=issue_response['state']
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
                issue.status = issue_response['state']

                #if closed then remove monetization
                if issue.status == 'closed':
                    owner = Patron.objects.get(user__username=git_username)
                    monetization_buttons = CoinbaseButton.objects.get(issue=issue,owner=owner,type="patronage").delete()
                    

                issue.save()
                issues.append(issue)
            except ObjectDoesNotExist:
                issue = Issue.objects.create(
                    github_api_url=issue_response['url'],
                    github_html_url=issue_response['html_url'],
                    github_id=issue_response['id'],
                    title=issue_response['title'],
                    github_issue_no=issue_response['number'],
                    json_body=json.dumps(issue_response),
                    repository=repo_saved,
                    status=issue_response['state']
                )
                issues.append(issue)

    except ObjectDoesNotExist:
        template_name="error_ajax.html"

    return render_to_response(template_name,
        {'issues':issues },
        context_instance=RequestContext(request))

@login_required()
def monetize_issue_ajax(request, issue_id,
          template_name="repo_button_ajax.html"):

    patron = Patron.objects.get(user__username=request.user.username)

    client_coinbase = CoinbaseV1()

    issue  = get_object_or_404(Issue, pk=issue_id)
    
    #make a button id that will persist for callback
    button_guid = str(uuid.uuid1())
    callback_url = '{0}/{1}/?secret={2}'.format(
    	settings.COINBASE_ORDER_CALLBACK,
    	patron.user.username,
    	patron.coinbase_callback_secret)
    	
    button_request = {
        'button':{
            'name':'{0} {1}'.format(issue.github_id, issue.title),
            'custom':button_guid,
            'description':issue.title,
            'price_string':10.00,
            'price_currency_iso':'USD',
            'button_type':'donation',
            'style':'donation_small',
            'choose_price':True,
            'price1':5.00,
            'price2':10.00,
            'price3':25.00,
            'price4':100.00,
            'callback_url':callback_url
        }
    }

    #refresh the user token before any coinbase call
    helper = GitpatronHelper()
    helper.refresh_user_token(patron.user.username)


    refresh_response = helper.refresh_user_token(patron.user.username)


    button_response = client_coinbase.post_button_oauth(
            button_request,
            refresh_response['access_token'],
            refresh_response['refresh_token'],
            settings.COINBASE_OAUTH_CLIENT_ID,
            settings.COINBASE_OAUTH_CLIENT_SECRET)


    if(button_response['error_code'] != None):
        return render_to_response('error_ajax.html',
            button_response,
            context_instance=RequestContext(request))

    else:
        #always update tokens on every oauth call
        patron.coinbase_access_token = button_response['access_token']
        patron.coinbase_refresh_token = button_response['refresh_token']
        # patron.coinbase_callback_secret = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        patron.save()

        #create the button
        button_created = CoinbaseButton.objects.create(
            code=button_response['button']['code'],
            external_id=issue.github_api_url,
            button_response=json.dumps(button_response),
            button_guid=button_guid,
            callback_url=callback_url,
            issue=issue,
            type="patronage",
            owner=patron)

        return render_to_response(template_name,
            { 'issue':issue },
            context_instance=RequestContext(request))

@login_required()
def claim_issue_ajax(request, issue_id,
          template_name="claim_button_ajax.html"):

    committer = Patron.objects.get(user__username=request.user.username)
    issue  = get_object_or_404(Issue, pk=issue_id)
    claim_issue_ajax = ClaimedIssue.objects.create(committer=committer, issue=issue)

    return render_to_response(template_name,
        { 'issue':issue },
        context_instance=RequestContext(request))


@login_required()
def claimed_issue(request, claimed_issue_id,
          template_name="claimed_issue.html"):

    claimed_issue  = get_object_or_404(ClaimedIssue, pk=claimed_issue_id)

    return render_to_response(template_name,
        { 'claimed':claimed_issue },
        context_instance=RequestContext(request))


@login_required()
def fix_issue_ajax(request, fix_issue_id,
          template_name="ajax_result.html"):

    claim_issue_ajax = get_object_or_404(ClaimedIssue, pk=fix_issue_id)
    claim_issue_ajax.fixed = True
    claim_issue_ajax.save()

    return render_to_response(template_name,
        { 'ajax_message':'Issue set to fixed and closed on github.' },
        context_instance=RequestContext(request))



def claimed(request, template_name="claimed.html"):
    committer = Patron.objects.get(user__username=request.user.username)
    claimed = ClaimedIssue.objects.filter(committer=committer )

    return render_to_response(template_name,
        {'claimed':claimed, 'settings':settings },
        context_instance=RequestContext(request))

def cb_auth_redirect(request):
    coinbase_client = CoinbaseV1()
    return HttpResponseRedirect(coinbase_client.get_oauth_redirect())

# the login is required because we want to make
# sure we know what user to lookup for callback
@login_required()
def coinbase_callback(request,template_name="coinbase_auth.html"):

    patron = Patron.objects.get(user__username=request.user.username)

    if request.method == 'GET':

        context = {}

        #use the code to POST and get an access_token
        coinbase_client = CoinbaseV1()

        #refresh the user token before any coinbase call
        helper = GitpatronHelper()

        # refresh_response = helper.refresh_user_token(patron.user.username)

        response_obj = coinbase_client.get_oauth_response(request.GET['code'])
        # {
        #     u'access_token': u'76af04cab8413dc39e7affe408673fbb75d4a02143a6cc21732af6d470bbab8b',
        #     u'token_type': u'bearer',
        #     u'expires_in': 7200,
        #     u'refresh_token': u'4deb04b689ae38165af92edb1077e07ef0eba692107cb97796260b9f56be0899',
        #     u'scope': u'all'
        # }

        #update the Patron object
        if patron:
            context = {}
            context['access_token']=response_obj['access_token']
            #http://gitpatron.com/cbcallback/claytantor/?secret=a8b693bf-668c-461d-9a91-78f4b083e288

            patron.coinbase_access_token=response_obj['access_token']
            patron.coinbase_refresh_token=response_obj['refresh_token']
            patron.coinbase_callback_secret = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
            patron.save()
            context['user_coinbase_callback']='{0}?secret={1}'.format(settings.COINBASE_OAUTH_CLIENT_CALLBACK,patron.coinbase_callback_secret)

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

@login_required()
def patronage(request,
          template_name="orders.html"):

    repo_owner = Patron.objects.get(user__username=request.user.username)
    orders = CoinOrder.objects.filter(
        button__owner=repo_owner,
        button__type='patronage'
    )

    return render_to_response(template_name,
        {
            'title':'Patronage',
            'orders':orders
        },
        context_instance=RequestContext(request))

@login_required()
def payments(request,
          template_name="orders.html"):

    committer = Patron.objects.get(user__username=request.user.username)
    orders = CoinOrder.objects.filter(
        button__owner=committer
    )

    return render_to_response(template_name,
        {
            'title':'Payments',
            'orders':orders
        },
        context_instance=RequestContext(request))

def fix_form_ajax(request,
          template_name="fix_form_ajax.html"):

    context = {}
    if request.method == 'POST':
        fixform = FixForm(request.POST)
        if fixform.is_valid():
            template_name='ajax_result.html'
            context['ajax_message'] = 'Fix Saved'

            patron = Patron.objects.get(user__username=request.user.username)


            # look we need to make a button and it should
            # be interactive like it asks me
            # how much I want to be paid. righT?
            # lets assume they are crazy, and that they arent
            # paid shit until we get a form model going
            claim_issue_ajax = ClaimedIssue.objects.get(id=fixform.cleaned_data['issue_id'])


            #ok make a gd button!
            client_coinbase = CoinbaseV1()

            #make a button id that will persist for callback
            button_guid = str(uuid.uuid1())

            callback_url = '{0}/{1}/?secret={2}'.format(
                settings.COINBASE_ORDER_CALLBACK,
                patron.user.username,
                patron.coinbase_callback_secret)

            # issue  = get_object_or_404(Issue, pk=issue_id)
            button_request = {
                'button':{
                    'name':'Fix for {0} {1}'.format(claim_issue_ajax.issue.github_id, claim_issue_ajax.issue.title),
                    'custom':button_guid,
                    'description':'Fix for {0}'.format(claim_issue_ajax.issue.title),
                    'price_string':fixform.cleaned_data['min_amount'],
                    'price_currency_iso':'USD',
                    'button_type':'buy_now',
                    'style':'donation_small',
                    'choose_price':False,
                    'callback_url':callback_url
                }
            }

            #refresh the user token before any coinbase call
            helper = GitpatronHelper()
            refresh_response = helper.refresh_user_token(patron.user.username)

            button_response = client_coinbase.post_button_oauth(
                    button_request,
                    refresh_response['access_token'],
                    refresh_response['refresh_token'],
                    settings.COINBASE_OAUTH_CLIENT_ID,
                    settings.COINBASE_OAUTH_CLIENT_SECRET)


            if(button_response['error_code'] != None):
                return render_to_response('error_ajax.html',
                    button_response,
                    context_instance=RequestContext(request))

            else:
                #always update tokens on every oauth call
                patron.coinbase_access_token = button_response['access_token']
                patron.coinbase_refresh_token = button_response['refresh_token']
                patron.save()

                #create the button
                button_created = CoinbaseButton.objects.create(
                    code=button_response['button']['code'],
                    external_id=claim_issue_ajax.issue.github_api_url,
                    button_guid=button_guid,
                    callback_url=callback_url,
                    button_response=json.dumps(button_response),
                    issue=claim_issue_ajax.issue,
                    type="fix",
                    owner=patron)

                # claim_issue_ajax.fixed = True
                claim_issue_ajax.button = button_created
                claim_issue_ajax.github_commit_id = fixform.cleaned_data['git_commit_id']
                claim_issue_ajax.save()

        context['form'] = fixform


    else:
        form = FixForm(initial={'issue_id': request.GET.get('fixed_issue_id')})
        context['form'] = form


    return render_to_response(template_name,
    context,
    context_instance=RequestContext(request))