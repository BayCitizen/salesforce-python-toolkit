# coding: utf-8

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

import datetime
import re
import string
import sys
import unittest

sys.path.append('../')

from sforce.base import SforceBaseClient

from suds import WebFault

# strings we can look for to ensure headers sent
ALLOW_FIELD_TRUNCATION_HEADER_STRING = '<tns:allowFieldTruncation>false</tns:allowFieldTruncation>'
ASSIGNMENT_RULE_HEADER_STRING = '<tns:useDefaultRule>true</tns:useDefaultRule>'
CALL_OPTIONS_STRING = '<tns:defaultNamespace>*DEVELOPER NAMESPACE PREFIX*</tns:defaultNamespace>'
EMAIL_HEADER_STRING = '<tns:triggerAutoResponseEmail>true</tns:triggerAutoResponseEmail>'
LOCALE_OPTIONS_STRING = '<tns:language>en_US</tns:language>'
# starting in 0.3.7, xsi:type="ns1:ID" is omitted from opening tag
LOGIN_SCOPE_HEADER_STRING = '>00D000xxxxxxxxx</tns:organizationId>'
MRU_HEADER_STRING = '<tns:updateMru>true</tns:updateMru>'
PACKAGE_VERSION_HEADER_STRING = '<tns:namespace>SFGA</tns:namespace>'
QUERY_OPTIONS_STRING = '<tns:batchSize>200</tns:batchSize>'
SESSION_HEADER_STRING = '</tns:sessionId>'
# starting in 0.3.7, xsi:type="ns1:ID" is omitted from opening tag
USER_TERRITORY_DELETE_HEADER_STRING = '>005000xxxxxxxxx</tns:transferToUserId>'

