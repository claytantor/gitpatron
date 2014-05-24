import urllib2
import json
from django.conf import settings
from urllib2 import HTTPError

class GithubV3():

    def get_json(self, url):
        try:
            response = urllib2.urlopen(url)
            json_response = response.read()
            return json.loads(json_response)
        except HTTPError:
            return json.loads('{}')


    def post_json(self, url, data_obj):
        try:
            data_json = json.dumps(data_obj)
            req = urllib2.Request(url, data_json, {'Content-Type': 'application/json'})
            f = urllib2.urlopen(req)
            response_obj = json.loads(f.read())
            f.close()
            return response_obj
        except HTTPError:
            return json.loads('{}')


#     {
#   "login": "claytantor",
#   "id": 407854,
#   "avatar_url": "https://avatars.githubusercontent.com/u/407854?",
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
#   "site_admin": false,
#   "name": "Clay Graham",
#   "company": "Welocally",
#   "blog": "http://www.welocally.com/?page_id=147",
#   "location": "Oakland, CA",
#   "email": "claytantor@gmail.com",
#   "hireable": false,
#   "bio": "",
#   "public_repos": 19,
#   "public_gists": 18,
#   "followers": 0,
#   "following": 23,
#   "created_at": "2010-09-20T06:22:33Z",
#   "updated_at": "2014-04-12T16:48:48Z"
# }
    def get_user(self, github_login):
        user_obj = self.get_json('https://api.github.com/users/{0}'.format(github_login))
        return user_obj

    #{u'access_token': u'faf603c66673f104270e3d19a6c1df0ad930d306', u'token_type': u'bearer', u'scope': u''}
    def get_oauth_response(self,oath_code):
        # client_id=...&
        # redirect_uri=http://www.example.com/oauth_redirect&
        # client_secret=...&
        # code=...

        data = {
            'client_id':settings.GIT_APP_CLIENT_ID,
            'redirect_uri':settings.GIT_APP_REDIRECT,
            'client_secret': settings.GIT_APP_CLIENT_SECRET,
            'code':oath_code
        }

        response_obj = self.post_json(
            'https://github.com/login/oauth/access_token',data)

        return response_obj


    #https://api.github.com/user?access_token=faf603c66673f104270e3d19a6c1df0ad930d306
    def get_oauth_user(self,access_token):
        user_obj = self.get_json('https://api.github.com/user?access_token={0}'.format(access_token))
        return user_obj

    def get_user_repos(self,git_login, access_token):
        repos_obj = self.get_json('https://api.github.com/user/{0}/repos?access_token={1}'.format(git_login,access_token))
        return repos_obj

    def get_oauth_user_repos(self, access_token):
        repos_obj = self.get_json('https://api.github.com/user/repos?access_token={0}'.format(access_token))
        return repos_obj

    #https://api.github.com/search/repositories?q=twitter4j

