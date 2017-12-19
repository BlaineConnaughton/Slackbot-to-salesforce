import logging
import re
import time
import datetime
from ConfigParser import SafeConfigParser

#from google.appengine.api import mail

#------------------------------------------------------------------------------
#
#   Error Logging
#
#------------------------------------------------------------------------------
def critical_error(body):
    logging.critical(body)
    send_admin_email(subject="SurveyApp - Critical Error", body=body)

#------------------------------------------------------------------------------
#
#   Email Functionality
#
#------------------------------------------------------------------------------


def send_admin_email(subject, body):
    # Send error email
    send_email(to="var-app-alerts-groups@hubspot.com",subject=subject,body=body)

def send_email(to,subject,body,html=""):
    if html == "":
        html = body
    
    # Send email
    # mail.send_mail(sender="VAR Calculator <mmetcoff@hubspot.com>", to=to, subject=subject, body=body, html=html)
    mail.send_mail(sender="Agency Assessment <services-apps@hubspot.com>", to=to, subject=subject, body=body, html=html)

def get_email_html(html):    
    import os,main,jinja2   
    jinja = jinja2.Environment(
                loader=jinja2.FileSystemLoader(os.path.dirname(main.__file__)),
                extensions=['jinja2.ext.autoescape'],
                autoescape=True)
    jinja_template = jinja.get_template("templates/email/email.html")
    return jinja_template.render({ "html": html })

#------------------------------------------------------------------------------
#
#   HS Credentials
#
#------------------------------------------------------------------------------

def get_hs_client(is_sandbox=False):
    if is_sandbox:
        section = "hubspot_sandbox"
    else:
        section = "hubspot_prod"

    # Read SFDC Credentials INI
    parser = SafeConfigParser()
    parser.read('hs_credentials.ini')
    token = parser.get(section, 'token')    
    return token

#-----------------------------------------------------------------------------
#
#   lookup()        
#   Helps find items in a dict array
#
#   Usage: lookup(data, key="name", sel="CompanyName")
#
#   @seq - The dict array you want to search through 
#   @key - The key name to match on 
#   @sel - The value to match on
#
#   @ret - dict()
#
#-----------------------------------------------------------------------------
def lookup(seq, key, sel):
    try:
        d = dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))
        return str(d[sel]["value"]).strip()
    except:
        return ""


#-----------------------------------------------------------------------------
#    Get a datetime object or a int() Epoch timestamp and return a
#    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
#    'just now', etc
#-----------------------------------------------------------------------------
def csv_date(s):
    return s.strftime("%Y-%m-%d %H:%M:%S")


#-----------------------------------------------------------------------------
#
#    Slugify
#
#-----------------------------------------------------------------------------
_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')
def slugify(value):
    value = unicode(_slugify_strip_re.sub('', value).strip().lower())
    return _slugify_hyphenate_re.sub('-', value)

#-----------------------------------------------------------------------------
#    Get a datetime object or a int() Epoch timestamp and return a
#    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
#    'just now', etc
#-----------------------------------------------------------------------------
def pretty_date(time=False):    
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time 
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:        
        if second_diff < 60:
            return "less than a minute ago"
        if second_diff < 120:
            return  "one minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"

    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 14:
        return "1 week ago"
    if day_diff < 31:
        return str(day_diff/7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff/30) + " months ago"
    return str(day_diff/365) + " years ago"

def is_date(origdate):
    if re.match('(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](19|20)\d\d', origdate):
        return True
    else:
        return False

def convert_date(origdate):
    # Get timestamp, convert to string, strip '.0', and append 000 to make milliseconds
    # I'm incrementing the day by 1, because even though HS says we require timestamps as of midnight UTC, we don't appear to respect that format, and show 1 day prior
    newtime = datetime.datetime.strptime(origdate, "%m/%d/%Y") + datetime.timedelta(days=1)
    newtime = newtime.timetuple()
    return str(time.mktime(newtime))[:-2] + '000'


def convert_fields_json_obj_to_dict(fields_obj):
    json_as_dict = {}
    for field in fields_obj:
        val = ""
        if field['value']:
            val = field['value']
        else:
            val = field['label']

        field_name = field['name']

        try:
            json_as_dict[field_name] += "<br>" + val
        except:
            json_as_dict[field_name] = val
    return json_as_dict