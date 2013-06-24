from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from outbound import OutboundHandler
from inbound import InboundHandler

app = webapp.WSGIApplication([
    ('/emails(\.json)*', OutboundHandler),
    InboundHandler.mapping()
  ],
  debug=True)
