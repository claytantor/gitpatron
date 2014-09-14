import json
import string
import random
import uuid
import re
import urllib
from datetime import datetime
from datetime import timedelta

from django.shortcuts import render_to_response, get_object_or_404
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
from django.template import RequestContext, loader

from app.util.gravatarv1 import GravatarV1
from app.util.githubv3 import GithubV3
from app.util.coinbasev1 import CoinbaseV1
from app.util.gitpatronhelper import GitpatronHelper

from app.models import Patron, CallbackMessage, CoinbaseButton, \
    Issue, Repository, ClaimedIssue, CoinOrder, WatchedRepository, \
    PullRequest

from app.forms import SettingsProfileForm

# Create your views here.

def index(request,
          template_name="index.html"):

    # projects = Project.objects.all()
    return render_to_response(template_name,
        {},
        context_instance=RequestContext(request))

def moderator(request,
          template_name="moderator.html"):

    # projects = Project.objects.all()
    return render_to_response(template_name,
        {},
        context_instance=RequestContext(request))

#(login_url='/login.html')
@login_required(login_url='/login.html')
def home(request,
          template_name="home.html"):

    patron = Patron.objects.get(github_login=request.user.username)
    published_repos = Repository.objects.filter(owner=patron)
    client = GithubV3()
    github_repos = client.get_oauth_user_repos(patron.github_access_token)
    watched = WatchedRepository.objects.filter(watcher=patron)

    #donations on repos the patron owns
    patron_donation_orders = CoinOrder.objects.filter(
        button__owner=patron
    )

    sum_patronage_cents = 0;
    for order in patron_donation_orders:
        sum_patronage_cents += order.total_coin_cents

    #payments on repos the patron owns
    fix_orders = CoinOrder.objects.filter(
        button__issue__repository__owner=patron
    )

    sum_fix_cents = 0;
    for order in fix_orders:
        sum_fix_cents += order.total_coin_cents

    #fix payments for fixes the patron made
    fix_payments = CoinOrder.objects.filter(button__owner=patron, button__type='fix')

    sum_fix_cents_paid = 0;
    for order in fix_payments:
        sum_fix_cents_paid += order.total_coin_cents




    return render_to_response(template_name,
        {
            # 'orders':orders,
            'watched':watched,
            'patron':patron,

            #this is patronage into repos the patron owns
            'patron_donation_orders':patron_donation_orders,
            'sum_patronage_cents':sum_patronage_cents,

            'fix_orders':fix_orders,
            'sum_fix_cents':sum_fix_cents,

            #this is where payments have been made
            'fix_payments':fix_payments,
            'sum_fix_cents_paid':sum_fix_cents_paid,


            'repos':published_repos,
            'github_repos':github_repos,
            # 'claimed_issues':claimed_issues
        },
        context_instance=RequestContext(request))

@login_required(login_url='/login.html')
def repos(request,
          template_name="repos.html"):

    # patron = Patron.objects.get(github_login=request.user.username)
    patron = Patron.objects.get(github_login=request.user.username)

    client = GithubV3()
    repos = client.get_oauth_user_repos(patron.github_access_token)

    return render_to_response(template_name,
        {'repos':repos},
        context_instance=RequestContext(request))

@login_required(login_url='/login.html')
def public_repos(request,
          template_name="repos.html"):


    repos = Repository.objects.all()

    return render_to_response(template_name,
        {'repos':repos},
        context_instance=RequestContext(request))

@login_required(login_url='/login.html')
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
def cbcallback(request, github_username):

    print request.body

    patron = Patron.objects.get(user__username=github_username)

    print 'request secret: {0} patron callaback secret: {1}'.format(request.GET['secret'],patron.coinbase_callback_secret)

    if request.GET['secret'] and request.GET['secret'] == patron.coinbase_callback_secret:

        print 'secret was found'

        callback_message = json.loads(request.body)

        order_message = callback_message['order']

        #find the button related to this order
        order_button = CoinbaseButton.objects.get(code=order_message['button']['id'])

        #get all the buttons associated with this issue
        all_order_buttons = CoinbaseButton.objects.filter(issue=order_button.issue)

        #dont let the order be created if it already exists
        orders_exist = CoinOrder.objects.filter(external_id=order_message['id'])

        print 'orders found: {0} for order with id: {1}'.format(len(orders_exist), order_message['id'])

        if len(orders_exist) == 0:
            print 'making order'


            try:

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
                    button = order_button,
                    created_at=datetime.utcnow()
                )

                #disable any issue buttons on payment
                for issue_order_button in all_order_buttons:
                    issue_order_button.enabled = False
                    issue_order_button.save()

            except Exception as e:
                print '%s (%s)' % (e.message, type(e))

        else:
            print 'did not make order'

        CallbackMessage.objects.create(is_processed=True, owner=patron, processed_at = timezone.now(), message=request.body)
        response = {'message':'SUCCEED'}
        return HttpResponse(json.dumps(response), mimetype='application/json')
    else:
        return render_to_response("error.html",
            {'message':'could not find secret in response callback.'},
            context_instance=RequestContext(request))

