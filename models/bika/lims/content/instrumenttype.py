from dependencies.dependency import ClassSecurityInfo
from dependencies.dependency import *
from dependencies.dependency import View, ModifyPortalContent
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IInstrumentType
from dependencies.dependency import implements

schema = BikaSchema.copy()

schema['description'].schemata = 'default'
schema['description'].widget.visible = True

class InstrumentType(BaseContent):
    implements(IInstrumentType)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(InstrumentType, PROJECTNAME)
