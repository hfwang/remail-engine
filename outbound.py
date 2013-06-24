import logging, yaml, json
from email.utils import parseaddr
from google.appengine.ext import webapp, deferred
from google.appengine.api import mail, urlfetch

settings = yaml.load(open('settings.yaml'))

def email(body):
  email = json.loads(body)

  # For some reason, ActiveResource is very adamant about generating a JSON
  # root... so unnest it if needed
  if 'email' in email:
    email = email['email']

  if settings['mandrill_api_key'] and settings['mandrill_api_key'] != 'changeme':
    send_via_mandrill(email)
  else:
    send_via_appengine(email)

def send_via_mandrill(args):
  mandrill_url = 'https://mandrillapp.com/api/1.0/messages/send.json'
  payload = { 'to': [] }

  # Translate fields from -> to
  fields = [
    ('subject', 'subject'),
    ('html', 'html'),
    ('body', 'text'),
    ('headers', 'headers'),
  ]
  for src, dest in fields:
    if src in args:
      payload[dest] = args[src]

  from_name, from_addr = parseaddr(args['sender'])
  payload['from_email'] = from_addr
  if from_name:
    payload['from_name'] = from_name

  if isinstance(args['to'], basestring):
    args['to'] = [args['to']]
  for recipient in args['to']:
    name, addr = parseaddr(recipient)
    struct = { 'email': addr }
    if name:
      struct['name'] = name
    payload['to'].append(struct)

  payload = {
    "key": settings['mandrill_api_key'],
    "message": payload
  }

  logging.debug("Sending via mandrill: %s", json.dumps(payload))
  content = urlfetch.fetch(
    mandrill_url,
    method=urlfetch.POST,
    headers={'Content-Type': 'application/json'},
    payload=json.dumps(payload))
  if content.status_code == 200:
    logging.info("Successfully sent")
  else:
    logging.error("Failed to send: %s", content)

def send_via_appengine(args):
  mail.EmailMessage(**args).send()

class OutboundHandler(webapp.RequestHandler):
  def post(self, *args):
    api_key = self.request.headers.get('Authorization')

    if api_key != settings['api_key']:
      logging.error("Invalid API key: " + str(api_key))
      self.error(401)
      return

    deferred.defer(email, self.request.body, _queue='outbound')