def login_user(request):
    print settings.GIT_APP_REDIRECT

    # rurl = 'https://github.com/login/oauth/authorize?client_id={0}&redirect_uri={1}&scope={2}'.format(
		# settings.GIT_APP_CLIENT_ID,
    #     urllib.quote_plus(settings.GIT_APP_REDIRECT),
    #     settings.GIT_OAUTH_SCOPES)
    #
    # print rurl

    return redirect(
		'https://github.com/login/oauth/authorize?client_id={0}&redirect_uri={1}&scope={2}'.format(
		settings.GIT_APP_CLIENT_ID,
        urllib.quote_plus(settings.GIT_APP_REDIRECT),
        settings.GIT_OAUTH_SCOPES), foo='bar')


def oauth_redirect(request,
          template_name="home.html"):

 
    if request.method == 'GET':

        #use the code to POST and get an access_token
        client = GithubV3()
        response_obj = client.get_oauth_response(request.GET['code'])

        oauth_user = client.get_oauth_user(response_obj['access_token'])

        #see if the user is in the beta program
        helper = GitpatronHelper()
        if settings.GITPATRON_STATE != 'RELEASE' and helper.is_beta_user(oauth_user['login']) is False:
            return render_to_response('beta_signup.html',{'message':'the github user: {0} has not signed up for the beta program.'.format(oauth_user['login'])},context_instance=RequestContext(request))

        try:
            patron = Patron.objects.get(github_login=oauth_user['login'])
            patron.github_access_token = response_obj['access_token']
            patron.save()
        except ObjectDoesNotExist:
            try:
                user = User.objects.get(username=oauth_user['login'])
            except ObjectDoesNotExist:
                user = \
                    User.objects.create_user(
                        oauth_user['login'], None, settings.GITPATRON_PW_SECRET_KEY)

            gravatar_email = ''
            if 'email' in oauth_user:
                gravatar_email = oauth_user['email']

            github_name = ''
            if 'name' in oauth_user:

                github_name = oauth_user['name']
            patron =\
                Patron.objects.create(
                    github_access_token=response_obj['access_token'],
                    github_login=oauth_user['login'],
                    gravatar_email=gravatar_email,
                    name=github_name,
                    user=user
                )

        auth_user = authenticate(username=oauth_user['login'], password=settings.GITPATRON_PW_SECRET_KEY)
        if auth_user is not None:
            if auth_user.is_active:
                login(request, auth_user)
                # Redirect to a success page.
                #needs the full app url for redirect
                return HttpResponseRedirect('{0}/home.html'.format(settings.GITPATRON_APP_URL))
            else:
                # # Return a 'disabled account' error message
                # context['message']=request.POST['username']+' account has been suspended.'
                return render_to_response('error.html',{'message':'auth user is not empty but us unactive'},context_instance=RequestContext(request))
        else:
            return render_to_response('error.html',{'message':'auth user is empty or (most likely) the GITPATRON_PW_SECRET_KEY is incorrect '},context_instance=RequestContext(request))


    else:
        return render_to_response('error.html',
            {'message':'response is not GET'},
            context_instance=RequestContext(request))

def logout_user(request):
    logout(request)
    return redirect('{0}/index.html'.format(settings.GITPATRON_APP_URL), foo='bar')


def repo(request,git_username,repo_name,
          template_name="repo.html"):

    is_published = False
    issues = None
    try:
        repo = Repository.objects.get(owner__user__username=git_username,name=repo_name)
        is_published = True
        issues = Issue.objects.filter(repository=repo).exclude(json_body__iregex=r'pull_request').order_by('github_issue_no')
        #pull_requests = Issue.objects.filter(repository=repo, json_body__iregex=r'pull_request').exclude(status='closed').order_by('github_issue_no')
        pull_requests = PullRequest.objects.filter(repository=repo).order_by('github_issue_no')

        #calculate all patronage
        #get all orders for the specifc repo
        repo_patronage_orders = CoinOrder.objects.filter(
            button__issue__repository = repo,
            button__type='patronage'
        )

        sum_patronage_cents = 0;
        for order in repo_patronage_orders:
            sum_patronage_cents += order.total_coin_cents

        #calculate all fixes
        repo_fix_orders = CoinOrder.objects.filter(
            button__issue__repository = repo,
            button__type='fix'
        )

        total_payments = 0
        for order in repo_fix_orders:
            total_payments += order.total_coin_cents



    except ObjectDoesNotExist:
        github_client = GithubV3()
        repo = github_client.get_repo(git_username,repo_name)

    return render_to_response(template_name,
        {
            'repo':repo,
            'issues':issues,
            'repo_patronage_orders':repo_patronage_orders,
            'repo_fix_orders':repo_fix_orders,
            'pull_requests':pull_requests,
            'is_published':is_published,
            'settings':settings,
            'sum_patronage_cents':sum_patronage_cents,
            'sum_fix_cents':total_payments
            },
        context_instance=RequestContext(request))


