"""
proof-of-concept twitter bot
"""

from datetime import datetime
from django.utils import simplejson as json
import ConfigParser
import httplib2
import os
import pickle
import socket
import time
import tweepy


http = httplib2.Http()

class TwitterFetcher(object):

    def __init__(self, twitter_api, username):
        self.twitter_api = twitter_api
        self.username = username
        
    def parse(self, tweet):
        msg = tweet.text.replace('@' + self.username, '')
        # XXX what's the actual tweet format going to look like?
        try:
            title, location = msg.split('#bikerack', 1)
            return title.strip(), location.strip()
        except ValueError:
            print "couldn't parse tweet %r" % msg
            return None, None

    def get_tweets(self, since_id=None):
        """
        Try to get all our mentions and direct messages.
        Subject to Twitter's pagination limits,
        http://apiwiki.twitter.com/Things-Every-Developer-Should-Know#6Therearepaginationlimits
        """
        tweets = []
        max_pages = 16
        max_per_page = 200
        for tweet_func in (self.twitter_api.mentions,
                           self.twitter_api.direct_messages):
            for page in range(1, max_pages + 1):
                if since_id is not None:
                    more_tweets = tweet_func(count=max_per_page, page=page, since_id=since_id)
                else:
                    more_tweets = tweet_func(count=max_per_page, page=page)
                tweets += more_tweets
                if len(more_tweets) < max_per_page:
                    break
        tweets.sort(key=lambda t: t.id, reverse=True)
        return tweets


class RackBuilder(object):

    def __init__(self, url, config, api):
        self.url = url
        self.username = config.get('twitter', 'user')
        self.password = config.get('twitter', 'password')
        self.twitter_api = api
    
    def main(self, recent_only=True):
        url = self.url
        last_processed_id = None
        if recent_only:
            status_file_path = '/tmp/tweet.pickle'
            try:
                statusfile = open(status_file_path, 'r')
                status = pickle.load(statusfile)
                last_processed_id = status['last_processed_id']
                statusfile.close()
            except (IOError, EOFError):
                pass
        twit = TwitterFetcher(self.twitter_api, self.username)
        all_tweets = twit.get_tweets(last_processed_id)
        if all_tweets and last_processed_id:
            statusfile = open(status_file_path, 'w')
            pickle.dump({'last_processed_id': all_tweets[0].id}, statusfile)
            statusfile.close()
        for tweet in all_tweets:
            title, location = twit.parse(tweet)
            if title and location:
                new_rack(title, location, tweet.user.name, tweet.id, url)

            # TODO: batch-notification of success to cut down on posts:
            # if success, maintain a queue of recently successful posts,
            # and every N minutes:
            # - start with a template success message like
            # 'thanks for rack suggestions, see http://bit.ly/XXX'
            # - while chars < 140:
            # -   pop a suggestion from the queue
            # -   prepend @username to the message
            # -   append &id=X to a url like http://fixcity.org/rack/by_id?...
            # -   ... this would be a new view that shows all the id'd racks.
            # - build a bit.ly version of the URL and insert it in the message
            # - tweet the message
            # - repeat until we're out of users, or hit our API limit
            
        print self.twitter_api.rate_limit_status()





def bounce(*args, **kw):
    # XXX TODO
    print "OUCH %s %s" % (str(args), str(kw))

def adapt_errors(adict):
    # XXX TODO
    return adict

def new_rack(title, address, user, tweetid, url):
    # XXX strip out our username from the title
    
    # XXX UGH, copy-pasted from handle_mailin.py. Refactoring time!
    description = ''
    # We don't bother with microsecond precision because
    # Django datetime fields can't parse it anyway.
    now = datetime.fromtimestamp(int(time.time()))
    data = dict(title=title,
                description=description,
                date=now.isoformat(' '),
                address=address,
                geocoded=0,  # Do server-side geocoding.
                twitter_user=user,
                twitter_id=tweetid,
                )

    jsondata = json.dumps(data)
    headers = {'Content-type': 'application/json'}
            
    # TODO: if errors, respond to user (privately?) w/ error info.
    #  -- possibly with a URL to a single generic help page?
    
    error_subject = "Unsuccessful Rack Request"
    try:
        response, content = http.request(url, 'POST',
                                         headers=headers,
                                         body=jsondata)
    except socket.error:
        bounce(
            error_subject,
            "Thanks for trying to suggest a rack.\n"
            "We are unfortunately experiencing some difficulties at the\n"
            "moment -- please try again in an hour or two!",
            notify_admin='Server down??'
            )
        return

    if response.status >= 500:
        err_msg = (
            "Thanks for trying to suggest a rack.\n"
            "We are unfortunately experiencing some difficulties at the\n"
            "moment. Please check to make sure your subject line follows\n"
            "this format exactly:\n\n"
            "  Key Foods @224 McGuinness Blvd Brooklyn NY\n\n"
            "If you've made an error, please resubmit. Otherwise we'll\n"
            "look into this issue and get back to you as soon as we can.\n"
            )
        admin_body = content
        bounce(error_subject, err_msg, notify_admin='500 Server error',
               notify_admin_body=content)
        return

    result = json.loads(content)
    if result.has_key('errors'):

        err_msg = (
            "Thanks for trying to suggest a rack through fixcity.org,\n"
            "but it won't go through without the proper information.\n\n"
            "Please correct the following errors:\n\n")

        errors = adapt_errors(result['errors'])
        for k, v in sorted(errors.items()):
            err_msg += "%s: %s\n" % (k, '; '.join(v))

        err_msg += "\nPlease try again!\n"
        bounce(error_subject, err_msg)
        return


def get_config():
    import fixcity
    configfile = os.path.abspath(
        os.path.join(os.path.dirname(fixcity.__file__), 'config.ini'))
    assert os.path.exists(configfile), "Config file %s not found" % configfile
    config = ConfigParser.RawConfigParser()
    config.read(configfile)
    return config


def api_factory(config):
     auth = tweepy.BasicAuthHandler(config.get('twitter', 'user'),
                                    config.get('twitter', 'password'))
     api = tweepy.API(auth)
     return api
    
if __name__ == '__main__':
    config = get_config()
    api = api_factory(config)
    builder = RackBuilder('http://localhost:8000/rack/', config, api)
    builder.main(False)

