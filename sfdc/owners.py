#!/usr/bin/env python

#import logging
#from google.appengine.api import memcache
from helper import sfdc_query, sfdc_create

#-----------------------------------------------------------------------------
#
#   Salesforce - Opportunity
#
#-----------------------------------------------------------------------------
def get_sfdc_owner_by_email(email):
    '''Get the salesforce owner by the email of the contact'''
    ret = sfdc_query("""
    	SELECT OwnerId 
    	FROM Contact 
    	WHERE Email = '%s'""" % str(email))
    if ret:
        return ret[0]
    else:
        return None

def get_sfdc_contactid_by_email(email):
    '''Get the salesforce contactid by the email of the contact'''
    ret = sfdc_query("""
        SELECT Id 
        FROM Contact 
        WHERE Email = '%s'""" % str(email))
    if ret:
        return ret[0]
    else:
        return None


def get_sfdc_owner_by_portal_id(portalid):
    '''Get the salesforce owner by portal id'''
    ret = sfdc_query("""
    	SELECT Sales_Rep_Owner__c 
    	FROM Customer_Subscription__c 
    	WHERE HubFinder_URL__c LIKE '%s' """ % ("%" + str(portalid)))
    if ret:
        return ret[0]
    else:
        return None

def get_sfdc_owner_alias_by_owner_id(id):
    '''Get the salesforce owner by portal id'''
    ret = sfdc_query("""
        SELECT CommunityNickname 
        FROM User
        WHERE Id =  '%s' """ % str(id))
    if ret:
        return ret[0]
    else:
        return None

def assign_contact_to_campaign(campaignId , contactId):

    fields = {}
    fields['ContactId'] = contactId
    fields['CampaignId'] = campaignId

    return sfdc_create('CampaignMember' , fields)