def repo_chart_json(request,git_username,repo_name):

    repo = Repository.objects.get(owner__user__username=git_username,name=repo_name)
    orders = CoinOrder.objects.filter(button__issue__repository=repo).order_by('created_at')

    donation_orders = CoinOrder.objects.filter(button__issue__repository=repo,button__type="patronage").order_by('created_at')
    fix_orders = CoinOrder.objects.filter(button__issue__repository=repo,button__type="fix").order_by('created_at')

    last_order = orders.reverse()[0]

    elapsedTime = last_order.created_at.replace(tzinfo=None) - repo.created_at.replace(tzinfo=None)
    days = elapsedTime.days+2

    # print 'last_order_date:{0} repo_created:{1} elapsed:{2}'.format(
    #     last_order.created_at.replace(tzinfo=None),
    #     repo.created_at.replace(tzinfo=None),
    #     elapsedTime.days)

    data = {
        'x': 'x',
        'columns': [
            ['x'],
            ['donations'],
            ['payments'],
        ]
    }

    total_donations = 0
    total_fix_payments = 0

    for n in range(days):
        repo_created = repo.created_at + timedelta(days=n)
        donation_date_formatted = repo_created.strftime("%Y-%m-%d")
        for order in donation_orders:
            order_date_formatted = order.created_at.strftime("%Y-%m-%d")
            if donation_date_formatted == order_date_formatted:
                total_donations += order.total_coin_cents

        for order in fix_orders:
            order_date_formatted = order.created_at.strftime("%Y-%m-%d")
            if donation_date_formatted == order_date_formatted:
                total_fix_payments += order.total_coin_cents

        data['columns'][0].append(donation_date_formatted)
        data['columns'][1].append("{0:g}".format(float(total_donations) / 100000000))
        data['columns'][2].append("{0:g}".format(float(total_fix_payments) / 100000000))



    # data = {
    #       'columns': [
    #         ['donations'],
    #         ['amounts']
    #       ]
    # }
    #
    # total_payments = 0
    # for order in orders:
    #     total_payments += order.total_coin_cents
    #     data['columns'][0].append(total_payments)
    #     data['columns'][1].append(order.total_coin_cents)

    return HttpResponse(json.dumps(data), mimetype='application/json')

@login_required(login_url='/login.html')
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
            owner = patron,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        #get the issues and add those
        issues_response = github_client.get_repo_issues(git_username,repo_name)

        for issue_response in issues_response:
            create_issue(issue_response, repo_created)
            create_pull_request(issue_response, repo_created)

        is_published = True

    else:
        template_name="error_ajax.html"

    return render_to_response(template_name,
            {'repo':repo_created, 'issues':repo_created.issue_set.all(),'is_published':is_published  },
            context_instance=RequestContext(request))

@login_required(login_url='/login.html')
def sync_issues_ajax(request, git_username,repo_name,
          template_name="issues_ajax.html"):

    #the repo has to be linked and published for the sync to occur
    try:
        repo_saved = Repository.objects.get(owner__user__username=git_username,name=repo_name)

        github_client = GithubV3()
        issues_response = github_client.get_repo_issues(git_username,repo_name)
        issues = []
        pull_requests = []

        for issue_response in issues_response:
            #try to look up the issue
            #is this an issue or a pull request

            if is_pull_request(issue_response):
                try:
                    pull_request = PullRequest.objects.get(github_id=issue_response['id'])
                    pull_request.status = issue_response['state']
                    pull_request.save()
                    pull_requests.append(pull_request)
                except ObjectDoesNotExist:
                    pull_request = create_pull_request(issue_response,repo_saved)
                    pull_requests.append(pull_request)
            else:
                #try to get the issue, create it if it doeant exist
                try:
                    issue = Issue.objects.get(github_id=issue_response['id'])
                    issue.status = issue_response['state']

                    # MOVING THIS TO PAYMENT CALLBACK
                    # #if closed then remove monetization WHY?, just disable them!!! this is confusing
                    # if issue.status == 'closed':
                    #     monetization_buttons = CoinbaseButton.objects.filter(issue=issue)
                    #     if len(monetization_buttons)>0:
                    #         for button in monetization_buttons:
                    #             button.enabled = False
                    #             button.save()

                    issue.save()
                    issues.append(issue)
                except ObjectDoesNotExist:
                    #doesn not exist create
                    issues.append(create_issue(issue_response,repo_saved))


    except ObjectDoesNotExist:
        template_name="error_ajax.html"

    return render_to_response(template_name,
        {
            'issues':sorted(issues, key=lambda issue: issue.github_issue_no),
            'pull_requests':sorted(pull_requests, key=lambda pull_request: pull_request.github_issue_no)
        },
        context_instance=RequestContext(request))

