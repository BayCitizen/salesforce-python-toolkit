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

from base import SforceBaseClient

import suds.sudsobject

class SforceEnterpriseClient(SforceBaseClient):
  def __init__(self, wsdl, **kwargs):
    super(SforceEnterpriseClient, self).__init__(wsdl, **kwargs)

  # Core calls

  def convertLead(self, leadConverts):
    xml = self._marshallSObjects(leadConverts)
    return super(SforceEnterpriseClient, self).convertLead(xml)

  def create(self, sObjects):
    xml = self._marshallSObjects(sObjects)
    return super(SforceEnterpriseClient, self).create(xml)

  def merge(self, sObjects):
    xml = self._marshallSObjects(sObjects)
    return super(SforceEnterpriseClient, self).merge(xml)

  def process(self, sObjects):
    xml = self._marshallSObjects(sObjects)
    return super(SforceEnterpriseClient, self).process(xml)

  def retrieve(self, fieldList, sObjectType, ids):
    '''
    Currently, this uses query() to emulate the retrieve() functionality, as suds' unmarshaller
    borks on the sf: prefix that Salesforce prepends to all fields other than Id and type (any
    fields not defined in the 'sObject' section of the Enterprise WSDL)
    '''
    # HACK HACK HACKITY HACK
    
    if not isinstance(ids, (list, tuple)):
      ids = (ids, )

    # The only way to make sure we return objects in the correct order, and return None where an
    # object can't be retrieved by Id, is to query each ID individually
    sObjects = []
    for id in ids:
      queryString = 'SELECT Id, ' + fieldList + ' FROM ' + sObjectType + ' WHERE Id = \'' + id + '\' LIMIT 1'
      queryResult = self.query(queryString)

      if queryResult.size == 0:
        sObjects.append(None)
        continue

      # There will exactly one record in queryResult.records[] at this point
      record = queryResult.records[0]
      sObject = self.generateObject(sObjectType)
      for (k, v) in record:
        setattr(sObject, k, v)
      sObjects.append(sObject)

    return self._handleResultTyping(sObjects)
  
  def search(self, searchString):
    searchResult = super(SforceEnterpriseClient, self).search(searchString)

    # HACK <result/> gets unmarshalled as '' instead of an empty SearchResult
    # return an empty SearchResult instead
    if searchResult == '':
      return self._sforce.factory.create('SearchResult')

    return searchResult

  def update(self, sObjects):
    xml = self._marshallSObjects(sObjects)
    return super(SforceEnterpriseClient, self).update(xml)

  def upsert(self, externalIdFieldName, sObjects):
    xml = self._marshallSObjects(sObjects)
    return super(SforceEnterpriseClient, self).upsert(externalIdFieldName, xml)

  # Utility calls

  def sendEmail(self, sObjects):
    xml = self._marshallSObjects(sObjects)
    return super(SforceEnterpriseClient, self).sendEmail(xml)
