"""Client - the main organisational entity in bika.
"""
from dependencies.dependency import ClassSecurityInfo
from dependencies.dependency import schemata
from dependencies import atapi
from dependencies.dependency import DisplayList
from dependencies.dependency import permissions
from dependencies.dependency import getToolByName
from dependencies.dependency import safe_unicode
from lims import PMF, bikaMessageFactory as _
from lims import interfaces
from lims.config import *
from lims.content.organisation import Organisation
from lims.interfaces import IClient
from lims.utils import isActive
from dependencies.dependency import getUtility
from dependencies.dependency import implements
from dependencies.dependency import alsoProvides
import json
import sys
from lims.workflow import getCurrentState, StateFlow, InactiveState

schema = Organisation.schema.copy() + atapi.Schema((
    atapi.StringField('ClientID',
        required = 1,
        searchable = True,
        validators = ('uniquefieldvalidator', 'standard_id_validator'),
        widget = atapi.StringWidget(
            label=_("Client ID"),
        ),
    ),
    atapi.BooleanField('BulkDiscount',
        default = False,
        write_permission = ManageClients,
        widget = atapi.BooleanWidget(
            label=_("Bulk discount applies"),
        ),
    ),
    atapi.BooleanField('MemberDiscountApplies',
        default = False,
        write_permission = ManageClients,
        widget = atapi.BooleanWidget(
            label=_("Member discount applies"),
        ),
    ),
    atapi.LinesField('EmailSubject',
        schemata = 'Preferences',
        default = ['ar', ],
        vocabulary = EMAIL_SUBJECT_OPTIONS,
        widget = atapi.MultiSelectionWidget(
            description=_("Items to be included in email subject lines"),
            label=_("Email subject line"),
        ),
    ),
    atapi.ReferenceField('DefaultCategories',
        schemata = 'Preferences',
        required = 0,
        multiValued = 1,
        vocabulary = 'getAnalysisCategories',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('AnalysisCategory',),
        relationship = 'ClientDefaultCategories',
        widget = atapi.ReferenceWidget(
            checkbox_bound = 0,
            label=_("Default categories"),
            description=_("Always expand the selected categories in client views"),
        ),
    ),
    atapi.ReferenceField('RestrictedCategories',
        schemata = 'Preferences',
        required = 0,
        multiValued = 1,
        vocabulary = 'getAnalysisCategories',
        validators = ('restrictedcategoriesvalidator',),
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('AnalysisCategory',),
        relationship = 'ClientRestrictedCategories',
        widget = atapi.ReferenceWidget(
            checkbox_bound = 0,
            label=_("Restrict categories"),
            description=_("Show only selected categories in client views"),
        ),
    ),
    atapi.StringField('DefaultARSpecs',
        schemata = "Preferences",
        default = 'ar_specs',
        vocabulary = DEFAULT_AR_SPECS,
        widget = atapi.SelectionWidget(
            label=_("Default AR Specifications"),
            description=_("DefaultARSpecs_description"),
            format='select',
        )
    ),
    atapi.BooleanField('DefaultDecimalMark',
        schemata = "Preferences",
        default = True,
        widget = atapi.BooleanWidget(
            label=_("Default decimal mark"),
            description=_("The decimal mark selected in Bika Setup will be used."),
        )
    ),
    atapi.StringField('DecimalMark',
        schemata = "Preferences",
        vocabulary=DECIMAL_MARKS,
        default = ".",
        widget = atapi.SelectionWidget(
            label=_("Custom decimal mark"),
            description=_("Decimal mark to use in the reports from this Client."),
            format = 'select',
        )
    ),
))

schema['AccountNumber'].write_permission = ManageClients
schema['title'].widget.visible = False
schema['description'].widget.visible = False
schema['EmailAddress'].schemata = 'default'

schema.moveField('ClientID', after='Name')

class Client(Organisation):
    implements(IClient)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the Organisation's Name as its title """
        return safe_unicode(self.getField('Name').get(self)).encode('utf-8')

    security.declarePublic('getContactFromUsername')
    def getContactFromUsername(self, username):
        for contact in self.objectValues('Contact'):
            if contact.getUsername() == username:
                return contact.UID()

    security.declarePublic('getContactUIDForUser')
    def getContactUIDForUser(self):
        """ get the UID of the user associated with the authenticated user
        """
        membership_tool = getToolByName(self, 'portal_membership')
        member = membership_tool.getAuthenticatedMember()
        username = member.getUserName()
        r = self.portal_catalog(
            portal_type = 'Contact',
            getUsername = username
        )
        if len(r) == 1:
            return r[0].UID


    security.declarePublic('getARImportOptions')
    def getARImportOptions(self):
        return ARIMPORT_OPTIONS

    security.declarePublic('getAnalysisCategories')
    def getAnalysisCategories(self):
        """ return all available analysis categories """
        bsc = getToolByName(self, 'bika_setup_catalog')
        cats = []
        for st in bsc(portal_type = 'AnalysisCategory',
                      inactive_state = 'active',
                      sort_on = 'sortable_title'):
            cats.append((st.UID, st.Title))
        return DisplayList(cats)

    def getContacts(self, only_active=True):
        """ Return an array containing the contacts from this Client
        """
        contacts = []
        if only_active:
            contacts = [c for c in self.objectValues('Contact') if
                        getCurrentState(c, StateFlow.inactive) == InactiveState.active]
        else:
            contacts = self.objectValues('Contact')
        return contacts;

    def getDecimalMark(self):
        """ Return the decimal mark to be used on reports for this
            client. If the client has DefaultDecimalMark selected, the
            Default value from Bika Setup will be returned. Otherwise,
            will return the value of DecimalMark.
        """
        if self.getDefaultDecimalMark() == False:
            return self.Schema()['DecimalMark'].get(self)
        return self.bika_setup.getDecimalMark()


schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)

atapi.registerType(Client, PROJECTNAME)