@login_required(login_url='/login.html')
def monetize_issue_ajax(request, issue_id,
          template_name="ajax_result.html"):

    patron = Patron.objects.get(user__username=request.user.username)



    client_coinbase = CoinbaseV1()

    issue  = get_object_or_404(Issue, pk=issue_id)

    #see if a patronage button for this issue exists
    patronage_button_issue = CoinbaseButton.objects.filter(issue=issue, type='patronage')

    if len(patronage_button_issue) == 0:

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
                {'message':'problem making button'},
                context_instance=RequestContext(request))

        else:
            #always update tokens on every oauth call
            patron.coinbase_access_token = button_response['access_token']
            patron.coinbase_refresh_token = button_response['refresh_token']
            # patron.coinbase_callback_secret = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
            patron.save()

            #create the button (if a patronage button doesnt already exist)

            button_created = CoinbaseButton.objects.create(
                code=button_response['button']['code'],
                external_id=issue.github_api_url,
                button_response=json.dumps(button_response),
                button_guid=button_guid,
                callback_url=callback_url,
                issue=issue,
                type="patronage",
                owner=patron,
                enabled=True)

            return render_to_response(template_name,
                { 'issue':issue,
                  'ajax_message':"Done!"},
                context_instance=RequestContext(request))
    else:
        return render_to_response('error_ajax.html',
            {'message':'patronage button already exists for this issue'},
            context_instance=RequestContext(request))

def monetize_repo_ajax(request, repo_id,
          template_name="ajax_response.html"):

        repo  = get_object_or_404(Repository, pk=repo_id)

        return render_to_response(template_name,
            { 'repo':repo },
            context_instance=RequestContext(request))


@login_required(login_url='/login.html')
def claim_issue_ajax(request, issue_id,
          template_name="claim_button_ajax.html"):

    committer = Patron.objects.get(user__username=request.user.username)
    issue  = get_object_or_404(Issue, pk=issue_id)
    claim_issue_ajax = ClaimedIssue.objects.create(
        committer=committer, issue=issue,
        created_at=datetime.now(),
        updated_at=datetime.now())

    return render_to_response(template_name,
        { 'issue':issue },
        context_instance=RequestContext(request))


@login_required(login_url='/login.html')
def claimed_issue(request, claimed_issue_id,
          template_name="claimed_issue.html"):

    claimed_issue  = get_object_or_404(ClaimedIssue, pk=claimed_issue_id)

    return render_to_response(template_name,
        { 'claimed':claimed_issue },
        context_instance=RequestContext(request))


@login_required(login_url='/login.html')
def fix_issue_ajax(request, fix_issue_id,
          template_name="ajax_result.html"):

    claim_issue_ajax = get_object_or_404(ClaimedIssue, pk=fix_issue_id)
    claim_issue_ajax.fixed = True
    claim_issue_ajax.save()

    return render_to_response(template_name,
        { 'ajax_message':'Issue set to fixed and closed on github.' },
        context_instance=RequestContext(request))


@require_http_methods(["GET"])
@login_required(login_url='/login.html')
def wallet_wf_ajax(request, wf_index):

    data = {}

    patron = Patron.objects.get(user__username=request.user.username)

    if int(wf_index) == 1:
        data['message'] = 'setting patron to has coinbase wallet'
        data['next'] = True
        data['this_state'] = 1
        data['next_state'] = 2
        patron.account_created = True
        patron.save()

    elif int(wf_index) == 2:
        data['message'] = 'saving coinbase wallet address'
        data['next'] = True
        data['this_state'] = 2
        data['next_state'] = 3
        patron.wallet_address = request.GET['address']
        patron.save()

    elif int(wf_index) == 3:
        data['message'] = 'activating wallet'
    elif int(wf_index) == 4:
        data['message'] = 'checking for donation'
    else:
        data['message'] = 'dont know what to do here'

    return HttpResponse(json.dumps(data), mimetype='application/json')

