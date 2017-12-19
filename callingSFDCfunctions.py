import re
from sfdc import owners

def get_account_owner(lookup):

	print ("Here is what we got: " + str(lookup))

	#Check if it's an email
	if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", lookup):
		owner = owners.get_sfdc_owner_by_email(lookup)
		if owner == None:
			return "No customer portal found for that email"

	#Check if it's a number
	else: 
		try:
			print type(lookup)
			lookup = int(lookup)
			owner = owners.get_sfdc_owner_by_portal_id(lookup)
			if owner == None:
				return "No customer portal found for that portal"
		except:
			return "Not sure what you were looking for, that didn't seem to be an email address or a number"
	
	#the response back from these calls is a dictionary of lists for some reason, only want the first value
	value = owner.values()
	ownerid = value[0]
	
	account_owner = owners.get_sfdc_owner_alias_by_owner_id(ownerid)
	account_owner = account_owner.values()

	return str(account_owner[0])