# GET /repos/claytantor/grailo
# {
#   "id": 6740387,
#   "name": "grailo",
#   "full_name": "claytantor/grailo",
#   "owner": {
#     "login": "claytantor",
#     "id": 407854,
#     "avatar_url": "https://avatars.githubusercontent.com/u/407854?",
#     "gravatar_id": "c88d7ef134a9779657d7d63257b5f725",
#     "url": "https://api.github.com/users/claytantor",
#     "html_url": "https://github.com/claytantor",
#     "followers_url": "https://api.github.com/users/claytantor/followers",
#     "following_url": "https://api.github.com/users/claytantor/following{/other_user}",
#     "gists_url": "https://api.github.com/users/claytantor/gists{/gist_id}",
#     "starred_url": "https://api.github.com/users/claytantor/starred{/owner}{/repo}",
#     "subscriptions_url": "https://api.github.com/users/claytantor/subscriptions",
#     "organizations_url": "https://api.github.com/users/claytantor/orgs",
#     "repos_url": "https://api.github.com/users/claytantor/repos",
#     "events_url": "https://api.github.com/users/claytantor/events{/privacy}",
#     "received_events_url": "https://api.github.com/users/claytantor/received_events",
#     "type": "User",
#     "site_admin": false
#   },
#   "private": false,
#   "html_url": "https://github.com/claytantor/grailo",
#   "description": "A privacy centric social network based on client side public private key encryption.",
#   "fork": false,
#   "url": "https://api.github.com/repos/claytantor/grailo",
#   "forks_url": "https://api.github.com/repos/claytantor/grailo/forks",
#   "keys_url": "https://api.github.com/repos/claytantor/grailo/keys{/key_id}",
#   "collaborators_url": "https://api.github.com/repos/claytantor/grailo/collaborators{/collaborator}",
#   "teams_url": "https://api.github.com/repos/claytantor/grailo/teams",
#   "hooks_url": "https://api.github.com/repos/claytantor/grailo/hooks",
#   "issue_events_url": "https://api.github.com/repos/claytantor/grailo/issues/events{/number}",
#   "events_url": "https://api.github.com/repos/claytantor/grailo/events",
#   "assignees_url": "https://api.github.com/repos/claytantor/grailo/assignees{/user}",
#   "branches_url": "https://api.github.com/repos/claytantor/grailo/branches{/branch}",
#   "tags_url": "https://api.github.com/repos/claytantor/grailo/tags",
#   "blobs_url": "https://api.github.com/repos/claytantor/grailo/git/blobs{/sha}",
#   "git_tags_url": "https://api.github.com/repos/claytantor/grailo/git/tags{/sha}",
#   "git_refs_url": "https://api.github.com/repos/claytantor/grailo/git/refs{/sha}",
#   "trees_url": "https://api.github.com/repos/claytantor/grailo/git/trees{/sha}",
#   "statuses_url": "https://api.github.com/repos/claytantor/grailo/statuses/{sha}",
#   "languages_url": "https://api.github.com/repos/claytantor/grailo/languages",
#   "stargazers_url": "https://api.github.com/repos/claytantor/grailo/stargazers",
#   "contributors_url": "https://api.github.com/repos/claytantor/grailo/contributors",
#   "subscribers_url": "https://api.github.com/repos/claytantor/grailo/subscribers",
#   "subscription_url": "https://api.github.com/repos/claytantor/grailo/subscription",
#   "commits_url": "https://api.github.com/repos/claytantor/grailo/commits{/sha}",
#   "git_commits_url": "https://api.github.com/repos/claytantor/grailo/git/commits{/sha}",
#   "comments_url": "https://api.github.com/repos/claytantor/grailo/comments{/number}",
#   "issue_comment_url": "https://api.github.com/repos/claytantor/grailo/issues/comments/{number}",
#   "contents_url": "https://api.github.com/repos/claytantor/grailo/contents/{+path}",
#   "compare_url": "https://api.github.com/repos/claytantor/grailo/compare/{base}...{head}",
#   "merges_url": "https://api.github.com/repos/claytantor/grailo/merges",
#   "archive_url": "https://api.github.com/repos/claytantor/grailo/{archive_format}{/ref}",
#   "downloads_url": "https://api.github.com/repos/claytantor/grailo/downloads",
#   "issues_url": "https://api.github.com/repos/claytantor/grailo/issues{/number}",
#   "pulls_url": "https://api.github.com/repos/claytantor/grailo/pulls{/number}",
#   "milestones_url": "https://api.github.com/repos/claytantor/grailo/milestones{/number}",
#   "notifications_url": "https://api.github.com/repos/claytantor/grailo/notifications{?since,all,participating}",
#   "labels_url": "https://api.github.com/repos/claytantor/grailo/labels{/name}",
#   "releases_url": "https://api.github.com/repos/claytantor/grailo/releases{/id}",
#   "created_at": "2012-11-17T21:38:34Z",
#   "updated_at": "2013-05-28T23:37:56Z",
#   "pushed_at": "2012-12-02T18:56:22Z",
#   "git_url": "git://github.com/claytantor/grailo.git",
#   "ssh_url": "git@github.com:claytantor/grailo.git",
#   "clone_url": "https://github.com/claytantor/grailo.git",
#   "svn_url": "https://github.com/claytantor/grailo",
#   "homepage": "",
#   "size": 1396,
#   "stargazers_count": 3,
#   "watchers_count": 3,
#   "language": "JavaScript",
#   "has_issues": true,
#   "has_downloads": true,
#   "has_wiki": true,
#   "forks_count": 0,
#   "mirror_url": null,
#   "open_issues_count": 2,
#   "forks": 0,
#   "open_issues": 2,
#   "watchers": 3,
#   "default_branch": "master",
#   "network_count": 0,
#   "subscribers_count": 1
# }
    def get_repo(self,username,repo_name):
        repos_obj = self.get_json('https://api.github.com/repos/{0}/{1}'.format(username,repo_name))
        return repos_obj


    #GET /repos/:owner/:repo/issues
#     {
#     "body": "Messages have a 250 char max, a check script should track characters and limit",
#     "labels": [
#         {
#             "url": "https://api.github.com/repos/claytantor/grailo/labels/enhancement",
#             "color": "84b6eb",
#             "name": "enhancement"
#         }
#     ],
#     "title": "Message length check",
#     "url": "https://api.github.com/repos/claytantor/grailo/issues/4",
#     "labels_url": "https://api.github.com/repos/claytantor/grailo/issues/4/labels{/name}",
#     "created_at": "2012-11-25T21:57:56Z",
#     "events_url": "https://api.github.com/repos/claytantor/grailo/issues/4/events",
#     "comments_url": "https://api.github.com/repos/claytantor/grailo/issues/4/comments",
#     "html_url": "https://github.com/claytantor/grailo/issues/4",
#     "comments": 0,
#     "number": 4,
#     "updated_at": "2012-11-25T21:58:07Z",
#     "assignee": null,
#     "state": "open",
#     "user": {
#         "following_url": "https://api.github.com/users/claytantor/following{/other_user}",
#         "events_url": "https://api.github.com/users/claytantor/events{/privacy}",
#         "organizations_url": "https://api.github.com/users/claytantor/orgs",
#         "url": "https://api.github.com/users/claytantor",
#         "gists_url": "https://api.github.com/users/claytantor/gists{/gist_id}",
#         "html_url": "https://github.com/claytantor",
#         "subscriptions_url": "https://api.github.com/users/claytantor/subscriptions",
#         "avatar_url": "https://avatars.githubusercontent.com/u/407854?",
#         "repos_url": "https://api.github.com/users/claytantor/repos",
#         "received_events_url": "https://api.github.com/users/claytantor/received_events",
#         "gravatar_id": "c88d7ef134a9779657d7d63257b5f725",
#         "starred_url": "https://api.github.com/users/claytantor/starred{/owner}{/repo}",
#         "site_admin": false,
#         "login": "claytantor",
#         "type": "User",
#         "id": 407854,
#         "followers_url": "https://api.github.com/users/claytantor/followers"
#     },
#     "milestone": null,
#     "closed_at": null,
#     "id": 8657138
# }
    def get_repo_issues(self,username,repo_name):
        repos_obj = self.get_json('https://api.github.com/repos/{0}/{1}/issues'.format(username,repo_name))
        return repos_obj