@require_http_methods(["GET"])
@login_required(login_url='/login.html')
def revoke_wallet(request):

    patron = Patron.objects.get(user__username=request.user.username)
    patron.coinbase_access_token = None
    patron.coinbase_refresh_token = None
    patron.coinbase_callback_secret = None

    #is_account_created
    patron.account_created = False

    #wallet_address
    patron.wallet_address = None

    #has_donated
    patron.has_donated = False
    patron.save()


    return HttpResponseRedirect('{0}/settings.html'.format(settings.GITPATRON_APP_URL))

@require_http_methods(["POST"])
@csrf_exempt
def activate_callback(request):

    print 'got actvate callback secret:{0}={1}'.format(request.GET['secret'],settings.GITPATRON_CALLBACK_SECRET)
    print request.body

    #the system will own these
    if request.GET['secret'] and request.GET['secret']==settings.GITPATRON_CALLBACK_SECRET:
        patron = Patron.objects.get(coinbase_callback_secret=request.GET['secret'])

        callback_message = json.loads(request.body)
        order_message = callback_message['order']

        print json.dumps(order_message)

        activate_patron  = get_object_or_404(Patron, wallet_address=order_message['custom'])
        print 'activating patron:{0}'.format(activate_callback)

        activate_patron.has_donated = True
        activate_patron.save()

        CallbackMessage.objects.create(
			is_processed = True,
            owner=patron,
			processed_at = datetime.utcnow(),
            message=request.body)

#'app.views.monetize_fix_ajax',name='monetize_fix_ajax'),
@login_required(login_url='/login.html')
def monetize_fix_ajax(
        request,
        pull_user,
        pull_request_id,
        template_name="ajax_result.html"):


    print 'monetize_fix_ajax'
    # claim_issue_ajax = get_object_or_404(ClaimedIssue, pk=fix_issue_id)
    # claim_issue_ajax.fixed = True
    # claim_issue_ajax.save()

    #calc the fix amount from donations
    #issue = Issue.objects.get(id=issue_id)
    # pull_request = PullRequest.objects.get(id=pull_request_id)
    pull_request = PullRequest.objects.get(id=pull_request_id,issue_user__user__username=pull_user)
    orders = CoinOrder.objects.filter(button__issue=pull_request.fix_issue)
    total_payments = 0
    for order in orders:
        total_payments += order.total_coin_cents

    #------------------
    patron = Patron.objects.get(user__username=request.user.username)


    # look we need to make a button and it should
    # be interactive like it asks me
    # how much I want to be paid. righT?
    # lets assume they are crazy, and that they arent
    # paid shit until we get a form model going
    claim_issue_ajax = ClaimedIssue.objects.get(issue=pull_request.fix_issue)


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
            'price_string':0.005384,
            'price_currency_iso':'BTC',
            'button_type':'buy_now',
            'style':'buy_now_small',
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

        #make coin cents a bigint
        coin_val = total_payments * 100000000
        coin_cents = "%.0f" % coin_val

        #create the button
        button_created = CoinbaseButton.objects.create(
            code=button_response['button']['code'],
            external_id=claim_issue_ajax.issue.github_api_url,
            button_guid=button_guid,
            callback_url=callback_url,
            button_response=json.dumps(button_response),
            issue=claim_issue_ajax.issue,
            type="fix",
            owner=patron,
            total_coin_cents=coin_cents,
            total_coin_currency_iso="BTC",
            enabled=True)

        # claim_issue_ajax.fixed = True
        claim_issue_ajax.button = button_created
        claim_issue_ajax.github_commit_id = pull_request.fix_issue.github_issue_no
        claim_issue_ajax.committer_type = "pull request"
        claim_issue_ajax.save()


    #------------------

    return render_to_response(template_name,
        { 'ajax_message':'Pull request monetized' },
        context_instance=RequestContext(request))


@login_required(login_url='/login.html')
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
@login_required(login_url='/login.html')
def coinbase_callback(request,template_name="coinbase_auth.html"):

    patron = Patron.objects.get(user__username=request.user.username)

    if request.method == 'GET':

        context = {}

        #use the code to POST and get an access_token
        coinbase_client = CoinbaseV1()

        response_obj = coinbase_client.get_oauth_response(request.GET['code'])

        #update the Patron object
        if patron:
            context = {}
            context['access_token']=response_obj['access_token']
            patron.coinbase_access_token=response_obj['access_token']
            patron.coinbase_refresh_token=response_obj['refresh_token']
            patron.coinbase_callback_secret = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
            patron.save()
            context['user_coinbase_callback']='{0}?secret={1}'.format(settings.COINBASE_OAUTH_CLIENT_CALLBACK,patron.coinbase_callback_secret)

        else:
            context['message'] = 'error finding patron account.'
            template_name="error.html"


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

