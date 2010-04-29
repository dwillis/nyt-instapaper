from google.appengine.api import urlfetch
from google.appengine.api.labs import taskqueue
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util
from django.utils import simplejson as json
import logging
import os
import urllib2, urllib

class MainHandler(webapp.RequestHandler):
    def get(self):
        url = "http://json8.nytimes.com/pages/politics/index.json"        
        response = urllib2.urlopen(url).read()
        items = json.loads(response)['items']

        articles = []
        for item in items:
            linktext = item['title']
            url = item['link']
            byline = item['byline']
            articles.append({
                'url': url,
                'byline': byline,
                'linktext': linktext,
                }
            )
        template_values = {'articles': articles}
        
        path = os.path.join(os.path.dirname(__file__), 'list.html')
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        articles = self.request.get_all("articles")
        username = self.request.get('username')
        password = self.request.get('password')
        for url in articles:
           taskqueue.add(
               url='/load-worker-dfsgylsdfgkjdfhlgjkdfdfgjfdslg', 
               params={'url': url, 'username': username, 'password': password}
           )
        self.response.out.write("Sent %d articles to instapaper" % len(articles))
        
class LoadWorkerHandler(webapp.RequestHandler):
    def post(self):
        article_url = self.request.get('url')
        form_fields = {
          "username": self.request.get('username'),
          "password": self.request.get('password'),
          "url": article_url,
          "auto-title": "1"
        }
        form_data = urllib.urlencode(form_fields)

        instapaper_response = urlfetch.fetch(
            url= "https://www.instapaper.com/api/add",
            method= urlfetch.POST,
            payload= form_data
        )
        logging.info("Lodged %s with instapaper. Reponse = %d" % (article_url, instapaper_response.status_code))

def main():
    application = webapp.WSGIApplication([
        ('/', MainHandler),
        ('/load-worker-dfsgylsdfgkjdfhlgjkdfdfgjfdslg', LoadWorkerHandler),        
        ],
        debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
