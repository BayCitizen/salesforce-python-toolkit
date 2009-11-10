# This program is free software; you can redistribute it and/or modify
# it under the terms of the (LGPL) GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of the 
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library Lesser General Public License for more details at
# ( http://www.gnu.org/licenses/lgpl.html ).
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# Written by: David Lanstein ( lanstein yahoo com )

import string
import sys
import os.path

from suds.client import Client
from suds.transport.cache import FileCache
import suds.sudsobject
from suds.sax.element import Element

class SforceBaseClient(object):
  _sforce = None
  _sessionId = None
  _location = None
  _product = 'Python Toolkit'
  _version = (0, 1, 1)
  _objectNamespace = None
  _strictResultTyping = False

  _allowFieldTruncationHeader = None
  _assignmentRuleHeader = None
  _callOptions = None
  _assignmentRuleHeader = None
  _emailHeader = None
  _localeOptions = None
  _loginScopeHeader = None
  _mruHeader = None
  _packageVersionHeader = None
  _queryOptions = None
  _sessionHeader = None
  _userTerritoryDeleteHeader = None

  def __init__(self, wsdl, cacheDuration = 0, **kwargs):
    '''
    Connect to Salesforce
   
    'wsdl' : Location of WSDL
    'cacheDuration' : Duration of HTTP GET cache in seconds, or 0 for no cache
    'proxy' : Dict of pair of 'protocol' and 'location'
              e.g. {'http': 'my.insecure.proxy.example.com:80'}
    'username' : Username for HTTP auth when using a proxy ONLY
    'password' : Password for HTTP auth when using a proxy ONLY
    '''
    # Suds can only accept WSDL locations with a protocol prepended
    if '://' not in wsdl:
      # TODO windows users???
      # check if file exists, else let bubble up to suds as is
      # definitely don't want to assume http or https
      if os.path.isfile(wsdl):
        wsdl = 'file://' + os.path.abspath(wsdl)

    if cacheDuration > 0:
      cache = FileCache()
      cache.setduration(seconds = cacheDuration)
    else:
      cache = None
    
    self._sforce = Client(wsdl, cache = cache)

    # Set HTTP headers
    headers = {'User-Agent': 'Salesforce/' + self._product + '/' + '.'.join(str(x) for x in self._version)}

    # This HTTP header will not work until Suds gunzips/inflates the content
    # 'Accept-Encoding': 'gzip, deflate'

    self._sforce.set_options(headers = headers)

    if kwargs.has_key('proxy'):
      # urllib2 cannot handle HTTPS proxies yet (see bottom of README)
      if kwargs['proxy'].has_key('https'):
        raise NotImplementedError('Connecting to a proxy over HTTPS not yet implemented due to a \
limitation in the underlying urllib2 proxy implementation.  However, traffic from a proxy to \
Salesforce will use HTTPS.')
      self._sforce.set_options(proxy = kwargs['proxy'])

    if kwargs.has_key('username'):
      self._sforce.set_options(username = kwargs['username'])

    if kwargs.has_key('password'):
      self._sforce.set_options(password = kwargs['password'])

  # Toolkit-specific methods

  def generateHeader(self, sObjectType):
    '''
    Generate a SOAP header as defined in:
    http://www.salesforce.com/us/developer/docs/api/Content/soap_headers.htm
    '''
    try:
      return self._sforce.factory.create(sObjectType)
    except:
      print 'There is not a SOAP header of type %s' % sObjectType

  def generateObject(self, sObjectType):
    '''
    Generate a Salesforce object, such as a Lead or Contact
    '''
    obj = self._sforce.factory.create('ens:sObject')
    obj.type = sObjectType
    return obj

  def _handleResultTyping(self, result):
    '''
    If any of the following calls return a single result, and self._strictResultTyping is true,
    return the single result, rather than [(SaveResult) {...}]:

      convertLead()
      create()
      delete()
      emptyRecycleBin()
      invalidateSessions()
      merge()
      process()
      retrieve()
      undelete()
      update()
      upsert()
      describeSObjects()
      sendEmail()
    '''
    if self._strictResultTyping == False and len(result) == 1:
      return result[0]
    else:
      return result

  def _marshallSObjects(self, sObjects, tag = 'sObjects'):
    '''
    Marshall generic sObjects into a list of SAX elements
  
    This code is going away ASAP

    tag param is for nested objects (e.g. MergeRequest) where 
    key: object must be in <key/>, not <sObjects/>
    '''
    if not isinstance(sObjects, (tuple, list)):
      sObjects = (sObjects, )
    if sObjects[0].type in ['LeadConvert', 'SingleEmailMessage', 'MassEmailMessage']:
      nsPrefix = 'tns:'
    else:
      nsPrefix = 'ens:'

    li = []
    for obj in sObjects:
      el = Element(tag)
      el.set('xsi:type', nsPrefix + obj.type)
      for k, v in obj:
        if k == 'type':
          continue

        # This is here to avoid 'duplicate values' error when setting a field in fieldsToNull
        # Even a tag like <FieldName/> will trigger it
        if v == None: 
          # not going to win any awards for variable-naming scheme here
          tmp = Element(k)
          tmp.set('xsi:nil', 'true')
          el.append(tmp)
        elif isinstance(v, (list, tuple)):
          for value in v:
            el.append(Element(k).setText(value))
        elif isinstance(v, suds.sudsobject.Object):
          el.append(self._marshallSObjects(v, k))
        else:
          el.append(Element(k).setText(v))

      li.append(el)
    return li
 
  def _setEndpoint(self, location):
    '''
    Set the endpoint after when Salesforce returns the URL after successful login()
    '''
    # suds 0.3.7+ supports multiple wsdl services, but breaks setlocation :(
    # see https://fedorahosted.org/suds/ticket/261
    try:
      self._sforce.set_options(location = location)
    except:
      self._sforce.wsdl.service.setlocation(location)

    self._location = location

  def _setHeaders(self, call = None):
    '''
    Attach particular SOAP headers to the request depending on the method call made
    '''
    # All calls, including utility calls, set the session header
    headers = {'SessionHeader': self._sessionHeader}
    
    if call in ('convertLead',
                'create',
                'merge',
                'process',
                'undelete',
                'update',
                'upsert'):
      if self._allowFieldTruncationHeader is not None:
        headers['AllowFieldTruncationHeader'] = self._allowFieldTruncationHeader

    if call in ('create',
                'merge',
                'update',
                'upsert'):
      if self._assignmentRuleHeader is not None:
        headers['AssignmentRuleHeader'] = self._assignmentRuleHeader

    # CallOptions will only ever be set by the SforcePartnerClient
    if self._callOptions is not None:
      if call in ('create',
                  'merge',
                  'queryAll',
                  'query',
                  'queryMore',
                  'retrieve',
                  'search',
                  'update',
                  'upsert',
                  'convertLead',
                  'login',
                  'delete',
                  'describeGlobal',
                  'describeLayout',
                  'describeTabs',
                  'describeSObject',
                  'describeSObjects',
                  'getDeleted',
                  'getUpdated',
                  'process',
                  'undelete',
                  'getServerTimestamp',
                  'getUserInfo',
                  'setPassword',
                  'resetPassword'):
        headers['CallOptions'] = self._callOptions

    if call in ('create',
                'delete',
                'resetPassword',
                'update',
                'upsert'):
      if self._emailHeader is not None:
        headers['EmailHeader'] = self._emailHeader

    if call in ('describeSObject',
                'describeSObjects'):
      if self._localeOptions is not None:
        headers['LocaleOptions'] = self._localeOptions

    if call == 'login':
      if self._loginScopeHeader is not None:
        headers['LoginScopeHeader'] = self._loginScopeHeader

    if call in ('create',
                'merge',
                'query',
                'retrieve',
                'update',
                'upsert'):
      if self._mruHeader is not None:
        headers['MruHeader'] = self._mruHeader

    if call in ('convertLead',
                'create',
                'delete',
                'describeGlobal',
                'describeLayout',
                'describeSObject',
                'describeSObjects',
                'describeTabs',
                'merge',
                'process',
                'query',
                'retrieve',
                'search',
                'undelete',
                'update',
                'upsert'):
      if self._packageVersionHeader is not None:
        headers['PackageVersionHeader'] = self._packageVersionHeader

    if call in ('query',
                'queryAll',
                'queryMore',
                'retrieve'):
      if self._queryOptions is not None:
        headers['QueryOptions'] = self._queryOptions

    if call == 'delete':
      if self._userTerritoryDeleteHeader is not None:
        headers['UserTerritoryDeleteHeader'] = self._userTerritoryDeleteHeader

    self._sforce.set_options(soapheaders = headers)

  def setStrictResultTyping(self, strictResultTyping):
    '''
    Set whether single results from any of the following calls return the result wrapped in a list,
    or simply the single result object:

      convertLead()
      create()
      delete()
      emptyRecycleBin()
      invalidateSessions()
      merge()
      process()
      retrieve()
      undelete()
      update()
      upsert()
      describeSObjects()
      sendEmail()
    '''
    self._strictResultTyping = strictResultTyping

  def getSessionId(self):
    return self._sessionId

  def getLocation(self):
    return self._location

  def getConnection(self):
    return self._sforce

  def getLastRequest(self):
    return str(self._sforce.last_sent())

  def getLastResponse(self):
    return str(self._sforce.last_received())

  # Core calls

  def convertLead(self, leadConverts):
    '''
    Converts a Lead into an Account, Contact, or (optionally) an Opportunity.
    '''
    self._setHeaders('convertLead')
    return self._handleResultTyping(self._sforce.service.convertLead(leadConverts))

  def create(self, sObjects):
    self._setHeaders('create')
    return self._handleResultTyping(self._sforce.service.create(sObjects))

  def delete(self, ids):
    '''
    Deletes one or more objects
    '''
    self._setHeaders('delete')
    return self._handleResultTyping(self._sforce.service.delete(ids))

  def emptyRecycleBin(self, ids):
    '''
    Permanently deletes one or more objects
    '''
    self._setHeaders('emptyRecycleBin')
    return self._handleResultTyping(self._sforce.service.emptyRecycleBin(ids))
  
  def getDeleted(self, sObjectType, startDate, endDate):
    '''
    Retrieves the list of individual objects that have been deleted within the
    given timespan for the specified object.
    '''
    self._setHeaders('getDeleted')
    return self._sforce.service.getDeleted(sObjectType, startDate, endDate)

  def getUpdated(self, sObjectType, startDate, endDate):
    '''
    Retrieves the list of individual objects that have been updated (added or
    changed) within the given timespan for the specified object.
    '''
    self._setHeaders('getUpdated')
    return self._sforce.service.getUpdated(sObjectType, startDate, endDate)

  def invalidateSessions(self, sessionIds):
    '''
    Invalidate a Salesforce session
  
    This should be used with extreme caution, for the following (undocumented) reason:
    All API connections for a given user share a single session ID
    This will call logout() WHICH LOGS OUT THAT USER FROM EVERY CONCURRENT SESSION
  
    return invalidateSessionsResult
    '''
    self._setHeaders('invalidateSessions')
    return self._handleResultTyping(self._sforce.service.invalidateSessions(sessionIds))
 
  def login(self, username, password, token):
    '''
    Login to Salesforce.com and starts a client session.
  
    Unlike other toolkits, token is a separate parameter, because
    Salesforce doesn't explicitly tell you to append it when it gives
    you a login error.  Folks that are new to the API may not know this.
  
    'username' : Username
    'password' : Password
    'token' : Token
  
    return LoginResult
    '''
    self._setHeaders('login')
    result = self._sforce.service.login(username, password + token)

    # set session header
    header = self.generateHeader('SessionHeader')
    header.sessionId = result['sessionId']
    self.setSessionHeader(header)
    self._sessionId = result['sessionId']

    # change URL to point from test.salesforce.com to something like cs2-api.salesforce.com
    self._setEndpoint(result['serverUrl'])

    # na0.salesforce.com (a.k.a. ssl.salesforce.com) requires ISO-8859-1 instead of UTF-8
    if 'ssl.salesforce.com' in result['serverUrl'] or 'na0.salesforce.com' in result['serverUrl']:
      # currently, UTF-8 is hard-coded in Suds, can't implement this yet
      pass

    return result

  def logout(self):
    '''
    Logout from Salesforce.com
  
    This should be used with extreme caution, for the following (undocumented) reason:
    All API connections for a given user share a single session ID
    Calling logout() LOGS OUT THAT USER FROM EVERY CONCURRENT SESSION
  
    return LogoutResult
    '''
    self._setHeaders('logout')
    return self._sforce.service.logout()

  def merge(self, mergeRequests):
    self._setHeaders('merge')
    return self._handleResultTyping(self._sforce.service.merge(mergeRequests))

  def process(self, processRequests):
    self._setHeaders('process')
    return self._handleResultTyping(self._sforce.service.process(processRequests))

  def query(self, queryString):
    '''
    Executes a query against the specified object and returns data that matches
    the specified criteria.
    '''
    self._setHeaders('query')
    return self._sforce.service.query(queryString)

  def queryAll(self, queryString):
    '''
    Retrieves data from specified objects, whether or not they have been deleted.
    '''
    self._setHeaders('queryAll')
    return self._sforce.service.queryAll(queryString)
  
  def queryMore(self, queryLocator):
    '''
    Retrieves the next batch of objects from a query.
    '''
    self._setHeaders('queryMore')
    return self._sforce.service.queryMore(queryLocator)

  def retrieve(self, fieldList, sObjectType, ids):
    '''
    Retrieves one or more objects based on the specified object IDs.
    '''
    self._setHeaders('retrieve')
    return self._handleResultTyping(self._sforce.service.retrieve(fieldList, sObjectType, ids))

  def search(self, searchString):
    '''
    Executes a text search in your organization's data.
    '''
    self._setHeaders('search')
    return self._sforce.service.search(searchString)

  def undelete(self, ids):
    '''
    Undeletes one or more objects
    '''
    self._setHeaders('undelete')
    return self._handleResultTyping(self._sforce.service.undelete(ids))

  def update(self, sObjects):
    self._setHeaders('update')
    return self._handleResultTyping(self._sforce.service.update(sObjects))

  def upsert(self, externalIdFieldName, sObjects):
    self._setHeaders('upsert')
    return self._handleResultTyping(self._sforce.service.upsert(externalIdFieldName, sObjects))

  # Describe calls

  def describeGlobal(self):
    '''
    Retrieves a list of available objects in your organization
    '''
    self._setHeaders('describeGlobal')
    return self._sforce.service.describeGlobal()

  def describeLayout(self, sObjectType, recordTypeIds = None):
    '''
    Use describeLayout to retrieve information about the layout (presentation
    of data to users) for a given object type. The describeLayout call returns
    metadata about a given page layout, including layouts for edit and
    display-only views and record type mappings. Note that field-level security
    and layout editability affects which fields appear in a layout.
    '''
    self._setHeaders('describeLayout')
    return self._sforce.service.describeLayout(sObjectType, recordTypeIds)

  def describeSObject(self, sObjectsType):
    '''
    Describes metadata (field list and object properties) for the specified
    object.
    '''
    self._setHeaders('describeSObject')
    return self._sforce.service.describeSObject(sObjectsType)

  def describeSObjects(self, sObjectTypes):
    '''
    An array-based version of describeSObject; describes metadata (field list
    and object properties) for the specified object or array of objects.
    '''
    self._setHeaders('describeSObjects')
    return self._handleResultTyping(self._sforce.service.describeSObjects(sObjectTypes))

  # describeSoftphoneLayout not implemented
  # From the docs: "Use this call to obtain information about the layout of a SoftPhone. 
  # Use only in the context of Salesforce CRM Call Center; do not call directly from client programs."

  def describeTabs(self):
    '''
    The describeTabs call returns information about the standard apps and
    custom apps, if any, available for the user who sends the call, including
    the list of tabs defined for each app.
    '''
    self._setHeaders('describeTabs')
    return self._sforce.service.describeTabs()

  # Utility calls

  def getServerTimestamp(self):
    '''
    Retrieves the current system timestamp (GMT) from the Web service.
    '''
    self._setHeaders('getServerTimestamp')
    return self._sforce.service.getServerTimestamp()

  def getUserInfo(self):
    self._setHeaders('getUserInfo')
    return self._sforce.service.getUserInfo()

  def resetPassword(self, userId):
    '''
    Changes a user's password to a system-generated value.
    '''
    self._setHeaders('resetPassword')
    return self._sforce.service.resetPassword(userId)

  def sendEmail(self, emails):
    self._setHeaders('sendEmail')
    return self._handleResultTyping(self._sforce.service.sendEmail(emails))

  def setPassword(self, userId, password):
    '''
    Sets the specified user's password to the specified value.
    '''
    self._setHeaders('setPassword')
    return self._sforce.service.setPassword(userId, password)

  # SOAP header-related calls

  def setAllowFieldTruncationHeader(self, header):
    self._allowFieldTruncationHeader = header

  def setAssignmentRuleHeader(self, header):
    self._assignmentRuleHeader = header

  # setCallOptions() is only implemented in SforcePartnerClient
  # http://www.salesforce.com/us/developer/docs/api/Content/sforce_api_header_calloptions.htm

  def setEmailHeader(self, header):
    self._emailHeader = header

  def setLocaleOptions(self, header):
    self._localeOptions = header

  def setLoginScopeHeader(self, header):
    self._loginScopeHeader = header

  def setMruHeader(self, header):
    self._mruHeader = header

  def setPackageVersionHeader(self, header):
    self._packageVersionHeader = header

  def setQueryOptions(self, header):
    self._queryOptions = header

  def setSessionHeader(self, header):
    self._sessionHeader = header

  def setUserTerritoryDeleteHeader(self, header):
    self._userTerritoryDeleteHeader = header