@login_required(login_url='/login.html')
def patronage(request,
          template_name="payments.html"):

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

@login_required(login_url='/login.html')
def payments(request,
          template_name="payments.html"):

    committer = Patron.objects.get(user__username=request.user.username)
    orders = CoinOrder.objects.filter(
        button__owner=committer,
        button__type='fix'
    )

    return render_to_response(template_name,
        {
            'title':'Payments',
            'orders':orders
        },
        context_instance=RequestContext(request))

def about_gitpatron(request,
          template_name="about_gitpatron.html"):

    return render_to_response(template_name,
        { },
        context_instance=RequestContext(request))

def attribution(request,
          template_name="attribution.html"):

    return render_to_response(template_name,
        { },
        context_instance=RequestContext(request))


@login_required(login_url='/login.html')
def watch_repo_ajax(request,repoid,
          template_name="watch_repo_ajax.html"):

    watching_for_user = WatchedRepository.objects.filter(watcher__user=request.user, repository__id=repoid)
    repository = Repository.objects.get(id=repoid)
    if len(watching_for_user) > 0:
        #set to unwatch by delete
        watching_for_user.delete()
    else:
         #set to watch by create
        watcher = Patron.objects.get(user=request.user)
        watched = WatchedRepository.objects.create(
                    repository=repository,
                    watcher=watcher)

    return render_to_response(template_name,
        { 'repo':repository },
        context_instance=RequestContext(request))

# @login_required(login_url='/login.html')
# def fix_form_ajax(request,
#           owner,
#           reponame,
#           issue_no,
#           template_name="fix_form_ajax.html"):
#
#
#
#     issue = Issue.objects.get(repository__fullname='{0}/{1}'.format(owner,reponame),github_issue_no=issue_no)
#     context = {
#         'issue':issue
#     }
#
#     if request.method == 'POST':
#         fixform = FixForm(request.POST)
#         if fixform.is_valid():
#             template_name='ajax_result.html'
#             context['ajax_message'] = 'Fix Saved'
#
#             patron = Patron.objects.get(user__username=request.user.username)
#
#
#             # look we need to make a button and it should
#             # be interactive like it asks me
#             # how much I want to be paid. righT?
#             # lets assume they are crazy, and that they arent
#             # paid shit until we get a form model going
#             claim_issue_ajax = ClaimedIssue.objects.get(issue_id=fixform.cleaned_data['issue_id'])
#
#
#             #ok make a gd button!
#             client_coinbase = CoinbaseV1()
#
#             #make a button id that will persist for callback
#             button_guid = str(uuid.uuid1())
#
#             callback_url = '{0}/{1}/?secret={2}'.format(
#                 settings.COINBASE_ORDER_CALLBACK,
#                 patron.user.username,
#                 patron.coinbase_callback_secret)
#
#             # issue  = get_object_or_404(Issue, pk=issue_id)
#             button_request = {
#                 'button':{
#                     'name':'Fix for {0} {1}'.format(claim_issue_ajax.issue.github_id, claim_issue_ajax.issue.title),
#                     'custom':button_guid,
#                     'description':'Fix for {0}'.format(claim_issue_ajax.issue.title),
#                     'price_string':0.005384,
#                     'price_currency_iso':'BTC',
#                     'button_type':'buy_now',
#                     'style':'buy_now_small',
#                     'choose_price':False,
#                     'callback_url':callback_url
#                 }
#             }
#
#             #refresh the user token before any coinbase call
#             helper = GitpatronHelper()
#             refresh_response = helper.refresh_user_token(patron.user.username)
#
#             button_response = client_coinbase.post_button_oauth(
#                     button_request,
#                     refresh_response['access_token'],
#                     refresh_response['refresh_token'],
#                     settings.COINBASE_OAUTH_CLIENT_ID,
#                     settings.COINBASE_OAUTH_CLIENT_SECRET)
#
#
#             if(button_response['error_code'] != None):
#                 return render_to_response('error_ajax.html',
#                     button_response,
#                     context_instance=RequestContext(request))
#
#             else:
#                 #always update tokens on every oauth call
#                 patron.coinbase_access_token = button_response['access_token']
#                 patron.coinbase_refresh_token = button_response['refresh_token']
#                 patron.save()
#
#                 #make coin cents a bigint
#                 coin_val = fixform.cleaned_data['min_amount'] * 100000000
#                 coin_cents = "%.0f" % coin_val
#
#                 #create the button
#                 button_created = CoinbaseButton.objects.create(
#                     code=button_response['button']['code'],
#                     external_id=claim_issue_ajax.issue.github_api_url,
#                     button_guid=button_guid,
#                     callback_url=callback_url,
#                     button_response=json.dumps(button_response),
#                     issue=claim_issue_ajax.issue,
#                     type="fix",
#                     owner=patron,
#                     total_coin_cents=coin_cents,
#                     total_coin_currency_iso="BTC")
#
#                 # claim_issue_ajax.fixed = True
#                 claim_issue_ajax.button = button_created
#                 claim_issue_ajax.github_commit_id = fixform.cleaned_data['git_commit_id']
#                 claim_issue_ajax.committer_type = fixform.cleaned_data['type']
#                 claim_issue_ajax.save()
#
#         context['form'] = fixform
#
#
#     else:
#         form = FixForm(initial={'issue_id': issue.id})
#         context['form'] = form
#
#
#     return render_to_response(template_name,
#     context,
#     context_instance=RequestContext(request))

