from openerp import fields, models
from base_olims_model import BaseOLiMSModel
from fields.string_field import StringField
from fields.boolean_field import BooleanField
from fields.date_time_field import DateTimeField

schema = (fields.Many2one(string='Container',
        required = False,
        comodel_name='olims.container',
    ),
        fields.Many2one(string='Preservation',
        required = False,
        comodel_name='olims.preservation',
    ),


    BooleanField('Separate',
        default=False
    ),
            fields.Many2one(string='Analyses',
        required = False,
        comodel_name='olims.analysis',
    ),

    DateTimeField('DatePreserved',
    ),

    StringField('Preserver',
        searchable=True
    ),
          
    fields.Char(string='Days'),
    fields.Char(string='Hours'),
    fields.Char(string='Minutes'),
)

class SamplePartition(models.Model, BaseOLiMSModel):
    _name='olims.sample_partition'

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def _getCatalogTool(self):
        from lims.catalog import getCatalog
        return getCatalog(self)

    def Title(self):
        """ Return the Sample ID as title """
        return safe_unicode(self.getId()).encode('utf-8')

    #security.declarePublic('getAnalyses')

    def getAnalyses(self):
        """ return list of titles of analyses linked to this sample Partition """
        analyses = sorted(self.getBackReferences("AnalysisSamplePartition"))
        return analyses

    #security.declarePublic('current_date')

    def current_date(self):
        """ return current date """
        return DateTime()

    #security.declarePublic('disposal_date')

    def disposal_date(self):
        """ return disposal date """

        DateSampled = self.getDateSampled()

        # fallback to sampletype retention period
        st_retention = self.aq_parent.getSampleType().getRetentionPeriod()

        # but prefer retention period from preservation
        pres = self.getPreservation()
        pres_retention = pres and pres.getRetentionPeriod() or None

        rp = pres_retention and pres_retention or None
        rp = rp or st_retention

        td = timedelta(
            days='days' in rp and int(rp['days']) or 0,
            hours='hours' in rp and int(rp['hours']) or 0,
            minutes='minutes' in rp and int(rp['minutes']) or 0)

        dis_date = DateSampled and dt2DT(DT2dt(DateSampled) + td) or None
        return dis_date

    def workflow_script_preserve(self):
        workflow = getToolByName(self, 'portal_workflow')
        sample = self.aq_parent
        # Transition our analyses
        analyses = self.getBackReferences('AnalysisSamplePartition')
        if analyses:
            for analysis in analyses:
                doActionFor(analysis, "preserve")
        # if all our siblings are now up to date, promote sample and ARs.
        parts = sample.objectValues("SamplePartition")
        if parts:
            lower_states = ['to_be_sampled', 'to_be_preserved', ]
            escalate = True
            for part in parts:
                if workflow.getInfoFor(part, 'review_state') in lower_states:
                    escalate = False
            if escalate:
                doActionFor(sample, "preserve")
                for ar in sample.getAnalysisRequests():
                    doActionFor(ar, "preserve")

    def workflow_transition_expire(self):
        self.setDateExpired(DateTime())
        self.reindexObject(idxs=["review_state", "getDateExpired", ])

    def workflow_script_sample(self):
        if skip(self, "sample"):
            return
        sample = self.aq_parent
        workflow = getToolByName(self, 'portal_workflow')
        # Transition our analyses
        analyses = self.getBackReferences('AnalysisSamplePartition')
        for analysis in analyses:
            doActionFor(analysis, "sample")
        # if all our siblings are now up to date, promote sample and ARs.
        parts = sample.objectValues("SamplePartition")
        if parts:
            lower_states = ['to_be_sampled', ]
            escalate = True
            for part in parts:
                pstate = workflow.getInfoFor(part, 'review_state')
                if pstate in lower_states:
                    escalate = False
            if escalate:
                doActionFor(sample, "sample")
                for ar in sample.getAnalysisRequests():
                    doActionFor(ar, "sample")

    def workflow_script_to_be_sampled(self,cr,uid,ids,context=None):
            for items in self.browse(cr,uid,ids,context):
                analysis = self.pool.get('olims.analysis_request').browse(cr,uid,items.Analysis_Request.id,context)
            self.write(cr, uid, ids, {
                'state': analysis.state, 'DateDue':datetime.datetime.now()
            }, context=context)
            return True


    def workflow_script_to_be_preserved(self):
        if skip(self, "to_be_preserved"):
            return
        sample = self.aq_parent
        workflow = getToolByName(self, 'portal_workflow')
        # Transition our analyses
        analyses = self.getBackReferences('AnalysisSamplePartition')
        for analysis in analyses:
            doActionFor(analysis, "to_be_preserved")
        # if all our siblings are now up to date, promote sample and ARs.
        parts = sample.objectValues("SamplePartition")
        if parts:
            lower_states = ['to_be_sampled', 'to_be_preserved', ]
            escalate = True
            for part in parts:
                if workflow.getInfoFor(part, 'review_state') in lower_states:
                    escalate = False
            if escalate:
                doActionFor(sample, "to_be_preserved")
                for ar in sample.getAnalysisRequests():
                    doActionFor(ar, "to_be_preserved")

    def workflow_script_sample_due(self):
        if skip(self, "sample_due"):
            return
        sample = self.aq_parent
        workflow = getToolByName(self, 'portal_workflow')
        # Transition our analyses
        analyses = self.getBackReferences('AnalysisSamplePartition')
        for analysis in analyses:
            doActionFor(analysis, "sample_due")
        # if all our siblings are now up to date, promote sample and ARs.
        parts = sample.objectValues("SamplePartition")
        if parts:
            lower_states = ['to_be_preserved', ]
            escalate = True
            for part in parts:
                pstate = workflow.getInfoFor(part, 'review_state')
                if pstate in lower_states:
                    escalate = False
            if escalate:
                doActionFor(sample, "sample_due")
                for ar in sample.getAnalysisRequests():
                    doActionFor(ar, "sample_due")

    def workflow_script_receive(self):
        if skip(self, "receive"):
            return
        sample = self.aq_parent
        workflow = getToolByName(self, 'portal_workflow')
        sample_state = workflow.getInfoFor(sample, 'review_state')
        self.setDateReceived(DateTime())
        self.reindexObject(idxs=["getDateReceived", ])
        # Transition our analyses
        analyses = self.getBackReferences('AnalysisSamplePartition')
        for analysis in analyses:
            doActionFor(analysis, "receive")
        # if all sibling partitions are received, promote sample
        if not skip(sample, "receive", peek=True):
            due = [sp for sp in sample.objectValues("SamplePartition")
                   if workflow.getInfoFor(sp, 'review_state') == 'sample_due']
            if sample_state == 'sample_due' and not due:
                doActionFor(sample, 'receive')

    def workflow_script_reinstate(self):
        if skip(self, "reinstate"):
            return
        sample = self.aq_parent
        workflow = getToolByName(self, 'portal_workflow')
        self.reindexObject(idxs=["cancellation_state", ])
        sample_c_state = workflow.getInfoFor(sample, 'cancellation_state')
        # if all sibling partitions are active, activate sample
        if not skip(sample, "reinstate", peek=True):
            cancelled = [sp for sp in sample.objectValues("SamplePartition")
                         if workflow.getInfoFor(sp, 'cancellation_state') == 'cancelled']
            if sample_c_state == 'cancelled' and not cancelled:
                workflow.doActionFor(sample, 'reinstate')

    def workflow_script_cancel(self):
        if skip(self, "cancel"):
            return
        sample = self.aq_parent
        workflow = getToolByName(self, 'portal_workflow')
        self.reindexObject(idxs=["cancellation_state", ])
        sample_c_state = workflow.getInfoFor(sample, 'cancellation_state')
        # if all sibling partitions are cancelled, cancel sample
        if not skip(sample, "cancel", peek=True):
            active = [sp for sp in sample.objectValues("SamplePartition")
                      if workflow.getInfoFor(sp, 'cancellation_state') == 'active']
            if sample_c_state == 'active' and not active:
                workflow.doActionFor(sample, 'cancel')

SamplePartition.initialze(schema)