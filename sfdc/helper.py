#!/usr/bin/env python
import os
import logging
from ConfigParser import SafeConfigParser
#from google.appengine.api import memcache
import soap

def sfdc_email(arrEmails):
    ret = None
    try:
        sf = get_sfdc_client_cached()        
        ret = sf.email(arrEmails)
        logging.info('sfdc_email("%s") - SOAP Response\n%s' % (arrEmails, sf.response))
    except Exception,e:           
        logging.error('sfdc_email("%s") - EXCEPTION\n%s' % (arrEmails, str(e)))
    return ret

def sfdc_query(sfQuery):    
    ret = None
    try:
        #sf = get_sfdc_client_cached()
        sf = get_sfdc_client()
        ret = sf.query(sfQuery)
        logging.info('sfdc_query("%s") - SOAP Response\n%s' % (sfQuery, sf.response))
    except Exception,e:           
        logging.error('sfdc_query("%s") - EXCEPTION\n%s' % (sfQuery, str(e)))
    return ret

def sfdc_update(sfObject, sfId, sfFields):
    ret = None
    try:
        sf = get_sfdc_client_cached()        
        ret = sf.update(sfObject=sfObject, sfId=sfId, sfFields=sfFields)
        logging.info('sfdc_update("%s, %s, %s") - SOAP Response\n%s' % (sfObject, sfId, sfFields, sf.response))
    except Exception,e:
        logging.error('sfdc_update("%s, %s, %s") - EXCEPTION\n%s' % (sfObject, sfId, sfFields, str(e)))            
    return ret

def sfdc_create(sfObject, sfFields):
    ret = None
    try:
        sf = get_sfdc_client_cached()      
        ret = sf.create(sfObject=sfObject, sfFields=sfFields)
        logging.info('sfdc_create("%s, %s") - SOAP Response\n%s' % (sfObject, sfFields, sf.response))
    except Exception,e:
        logging.info(sf.response)
        logging.error('sfdc_create("%s, %s") - EXCEPTION\n%s' % (sfObject, sfFields, str(e)))            
    return ret

def get_sfdc_client_cached():
    cache_key = "get_sfdc_client"
    data = memcache.get(cache_key)
    if data is None:
        data = get_sfdc_client()
        if data:
            memcache.add(cache_key, data, 60 * 10) # Cache for 10 min
    return data

def get_sfdc_client():
    """ Initialize the sfdcSoapClient client with the proper credentials"""    
    
    is_sandbox = ('SFDC_USE_SANDBOX' in os.environ and os.environ['SFDC_USE_SANDBOX'] == True)
    logging.info('is_sandbox:%s' % is_sandbox)
    if is_sandbox:                
        section = "sfdc_sandbox"
    else:        
        section = "sfdc_prod"

    # Read SFDC Credentials INI
    parser = SafeConfigParser()
    parser.read('sfdc_credentials.ini')
    username = parser.get(section, 'username')
    password = parser.get(section, 'password')
    token = parser.get(section, 'token')    

    # Return a instance of the helper client
    return soap.sfdcSoapClient(username, password, token, is_sandbox)   