def issue(request,
          owner,
          reponame,
          issue_no,
          template_name="issue.html"):

    issue = Issue.objects.get(repository__fullname='{0}/{1}'.format(owner,reponame),github_issue_no=issue_no)
    patronage_orders = CoinOrder.objects.filter(button__issue=issue,button__type='patronage')
    fix_orders = CoinOrder.objects.filter(button__issue=issue,button__type='fix')

    #sum all orders value
    #total_payments = reduce(lambda x, y: x.total_coin_cents + y.total_coin_cents, orders)
    total_patronage = 0
    for order in patronage_orders:
        total_patronage += order.total_coin_cents

    total_fix = 0
    for order in fix_orders:
        total_fix += order.total_coin_cents


    context = {
        'issue':issue,
        'patronage_orders':patronage_orders,
        'fix_orders':fix_orders,
        'total_patronage':total_patronage,
        'total_fix':total_fix,
    }

    return render_to_response(template_name,
    context,
    context_instance=RequestContext(request))





def pull_mapping_ajax(request,
          pull_user,
          pull_mapping_id,
          issue_id,
          template_name="pull_mapping_ajax.html"):

    fix_issue = Issue.objects.get(id=issue_id)
    pull_request = PullRequest.objects.get(id=pull_mapping_id,issue_user__user__username=pull_user)

    #associate
    pull_request.fix_issue = fix_issue
    pull_request.save()

    context = {
        'pull_request':pull_request
    }

    return render_to_response(template_name, context,
        context_instance=RequestContext(request))


def patron(request,
          patron_name,
          template_name="patron.html"):
    patron = Patron.objects.get(user__username=patron_name)
    published_repos = Repository.objects.filter(owner=patron)

    client = GithubV3()
    github_user = client.get_user(patron_name)

    context = {
        'patron':patron,
        'avatar':github_user['avatar_url'],
        'github_user':github_user,
        'repos':published_repos,
    }

    return render_to_response(template_name,
    context,
    context_instance=RequestContext(request))


#issue_chart_json
def issue_chart_json(request,
          owner,
          reponame,
          issue_no):

    issue = Issue.objects.get(repository__fullname='{0}/{1}'.format(owner,reponame),github_issue_no=issue_no)
    orders = CoinOrder.objects.filter(button__issue=issue).order_by('created_at')

    #get the last donation order
    last_order = orders.reverse()[0]

    elapsedTime = last_order.created_at.replace(tzinfo=None) - issue.created_at.replace(tzinfo=None)
    days = elapsedTime.days+2

    # print 'last_order_date:{0} repo_created:{1} elapsed:{2} type:{3}'.format(
    #     last_order.created_at.replace(tzinfo=None),
    #     issue.created_at.replace(tzinfo=None),
    #     elapsedTime.days,
    #     last_order.button.type)

    is_paid = False;
    if(last_order.button.type=='fix'):
        is_paid = True

    data = {
        'is_paid':is_paid,
        'x': 'x',
        'columns': [
            ['x'],
            ['donations'],
        ]
    }

    total_payments = 0
    for n in range(days):
        date_donation = issue.created_at + timedelta(days=n)
        donation_date_formatted = date_donation.strftime("%Y-%m-%d")
        for order in orders:
            order_date_formatted = order.created_at.strftime("%Y-%m-%d")
            if donation_date_formatted == order_date_formatted:
                total_payments += order.total_coin_cents


        data['columns'][0].append(donation_date_formatted)
        data['columns'][1].append("{0:g}".format(float(total_payments) / 100000000))


    return HttpResponse(json.dumps(data), mimetype='application/json')

