from dependencies.dependency import aq_inner
from dependencies.dependency import aq_parent
from dependencies.dependency import getToolByName
from dependencies.dependency import REFERENCE_CATALOG
from bika.lims.permissions import AddStorageLocation

def upgrade(tool):
    """ Add Storage locacations to ARs and Samples.
    """
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    bc = getToolByName(portal, 'bika_catalog')
    for brain in bc(portal_type='AnalysisRequest'):
        obj = brain.getObject()
        if not obj.getPriority():
            obj.setDefaultPriority()
            #obj.reindexObject()

