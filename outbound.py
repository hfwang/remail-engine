import logging, yaml, json
from google.appengine.ext import webapp, deferred
from google.appengine.api import mail

settings = yaml.load(open('settings.yaml'))

def email(body):
  email = json.loads(body)
  mail.EmailMessage(**email).send()

class OutboundHandler(webapp.RequestHandler):
  def post(self, *args):
    api_key = self.request.headers.get('Authorization')

    if api_key != settings['api_key']:
      logging.error("Invalid API key: " + str(api_key))
      self.error(401)
      return

    deferred.defer(email, self.request.body, _queue='outbound')