class SforceBaseClientTest(unittest.TestCase):
  def setUp(self):
    pass

  def checkHeaders(self, call):
    result = self.h.getLastRequest()

    if (call != 'login'):
      self.assertTrue(result.find(SESSION_HEADER_STRING) != -1)

    if (call == 'convertLead' or
        call == 'create' or
        call == 'merge' or
        call == 'process' or
        call == 'undelete' or
        call == 'update' or
        call == 'upsert'):
      self.assertTrue(result.find(ALLOW_FIELD_TRUNCATION_HEADER_STRING) != -1)

    if (call == 'create' or
        call == 'merge' or 
        call == 'update' or 
        call == 'upsert'):
      self.assertTrue(result.find(ASSIGNMENT_RULE_HEADER_STRING) != -1)

    # CallOptions will only ever be set by the SforcePartnerClient
    if self.wsdlFormat == 'Partner':
      if (call == 'create' or
          call == 'merge' or
          call == 'queryAll' or
          call == 'query' or
          call == 'queryMore' or
          call == 'retrieve' or
          call == 'search' or
          call == 'update' or
          call == 'upsert' or
          call == 'convertLead' or
          call == 'login' or
          call == 'delete' or
          call == 'describeGlobal' or
          call == 'describeLayout' or
          call == 'describeTabs' or
          call == 'describeSObject' or
          call == 'describeSObjects' or
          call == 'getDeleted' or
          call == 'getUpdated' or
          call == 'process' or
          call == 'undelete' or
          call == 'getServerTimestamp' or
          call == 'getUserInfo' or
          call == 'setPassword' or
          call == 'resetPassword'):
        self.assertTrue(result.find(CALL_OPTIONS_STRING) != -1)

    if (call == 'create' or
        call == 'delete' or
        call == 'resetPassword' or
        call == 'update' or
        call == 'upsert'):
      self.assertTrue(result.find(EMAIL_HEADER_STRING) != -1)

    if (call == 'describeSObject' or
        call == 'describeSObjects'):
      self.assertTrue(result.find(LOCALE_OPTIONS_STRING) != -1)

    if call == 'login':
      self.assertTrue(result.find(LOGIN_SCOPE_HEADER_STRING) != -1)

    if (call == 'create' or
        call == 'merge' or
        call == 'query' or
        call == 'retrieve' or
        call == 'update' or
        call == 'upsert'):
      self.assertTrue(result.find(MRU_HEADER_STRING) != -1)

    if (call == 'convertLead' or
        call == 'create' or
        call == 'delete' or
        call == 'describeGlobal' or
        call == 'describeLayout' or
        call == 'describeSObject' or
        call == 'describeSObjects' or
        call == 'describeTabs' or
        call == 'merge' or
        call == 'process' or
        call == 'query' or
        call == 'retrieve' or
        call == 'search' or
        call == 'undelete' or
        call == 'update' or
        call == 'upsert'):
      self.assertTrue(result.find(PACKAGE_VERSION_HEADER_STRING) != -1)

    if (call == 'query' or
        call == 'queryAll' or
        call == 'queryMore' or
        call == 'retrieve'):
      self.assertTrue(result.find(QUERY_OPTIONS_STRING) != -1)

    if call == 'delete':
      self.assertTrue(result.find(USER_TERRITORY_DELETE_HEADER_STRING) != -1)

  def createLead(self, returnLead = False):
    lead = self.h.generateObject('Lead')
    lead.FirstName = u'Joë'
    lead.LastName = u'Möke'
    lead.Company = u'你好公司'
    lead.Email = 'joe@example.com'

    if returnLead:
      result = self.h.create(lead)
      lead.Id = result.id
      return (result, lead)
    else:
      return self.h.create(lead)

  def createLeads(self, returnLeads = False):
    lead = self.h.generateObject('Lead')
    lead.FirstName = u'Joë'
    lead.LastName = u'Möke'
    lead.Company = u'你好公司'
    lead.Email = 'joe@example.com'

    lead2 = self.h.generateObject('Lead')
    lead2.FirstName = u'Böb'
    lead2.LastName = u'Möke'
    lead2.Company = u'你好公司'
    lead2.Email = 'bob@example.com'

    if returnLeads:
      result = self.h.create((lead, lead2))
      lead.Id = result[0].id
      lead2.Id = result[1].id
      return (result, (lead, lead2))
    else:
      return self.h.create((lead, lead2))

  # Set SOAP headers
  def setHeaders(self, call):
    # no need to manually attach session ID, will happen after login automatically

    if (call == 'convertLead' or
        call == 'create' or
        call == 'merge' or
        call == 'process' or
        call == 'undelete' or
        call == 'update' or
        call == 'upsert'):
      self.setAllowFieldTruncationHeader()

    if (call == 'create' or
        call == 'merge' or 
        call == 'update' or 
        call == 'upsert'):
      self.setAssignmentRuleHeader()

    # CallOptions will only ever be set by the SforcePartnerClient
    if self.wsdlFormat == 'Partner':
      if (call == 'create' or
          call == 'merge' or
          call == 'queryAll' or
          call == 'query' or
          call == 'queryMore' or
          call == 'retrieve' or
          call == 'search' or
          call == 'update' or
          call == 'upsert' or
          call == 'convertLead' or
          call == 'login' or
          call == 'delete' or
          call == 'describeGlobal' or
          call == 'describeLayout' or
          call == 'describeTabs' or
          call == 'describeSObject' or
          call == 'describeSObjects' or
          call == 'getDeleted' or
          call == 'getUpdated' or
          call == 'process' or
          call == 'undelete' or
          call == 'getServerTimestamp' or
          call == 'getUserInfo' or
          call == 'setPassword' or
          call == 'resetPassword'):
        self.setCallOptions()

    if (call == 'create' or
        call == 'delete' or
        call == 'resetPassword' or
        call == 'update' or
        call == 'upsert'):
      self.setEmailHeader()

    if (call == 'describeSObject' or
        call == 'describeSObjects'):
      self.setLocaleOptions()

    if call == 'login':
      self.setLoginScopeHeader()

    if (call == 'create' or
        call == 'merge' or
        call == 'query' or
        call == 'retrieve' or
        call == 'update' or
        call == 'upsert'):
      self.setMruHeader()

    if (call == 'convertLead' or
        call == 'create' or
        call == 'delete' or
        call == 'describeGlobal' or
        call == 'describeLayout' or
        call == 'describeSObject' or
        call == 'describeSObjects' or
        call == 'describeTabs' or
        call == 'merge' or
        call == 'process' or
        call == 'query' or
        call == 'retrieve' or
        call == 'search' or
        call == 'undelete' or
        call == 'update' or
        call == 'upsert'):
      self.setPackageVersionHeader()

    if (call == 'query' or
        call == 'queryAll' or
        call == 'queryMore' or
        call == 'retrieve'):
      self.setQueryOptions()

    if call == 'delete':
      self.setUserTerritoryDeleteHeader()

  def setAllowFieldTruncationHeader(self):
    header = self.h.generateHeader('AllowFieldTruncationHeader');
    header.allowFieldTruncation = False
    self.h.setAllowFieldTruncationHeader(header)

  def setAssignmentRuleHeader(self):
    header = self.h.generateHeader('AssignmentRuleHeader');
    header.useDefaultRule = True
    self.h.setAssignmentRuleHeader(header)

  def setCallOptions(self):
    '''
    Note that this header only applies to the Partner WSDL.
    '''
    if self.wsdlFormat == 'Partner':
      header = self.h.generateHeader('CallOptions');
      header.client = '*MY CLIENT STRING*'
      header.defaultNamespace = '*DEVELOPER NAMESPACE PREFIX*'
      self.h.setCallOptions(header)
    else:
      pass

  def setEmailHeader(self):
    header = self.h.generateHeader('EmailHeader');
    header.triggerAutoResponseEmail = True
    header.triggerOtherEmail = True
    header.triggerUserEmail = True
    self.h.setEmailHeader(header)

  def setLocaleOptions(self):
    header = self.h.generateHeader('LocaleOptions');
    header.language = 'en_US'
    self.h.setLocaleOptions(header)

  def setLoginScopeHeader(self):
    header = self.h.generateHeader('LoginScopeHeader');
    header.organizationId = '00D000xxxxxxxxx'
    #header.portalId = '00D000xxxxxxxxx'
    self.h.setLoginScopeHeader(header)

  def setMruHeader(self):
    header = self.h.generateHeader('MruHeader');
    header.updateMru = True
    self.h.setMruHeader(header)

  def setPackageVersionHeader(self):
    header = self.h.generateHeader('PackageVersionHeader');
    pkg = {}
    pkg['majorNumber'] = 1
    pkg['minorNumber'] = 2
    pkg['namespace'] = 'SFGA'
    header.packageVersions = pkg
    self.h.setPackageVersionHeader(header)

  def setQueryOptions(self):
    header = self.h.generateHeader('QueryOptions');
    header.batchSize = 200
    self.h.setQueryOptions(header)

  def setSessionHeader(self):
    header = self.h.generateHeader('SessionHeader');
    header.sessionId = '*PIGGYBACK SESSION ID HERE*'
    self.h.setSessionHeader(header)

  def setUserTerritoryDeleteHeader(self):
    header = self.h.generateHeader('UserTerritoryDeleteHeader');
    header.transferToUserId = '005000xxxxxxxxx'
    self.h.setUserTerritoryDeleteHeader(header)

  # Core calls

  def testConvertLead(self):
    result = self.createLead()

    self.setHeaders('convertLead')

    leadConvert = self.h.generateObject('LeadConvert')
    leadConvert.leadId = result.id
    leadConvert.convertedStatus = 'Qualified' 
    result = self.h.convertLead(leadConvert)

    self.assertTrue(result.success)
    self.assertTrue(result.accountId[0:3] == '001')
    self.assertTrue(result.contactId[0:3] == '003')
    self.assertTrue(result.leadId[0:3] == '00Q')
    self.assertTrue(result.opportunityId[0:3] == '006')

    self.checkHeaders('convertLead')

  def testCreateCustomObject(self):
    case = self.h.generateObject('Case')
    result = self.h.create(case)

    self.assertTrue(result.success)
    self.assertTrue(result.id[0:3] == '500')
    
    caseNote = self.h.generateObject('Case_Note__c')
    caseNote.case__c = result.id
    caseNote.subject__c = 'my subject'
    caseNote.description__c = 'description here'
    result = self.h.create(caseNote)

    self.assertTrue(result.success)
    self.assertTrue(result.id[0:3] == 'a0E')
  
  def testCreateLead(self):
    self.setHeaders('create')

    result = self.createLead()
 
    self.assertTrue(result.success)
    self.assertTrue(result.id[0:3] == '00Q')

    self.checkHeaders('create')

  def testCreateLeads(self):
    result = self.createLeads()

    self.assertTrue(result[0].success)
    self.assertTrue(result[0].id[0:3] == '00Q')
    self.assertTrue(result[1].success)
    self.assertTrue(result[1].id[0:3] == '00Q')

  def testDeleteLead(self):
    self.setHeaders('delete')

    (result, lead) = self.createLead(True)
    result = self.h.delete(result.id)

    self.assertTrue(result.success)
    self.assertEqual(result.id, lead.Id)

    self.checkHeaders('delete')

  def testDeleteLeads(self):
    (result, (lead, lead2)) = self.createLeads(True)
    result = self.h.delete((result[0].id, result[1].id))

    self.assertTrue(result[0].success)
    self.assertEqual(result[0].id, lead.Id)
    self.assertTrue(result[1].success)
    self.assertEqual(result[1].id, lead2.Id)

  def testEmptyRecycleBinOneObject(self):
    (result, lead) = self.createLead(True)
    result = self.h.delete(result.id)
    result = self.h.emptyRecycleBin(result.id)

    self.assertTrue(result.success)
    self.assertEqual(result.id, lead.Id)

  def testEmptyRecycleBinTwoObjects(self):
    (result, (lead, lead2)) = self.createLeads(True)
    result = self.h.delete((result[0].id, result[1].id))
    result = self.h.emptyRecycleBin((result[0].id, result[1].id))

    self.assertTrue(result[0].success)
    self.assertEqual(result[0].id, lead.Id)
    self.assertTrue(result[1].success)
    self.assertEqual(result[1].id, lead2.Id)

  def testGetDeleted(self):
    self.setHeaders('getDeleted')

    now = datetime.datetime.utcnow()
    result = self.createLead()
    result = self.h.delete(result.id)
    result = self.h.getDeleted('Lead', now.isoformat(), '2019-01-01T23:01:01Z')

    # This will nearly always be one single result
    self.assertTrue(len(result.deletedRecords) > 0)

    for record in result.deletedRecords:
      self.assertTrue(isinstance(record.deletedDate, datetime.datetime))
      self.assertEqual(len(record.id), 18)

    self.checkHeaders('getDeleted')

  def testGetUpdated(self):
    self.setHeaders('getUpdated')

    now = datetime.datetime.utcnow()
    (result, lead) = self.createLead(True)
    result = self.h.update(lead)
    result = self.h.getUpdated('Lead', now.isoformat(), '2019-01-01T23:01:01Z')

    # This will nearly always be one single result
    self.assertTrue(len(result.ids) > 0)

    for id in result.ids:
      self.assertEqual(len(id), 18)

    self.checkHeaders('getUpdated')

  def testInvalidateSession(self):
    result = self.h.invalidateSessions(self.h.getSessionId())
    
    self.assertTrue(result.success)

  def testInvalidateSessions(self):
    result = self.h.invalidateSessions((self.h.getSessionId(), 'foo'))

    self.assertTrue(result[0].success)
    self.assertFalse(result[1].success)

  def testLogin(self):
    # This is really only here to test the login() SOAP headers
    self.setHeaders('login')
    
    try:
      self.h.login('foo', 'bar', 'baz')
    except WebFault:
      pass
    
    self.checkHeaders('login')

  def testLogout(self):
    result = self.h.logout()
    
    self.assertEqual(result, None)

  def testMerge(self):
    self.setHeaders('merge')

    (result, (lead, lead2)) = self.createLeads(True)

    mergeRequest = self.h.generateObject('MergeRequest')
    mergeRequest.masterRecord = lead
    mergeRequest.recordToMergeIds = result[1].id
    result = self.h.merge(mergeRequest)

    self.assertTrue(result.success)
    self.assertEqual(result.id, lead.Id)
    self.assertEqual(result.mergedRecordIds[0], lead2.Id)

    self.checkHeaders('merge')

  def testProcessSubmitRequestMalformedId(self):
    self.setHeaders('process')

    processRequest = self.h.generateObject('ProcessSubmitRequest')
    processRequest.objectId = '*ID OF OBJECT PROCESS REQUEST AFFECTS*'
    processRequest.comments = 'This is what I think.'
    result = self.h.process(processRequest)

    self.assertFalse(result.success)
    self.assertEqual(result.errors[0].statusCode, 'MALFORMED_ID')

    self.checkHeaders('process')

  def testProcessSubmitRequestInvalidId(self):
    processRequest = self.h.generateObject('ProcessSubmitRequest')
    processRequest.objectId = '00Q000xxxxxxxxx'
    processRequest.comments = 'This is what I think.'
    result = self.h.process(processRequest)

    self.assertFalse(result.success)
    self.assertEqual(result.errors[0].statusCode, 'INSUFFICIENT_ACCESS_ON_CROSS_REFERENCE_ENTITY')

  def testProcessWorkitemRequestMalformedId(self):
    processRequest = self.h.generateObject('ProcessWorkitemRequest')
    processRequest.action = 'Approve'
    processRequest.workitemId = '*ID OF OBJECT PROCESS REQUEST AFFECTS*'
    processRequest.comments = 'I approved this request.'
    result = self.h.process(processRequest)

    self.assertFalse(result.success)
    self.assertEqual(result.errors[0].statusCode, 'MALFORMED_ID')

  def testProcessWorkitemRequestInvalidId(self):
    processRequest = self.h.generateObject('ProcessWorkitemRequest')
    processRequest.action = 'Approve'
    processRequest.workitemId = '00Q000xxxxxxxxx'
    processRequest.comments = 'I approved this request.'
    result = self.h.process(processRequest)

    self.assertFalse(result.success)
    self.assertEqual(result.errors[0].statusCode, 'INVALID_CROSS_REFERENCE_KEY')

  # Note that Lead.LastName, Lead.Company, Account.Name can never equal NULL, they are required both
  # via API and UI
  #
  # Also, SOQL does not return fields that are NULL
  def testQueryNoResults(self):
    self.setHeaders('query')

    result = self.h.query('SELECT FirstName, LastName FROM Lead LIMIT 0')
    
    self.assertFalse(hasattr(result, 'records'))
    self.assertEqual(result.size, 0)

    self.checkHeaders('query')

  def testQueryOneResultWithFirstName(self):
    result = self.h.query('SELECT FirstName, LastName FROM Lead WHERE FirstName != NULL LIMIT 1')
    
    self.assertEqual(len(result.records), 1)
    self.assertEqual(result.size, 1)
    self.assertTrue(hasattr(result.records[0], 'FirstName'))
    self.assertTrue(hasattr(result.records[0], 'LastName'))
    self.assertFalse(isinstance(result.records[0].FirstName, list))
    self.assertFalse(isinstance(result.records[0].LastName, list))

  '''
  See explanation below.

  def testQueryOneResultWithoutFirstName(self):
    result = self.h.query('SELECT FirstName, LastName FROM Lead WHERE FirstName = NULL LIMIT 1')
    
    self.assertEqual(len(result.records), 1)
    self.assertEqual(result.size, 1)
    self.assertFalse(hasattr(result.records[0], 'FirstName'))
    self.assertTrue(hasattr(result.records[0], 'LastName'))
    self.assertFalse(isinstance(result.records[0].FirstName, list))
    self.assertFalse(isinstance(result.records[0].LastName, list))
  '''

  def testQueryTwoResults(self):
    result = self.h.query('SELECT FirstName, LastName FROM Lead WHERE FirstName != NULL LIMIT 2')
    
    self.assertTrue(len(result.records) > 1)
    self.assertTrue(result.size > 1)
    for record in result.records:
      self.assertTrue(hasattr(record, 'FirstName'))
      self.assertTrue(hasattr(record, 'LastName'))
      self.assertFalse(isinstance(record.FirstName, list))
      self.assertFalse(isinstance(record.LastName, list))

  def testQueryAllNoResults(self):
    self.setHeaders('queryAll')

    result = self.h.queryAll('SELECT Account.Name, FirstName, LastName FROM Contact LIMIT 0')
    
    self.assertFalse(hasattr(result, 'records'))
    self.assertEqual(result.size, 0)

    self.checkHeaders('queryAll')

  def testQueryAllOneResultWithFirstName(self):
    result = self.h.queryAll('SELECT Account.Name, FirstName, LastName FROM Contact WHERE FirstName != NULL LIMIT 1')
    
    self.assertEqual(len(result.records), 1)
    self.assertEqual(result.size, 1)
    self.assertTrue(hasattr(result.records[0], 'FirstName'))
    self.assertTrue(hasattr(result.records[0], 'LastName'))
    self.assertTrue(hasattr(result.records[0].Account, 'Name'))
    self.assertFalse(isinstance(result.records[0].FirstName, list))
    self.assertFalse(isinstance(result.records[0].LastName, list))
    self.assertFalse(isinstance(result.records[0].Account.Name, list))

  '''
  There's a bug with Salesforce where the query in this test where the Partner WSDL includes 
  FirstName in the SOAP response, but the Enterprise WSDL does not.

  Will report a bug once self-service portal is back up.

  Partner:
"<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns="urn:partner.soap.sforce.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:sf="urn:sobject.partner.soap.sforce.com"><soapenv:Body><queryAllResponse><result xsi:type="QueryResult"><done>true</done><queryLocator xsi:nil="true"/><records xsi:type="sf:sObject"><sf:type>Contact</sf:type><sf:Id xsi:nil="true"/><sf:Account xsi:type="sf:sObject"><sf:type>Account</sf:type><sf:Id xsi:nil="true"/><sf:Name>Unknown</sf:Name></sf:Account><sf:FirstName xsi:nil="true"/><sf:LastName>Administrator</sf:LastName></records><size>1</size></result></queryAllResponse></soapenv:Body></soapenv:Envelope>"

  Enterprise:
"<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns="urn:enterprise.soap.sforce.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:sf="urn:sobject.enterprise.soap.sforce.com"><soapenv:Body><queryAllResponse><result><done>true</done><queryLocator xsi:nil="true"/><records xsi:type="sf:Contact"><sf:Account xsi:type="sf:Account"><sf:Name>Unknown</sf:Name></sf:Account><sf:LastName>Administrator</sf:LastName></records><size>1</size></result></queryAllResponse></soapenv:Body></soapenv:Envelope>"

  def testQueryAllOneResultWithoutFirstName(self):
    result = self.h.queryAll('SELECT Account.Name, FirstName, LastName FROM Contact WHERE FirstName = NULL LIMIT 1')
    print result
    
    self.assertEqual(len(result.records), 1)
    self.assertEqual(result.size, 1)
    self.assertFalse(hasattr(result.records[0], 'FirstName'))
    self.assertTrue(hasattr(result.records[0], 'LastName'))
    self.assertTrue(hasattr(result.records[0].Account, 'Name'))
    self.assertFalse(isinstance(result.records[0].FirstName, list))
    self.assertFalse(isinstance(result.records[0].LastName, list))
    self.assertFalse(isinstance(result.records[0].Account.Name, list))
  '''

  def testQueryAllTwoResults(self):
    result = self.h.queryAll('SELECT Account.Name, FirstName, LastName FROM Contact WHERE FirstName != NULL LIMIT 2')
    
    self.assertTrue(len(result.records) > 1)
    self.assertTrue(result.size > 1)
    for record in result.records:
      self.assertTrue(hasattr(record, 'FirstName'))
      self.assertTrue(hasattr(record, 'LastName'))
      self.assertTrue(hasattr(record.Account, 'Name'))
      self.assertFalse(isinstance(record.FirstName, list))
      self.assertFalse(isinstance(record.LastName, list))
      self.assertFalse(isinstance(record.Account.Name, list))

  def testQueryMore(self):
    self.setHeaders('queryMore')

    result = self.h.queryAll('SELECT FirstName, LastName FROM Lead')
    
    while (result.done == False):
      self.assertTrue(result.queryLocator != None)
      self.assertEqual(len(result.records), 200)
      result = self.h.queryMore(result.queryLocator)

    self.assertTrue(len(result.records) > 1)
    self.assertTrue(len(result.records) <= 200)
    self.assertTrue(result.done)
    self.assertEqual(result.queryLocator, None)

    self.checkHeaders('queryMore')
    
  def testRetrievePassingList(self):
    self.setHeaders('retrieve')

    (result, lead) = self.createLead(True)
    result = self.h.retrieve('FirstName, LastName, Company, Email', 'Lead', [result.id])

    self.assertEqual(result.Id, lead.Id)
    self.assertEqual(result.type, 'Lead')
    self.assertEqual(result.FirstName, lead.FirstName)
    self.assertEqual(result.LastName, lead.LastName)
    self.assertEqual(result.Company, lead.Company)
    self.assertEqual(result.Email, lead.Email)

    self.checkHeaders('retrieve')

  def testRetrievePassingString(self):
    (result, lead) = self.createLead(True)
    result = self.h.retrieve('FirstName, LastName, Company, Email', 'Lead', result.id)

    self.assertEqual(result.Id, lead.Id)
    self.assertEqual(result.type, 'Lead')
    self.assertEqual(result.FirstName, lead.FirstName)
    self.assertEqual(result.LastName, lead.LastName)
    self.assertEqual(result.Company, lead.Company)
    self.assertEqual(result.Email, lead.Email)

  def testRetrievePassingTuple(self):
    (result, lead) = self.createLead(True)
    result = self.h.retrieve('FirstName, LastName, Company, Email', 'Lead', (result.id))

    self.assertEqual(result.Id, lead.Id)
    self.assertEqual(result.type, 'Lead')
    self.assertEqual(result.FirstName, lead.FirstName)
    self.assertEqual(result.LastName, lead.LastName)
    self.assertEqual(result.Company, lead.Company)
    self.assertEqual(result.Email, lead.Email)
    
  def testRetrievePassingListOfTwoIds(self):
    self.setHeaders('retrieve')

    (result, lead) = self.createLead(True)
    result = self.h.retrieve('FirstName, LastName, Company, Email', 'Lead', [result.id, result.id])

    self.assertEqual(result[0].Id, lead.Id)
    self.assertEqual(result[0].type, 'Lead')
    self.assertEqual(result[0].FirstName, lead.FirstName)
    self.assertEqual(result[0].LastName, lead.LastName)
    self.assertEqual(result[0].Company, lead.Company)
    self.assertEqual(result[0].Email, lead.Email)
    self.assertEqual(result[1].Id, lead.Id)
    self.assertEqual(result[1].type, 'Lead')
    self.assertEqual(result[1].FirstName, lead.FirstName)
    self.assertEqual(result[1].LastName, lead.LastName)
    self.assertEqual(result[1].Company, lead.Company)
    self.assertEqual(result[1].Email, lead.Email)

    self.checkHeaders('retrieve')

  def testSearchNoResults(self):
    self.setHeaders('search')

    result = self.h.search('FIND {asdfasdffdsaasdl;fjkwelhnfd} IN Name Fields RETURNING Lead(Name, Phone)')
    
    self.assertEqual(len(result.searchRecords), 0)

    self.checkHeaders('search')

  def testUndeleteLead(self):
    self.setHeaders('undelete')

    (result, lead) = self.createLead(True)
    result = self.h.delete(result.id)
    result = self.h.undelete(result.id)

    self.assertTrue(result.success)
    self.assertEqual(result.id, lead.Id)

    self.checkHeaders('undelete')

  def testUndeleteLeads(self):
    (result, (lead, lead2)) = self.createLeads(True)
    result = self.h.delete((result[0].id, result[1].id))
    result = self.h.undelete((result[0].id, result[1].id))

    self.assertTrue(result[0].success)
    self.assertEqual(result[0].id, lead.Id)
    self.assertTrue(result[1].success)
    self.assertEqual(result[1].id, lead2.Id)

  def testUpdateNoFieldsToNull(self):
    self.setHeaders('update')

    (result, lead) = self.createLead(True)

    lead.fieldsToNull = ()

    result = self.h.update(lead)
    self.assertTrue(result.success)
    self.assertEqual(result.id, lead.Id)

    self.checkHeaders('update')

  def testUpsertCreate(self):
    self.setHeaders('upsert')

    lead = self.h.generateObject('Lead')
    lead.FirstName = u'Joë'
    lead.LastName = u'Möke'
    lead.Company = u'你好公司'
    lead.Email = 'joe@example.com'
    result = self.h.upsert('Id', lead)

    self.assertTrue(result.created)
    self.assertTrue(result.id[0:3] == '00Q')
    self.assertTrue(result.success)

    self.checkHeaders('upsert')

  def testUpsertUpdate(self):
    (result, lead) = self.createLead(True)
    result = self.h.upsert('Id', lead)

    self.assertFalse(result.created)
    self.assertEqual(result.id, lead.Id)
    self.assertTrue(result.success)

  # Describe calls

  def testDescribeGlobal(self):
    self.setHeaders('describeGlobal')

    result = self.h.describeGlobal()

    self.assertTrue(hasattr(result, 'encoding'))
    self.assertTrue(hasattr(result, 'maxBatchSize'))

    foundAccount = False
    for object in result.sobjects:
      if object.name == 'Account':
        foundAccount = True 

    self.assertTrue(foundAccount)

    self.checkHeaders('describeGlobal')

  def testDescribeLayout(self):
    self.setHeaders('describeLayout')

    result = self.h.describeLayout('Lead', '012000000000000AAA') # Master Record Type

    self.assertEqual(result[1][0].recordTypeId, '012000000000000AAA')

    self.checkHeaders('describeLayout')

  def testDescribeSObject(self):
    self.setHeaders('describeSObject')

    result = self.h.describeSObject('Lead')

    self.assertTrue(hasattr(result, 'activateable'))
    self.assertTrue(hasattr(result, 'childRelationships'))
    self.assertEqual(result.keyPrefix, '00Q')
    self.assertEqual(result.name, 'Lead')

    self.checkHeaders('describeSObject')

  def testDescribeSObjects(self):
    self.setHeaders('describeSObjects')

    result = self.h.describeSObjects(('Contact', 'Account'))

    self.assertTrue(hasattr(result[0], 'activateable'))
    self.assertTrue(hasattr(result[0], 'childRelationships'))
    self.assertEqual(result[0].keyPrefix, '003')
    self.assertEqual(result[0].name, 'Contact')

    self.assertTrue(hasattr(result[1], 'activateable'))
    self.assertTrue(hasattr(result[1], 'childRelationships'))
    self.assertEqual(result[1].keyPrefix, '001')
    self.assertEqual(result[1].name, 'Account')

    self.checkHeaders('describeSObjects')

  def testDescribeTabs(self):
    self.setHeaders('describeTabs')

    result = self.h.describeTabs()
    self.assertTrue(hasattr(result[0], 'tabs'))

    self.checkHeaders('describeTabs')

  # Utility calls

  def testGetServerTimestamp(self):
    self.setHeaders('getServerTimestamp')

    result = self.h.getServerTimestamp()

    self.assertTrue(isinstance(result.timestamp, datetime.datetime))

    self.checkHeaders('getServerTimestamp')

  def testGetUserInfo(self):
    self.setHeaders('getUserInfo')

    result = self.h.getUserInfo()

    self.assertTrue(hasattr(result, 'userEmail'))
    self.assertTrue(hasattr(result, 'userId'))

    self.checkHeaders('getUserInfo')

  def testResetPassword(self):
    self.setHeaders('resetPassword')

    try:
      self.h.resetPassword('005000xxxxxxxxx')
      self.fail('WebFault not thrown')
    except WebFault:
      pass

    self.checkHeaders('resetPassword')

  def testSendSingleEmailFail(self):
    self.setHeaders('sendEmail')

    email = self.h.generateObject('SingleEmailMessage')
    email.toAddresses = 'joeexample.com'
    email.subject = 'This is my subject.'
    email.plainTextBody = 'This is the plain-text body of my email.'
    result = self.h.sendEmail([email])

    self.assertFalse(result.success)
    self.assertEqual(result.errors[0].statusCode, 'INVALID_EMAIL_ADDRESS')

    self.checkHeaders('sendEmail')

  def testSendSingleEmailPass(self):
    email = self.h.generateObject('SingleEmailMessage')
    email.toAddresses = 'joe@example.com'
    email.subject = 'This is my subject.'
    email.plainTextBody = 'This is the plain-text body of my email.'
    result = self.h.sendEmail([email])

    self.assertTrue(result.success)

  def testSendMassEmailFail(self):
    email = self.h.generateObject('MassEmailMessage')
    email.targetObjectIds = (('*LEAD OR CONTACT ID TO EMAIL*', '*ANOTHER LEAD OR CONTACT TO EMAIL*'))
    email.templateId = '*EMAIL TEMPLATE ID TO USE*'
    result = self.h.sendEmail([email])
 
    self.assertFalse(result.success)
    self.assertEqual(result.errors[0].statusCode, 'INVALID_ID_FIELD')

  # To make these tests as portable as possible, we won't depend on a particular templateId
  # to test to make sure our mass emails succeed.  From the failure message we can gather that 
  # SFDC is successfully receiving our SOAP message, and reasonably infer that our code works.

  def testSetPassword(self):
    self.setHeaders('setPassword')

    try:
      self.h.setPassword('*USER ID HERE*', '*NEW PASSWORD HERE*')
      self.fail('WebFault not thrown')
    except WebFault:
      pass

    self.checkHeaders('setPassword')

  # Toolkit-Specific Utility Calls:

  def testGenerateHeader(self):
    header = self.h.generateHeader('SessionHeader')
    
    self.assertEqual(header.sessionId, None)

  def testGenerateObject(self):
    account = self.h.generateObject('Account')

    self.assertEqual(account.fieldsToNull, [])
    self.assertEqual(account.Id, None)
    self.assertEqual(account.type, 'Account')

  def testGetLastRequest(self):
    self.h.getServerTimestamp()
    result = self.h.getLastRequest()

    self.assertTrue(result.find(':getServerTimestamp/>') != -1)

  def testGetLastResponse(self):
    self.h.getServerTimestamp()
    result = self.h.getLastResponse()

    self.assertTrue(result.find('<getServerTimestampResponse>') != -1)

  # SOAP Headers tested as part of the method calls

if __name__ == '__main__':
  unittest.main()

