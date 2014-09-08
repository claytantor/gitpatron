import urllib, hashlib


# Host: coinbase.com
class GravatarV1():

    def make_url(self,email_addr,default_url="identicon",size=128):
        # construct the url
        gravatar_url = "https://secure.gravatar.com/avatar/" + hashlib.md5(email_addr.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'d':default_url, 's':str(size)})
        return gravatar_url
