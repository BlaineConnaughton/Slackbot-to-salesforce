import webapp2
import os
import json
import logging
import urllib
from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from google.appengine.ext import deferred

import time
import jinja2

from sfdc import owners

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

CAMPAIGNS = {'additional-portal':'70139000001DtqEAAS' , 'ads': '70139000001DtqYAAS','api':'70139000001Dtr2AAC','enterprise':'70139000001DtqnAAC',
				'general':'70139000001DtqOAAS','professional':'70139000001DtqdAAC','reporting':'70139000001DtqJAAS','sales-pro':'70139000001DtqxAAC',
				'ssl':'70139000001DtqiAAC','transactional-email':'70139000001DtqsAAC','website':'70139000001DtqTAAS'}


def add_to_salesforce(campaign , contactId):
		logging.info("In the task Queue")
		result = owners.assign_contact_to_campaign(campaign , contactid)
		logging.info("Here is the result: " + str(result))


class MainHandler(webapp2.RequestHandler):
	def get(self):
		
		self.response.write("Get Request is working for this endpoint")


	def post(self):
		"""
		Sample output from the outgoing webhook
		token = IF1tO4uLreJIlZqOsw7pS0IG & team_id = T37NE1Z6D &
		team_domain = connaughtontest & channel_id = D390K92TE &
		channel_name = directmessage & user_id = U393NCRSB &
		user_name = blaine & command = % 2 Fsalesupgrade & text = test++test & 
		response_url = https % 3 A % 2 F % 2 Fhooks.slack.com % 2 Fcommands % 2 FT37NE1Z6D % 2 F122567803890 % 2 FXTC1YrKn0xhxziOVgGY9dKEy
		"""

		#nIEkFYY4vD1Y04f6YKt8HyQQ
		token = self.request.get('token')
		text = self.request.get('text')
		textlower = text.lower()

		data = textlower.split()
		number_of_items = len(data)

		if number_of_items == 0:
			self.response.write("Was expecting an email address and a campaign name.  To see the campaign names enter an email address ")
			return
		
		contact = memcache.get(data[0])
		if contact is None:
			contact = owners.get_sfdc_contactid_by_email(data[0])
			if contact:
				memcache.add(data[0], contact, 1200)

		if contact == None:
			self.response.write("No contact in salesforce found with that email")
			return
		if number_of_items == 1:
			self.response.write("Need a Campaign name from: additional-portal, ads, api, enterprise, general, professional, reporting, sales-pro, ssl, transactional-email, website. Use spaces to add to more than 1 ")
			return

		campaign_check = CAMPAIGNS.keys()

		#the response back from salesforce helper functions is a dictionary of lists
		value = contact.values()
		contactId = value[0]

		logging.info("Here is the Contactid: " + str(contactId))

		#Need to get a reponse back in 3 seconds or the connection is lost, so will do the actual salesforce updates after validating
		invalid_campaigns = ""
		valid_campaigns = []

		i = 1 #0 holds the email address
		while i < number_of_items:
			if data[i] in campaign_check:
				valid_campaigns.append(CAMPAIGNS[data[i]])
			else:
				invalid_campaigns = invalid_campaigns + str(data[i]) + " " 
			i = i + 1


		if len(invalid_campaigns) > 0:
			invalid_campaigns = "Enrolling in the valid campaigns, these campaigns are not valid though: " + invalid_campaigns
		else:
			invalid_campaigns = "You got it rockstar "

		self.response.write(invalid_campaigns)

		for camp in valid_campaigns:
			logging.info("this is a valid campaign: " + str(camp))
			time.sleep(.1)
			#deferred.defer(add_to_salesforce, camp , contactId)

			params={ 'campaignid': camp , 'contactid': str(contactId)}
			taskqueue.add(url='/task', params=params)

		return


class TaskHandler(webapp2.RequestHandler):
	def post(self):
		logging.info("In the task Queue")
		campaignid = self.request.get('campaignid')
		contactid = self.request.get('contactid')
		try:
			result = owners.assign_contact_to_campaign(campaignid , contactid)
			logging.info("Here is the result: " + str(result))
			self.response.set_status(200)
		except:
			self.response.set_status(401)
		return
		

app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/task', TaskHandler)
	], debug=True)