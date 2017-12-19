import os
from slackclient import SlackClient
from ConfigParser import SafeConfigParser


parser = SafeConfigParser()
parser.read('slackbot.ini')
SLACK_BOT_TOKEN = parser.get('slackbot', 'SLACK_BOT_TOKEN')
BOT_NAME = parser.get('slackbot', 'BOT_NAME')


slack_client = SlackClient(SLACK_BOT_TOKEN)

if __name__ == "__main__":
	api_call = slack_client.api_call("users.list")
	if api_call.get('ok'):
		# retrieve all users so we can find our bot
		users = api_call.get('members')
		for user in users:
			#print user
			if 'name' in user and user.get('name') == BOT_NAME:
				print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
	else:
		print("could not find bot user with the name " + BOT_NAME)