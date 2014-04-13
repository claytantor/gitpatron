import urllib2
import json


class GithubV3():

    def get_json(self, url):
        response = urllib2.urlopen(url)
        json_response = response.read()
        return json.loads(json_response)

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
        print(user_obj)

