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

import test_base
import test_config
from sforce.partner import SforcePartnerClient

from suds import WebFault
  
class SforcePartnerClientTest(test_base.SforceBaseClientTest):
  wsdlFormat = 'Partner'
  h = None

  def setUp(self):
    if self.h is None:
      self.h = SforcePartnerClient('../partner.wsdl.xml')
      self.h.login(test_config.USERNAME, test_config.PASSWORD, test_config.TOKEN)

  def testSearchOneResult(self):
    result = self.h.search('FIND {Single User} IN Name Fields RETURNING Lead(Name, Phone, Fax, Description, DoNotCall)')

    self.assertEqual(len(result.searchRecords), 1)
    self.assertEqual(result.searchRecords[0].record.Name, 'Single User')
    # it's not a string, it's a SAX Text object, but it can be cast to a string
    # just need to make sure it's not a bool
    self.assertTrue(result.searchRecords[0].record.DoNotCall in ('false', 'true'))
    # make sure we get None and not ''
    self.assertEqual(result.searchRecords[0].record.Description, None)


  def testSearchManyResults(self):
    result = self.h.search(u'FIND {Joë Möke} IN Name Fields RETURNING Lead(Name, Phone, DoNotCall, Company)')

    self.assertTrue(len(result.searchRecords) > 1)
    for searchRecord in result.searchRecords:
      self.assertEqual(searchRecord.record.Name, u'Joë Möke')
      self.assertEqual(searchRecord.record.Company, u'你好公司')
      self.assertTrue(searchRecord.record.DoNotCall in ('false', 'true'))

  def testUpdateOneFieldToNull(self):
    self.setHeaders('update')

    (result, lead) = self.createLead(True)

    lead.fieldsToNull = ('Email')
    lead.Email = None

    result = self.h.update(lead)
    self.assertTrue(result.success)
    self.assertEqual(result.id, lead.Id)

    result = self.h.retrieve('FirstName, LastName, Company, Email', 'Lead', (lead.Id))
    self.assertEqual(result.FirstName, u'Joë')
    self.assertEqual(result.LastName, u'Möke')
    self.assertEqual(result.Company, u'你好公司')
    self.assertEqual(result.Email, None)

  def testUpdateTwoFieldsToNull(self):
    self.setHeaders('update')

    (result, lead) = self.createLead(True)

    lead.fieldsToNull = ('FirstName', 'Email')
    lead.Email = None
    lead.FirstName = None

    result = self.h.update(lead)
    self.assertTrue(result.success)
    self.assertEqual(result.id, lead.Id)

    result = self.h.retrieve('FirstName, LastName, Company, Email', 'Lead', (lead.Id))

    self.assertEqual(result.FirstName, None)
    self.assertEqual(result.LastName, u'Möke')
    self.assertEqual(result.Email, None)

if __name__ == '__main__':
  unittest.main('test_partner')
