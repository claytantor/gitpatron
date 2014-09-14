import urllib2
from urllib2 import HTTPError
from io import StringIO
import json


# Host: coinbase.com
class MailchimpV1():

    def get_http(self, url):
        try:
            response = urllib2.urlopen(url)
            http_response = response.read()
            return http_response
        except HTTPError:
            return None

    def get_list(self, api_key, list_id):
        url = 'https://us1.api.mailchimp.com/export/1.0/list/?apikey={0}&id={1}'.format(api_key,list_id)
        response = self.get_http(url)
        buf = StringIO(unicode(response))
        header = json.loads(buf.readline())

        content = buf.readlines()
        members = []
        for line in content:
            member_line = json.loads(line)
            member = self.make_member(header,member_line)
            members.append(member)

        return members


    def make_member(self,header,member_line):
        member = {}
        for i in range(0, len(header)):
            member[header[i]] = member_line[i]

        return member