@login_required(login_url='/login.html')
def patron_settings(request,
          template_name="settings.html"):

    patron = Patron.objects.get(user=request.user)
    context = {
    }

    if request.method == 'GET':
        context ['settings_profile_form'] = \
            SettingsProfileForm(initial={'gravatar_email': patron.gravatar_email})
        context ['patron'] = patron

    elif request.method == 'POST':
        settings_profile_form = SettingsProfileForm(request.POST)
        if settings_profile_form.is_valid():
            gravatar_util = GravatarV1()
            email = settings_profile_form.cleaned_data['gravatar_email']
            gravatar_url = gravatar_util.make_url(
                email_addr=email,
                default_url="{0}/static/img/generic_avatar.png".format(settings.GITPATRON_APP_URL))
            patron.github_avatar_url = gravatar_url
            patron.gravatar_email = email
            patron.save()
            context ['settings_profile_form'] = settings_profile_form
            context ['patron'] = patron

    return render_to_response(template_name,
    context,
    context_instance=RequestContext(request))


def create_issue(issue_response, repo_created):
    #get the patron to associate
    issue_users = Patron.objects.filter(user__username=issue_response['user']['login'])

    r = list(issue_users[:1])
    if r:
        issue_user = r[0]
    else:
        issue_user = None

    #check for pull request
    json_body = json.dumps(issue_response)
    match = re.search(r'pull_request', json_body)

    if not match:
        issue = Issue.objects.create(
                github_api_url=issue_response['url'],
                github_html_url=issue_response['html_url'],
                github_id=issue_response['id'],
                title=issue_response['title'],
                github_issue_no=issue_response['number'],
                json_body=json_body,
                description=issue_response['body'],
                repository=repo_created,
                status=issue_response['state'],
                issue_user=issue_user,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        return issue
    else:
        return None

def create_pull_request(issue_response, repo_created):
    #get the patron to associate

    issue_users = Patron.objects.filter(user__username=issue_response['user']['login'])

    r = list(issue_users[:1])
    if r:
        issue_user = r[0]
    else:
        issue_user = None

    #check for pull request
    json_body = json.dumps(issue_response)
    match = re.search(r'pull_request', json_body)

    if match:
        pull_request = PullRequest.objects.create(
                github_api_url=issue_response['url'],
                github_html_url=issue_response['html_url'],
                github_id=issue_response['id'],
                title=issue_response['title'],
                github_issue_no=issue_response['number'],
                json_body=json_body,
                description=issue_response['body'],
                repository=repo_created,
                status=issue_response['state'],
                issue_user=issue_user,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
        )
        return pull_request
    else:
        return None

def is_pull_request(issue_response):
    #check for pull request
    json_body = json.dumps(issue_response)
    match = re.search(r'pull_request', json_body)

    if match:
        return True
    else:
        return False


#--------- javascript views (for widget) -----------------
def issue_widget_js(request, template_name='issue-widget.js'):

    issue_id = request.GET['issue_id']
    t = loader.get_template(template_name)
    c = RequestContext(request, {
        'application_url':settings.GITPATRON_APP_URL,
        'issue_id': issue_id})

    return HttpResponse(t.render(c), mimetype='application/json')

def issue_widget(request,
          issue_id,
          template_name="issue_widget.html"):

    issue = get_object_or_404(Issue,id=issue_id)
    patronage_orders = CoinOrder.objects.filter(button__issue=issue,button__type='patronage')
    fix_orders = CoinOrder.objects.filter(button__issue=issue,button__type='fix')

    #sum all orders value
    #total_payments = reduce(lambda x, y: x.total_coin_cents + y.total_coin_cents, orders)
    total_patronage = 0
    for order in patronage_orders:
        total_patronage += order.total_coin_cents

    total_fix = 0
    for order in fix_orders:
        total_fix += order.total_coin_cents


    context = {
        'issue':issue,
        'patronage_orders':patronage_orders,
        'fix_orders':fix_orders,
        'total_patronage':total_patronage,
        'total_fix':total_fix,
    }

    response = render_to_response(template_name,
        context,
        context_instance=RequestContext(request))

    response['X-Frame-Options'] = 'ALLOWALL'
    return response


def issue_popup(request, issue_id, template_name='issue_popup.html'):

    return render_to_response(template_name,
        {'issue_id':issue_id},
    context_instance=RequestContext(request))

