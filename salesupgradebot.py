import os
import time
from ConfigParser import SafeConfigParser
from slackclient import SlackClient

from callingSFDCfunctions import *

parser = SafeConfigParser()
parser.read('slackbot.ini')
SLACK_BOT_TOKEN = parser.get('slackbot', 'SLACK_BOT_TOKEN')
BOT_ID = parser.get('slackbot', 'BOT_ID')


# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "upgrade"

# instantiate Slack & Twilio clients
slack_client = SlackClient(SLACK_BOT_TOKEN)

def handle_command(command, channel):
	"""
		Receives commands directed at the bot and determines if they
		are valid commands. If so, then acts on the commands. If not,
		returns back what it needs for clarification.
	"""
	response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
			   "* command with either a portal id or email address"
	if command.startswith(EXAMPLE_COMMAND):
		
		response = get_account_owner(command.split(EXAMPLE_COMMAND)[1])

	slack_client.api_call("chat.postMessage", channel=channel,
						  text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
	"""
		The Slack Real Time Messaging API is an events firehose.
		this parsing function returns None unless a message is
		directed at the Bot, based on its ID.
	"""
	output_list = slack_rtm_output
	if output_list and len(output_list) > 0:
		for output in output_list:
			if output and 'text' in output and AT_BOT in output['text']:
				# return text after the @ mention, whitespace removed
				return output['text'].split(AT_BOT)[1].strip().lower(), \
					   output['channel']
	return None, None



if __name__ == "__main__":
	READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
	if slack_client.rtm_connect():
		print("Bot connected and running!")
		while True:
			command, channel = parse_slack_output(slack_client.rtm_read())
			if command and channel:
				handle_command(command, channel)
			time.sleep(READ_WEBSOCKET_DELAY)
	else:
		print("Connection failed. Invalid Slack token or bot ID?")
