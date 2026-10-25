import tempfile
from pathlib import Path
import unittest
from governor_workbench.store import Store


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.store=Store(Path(self.tmp.name)/'journal.db')
        self.context={'scope_hash':'scope','projects':[{'id':'a','evidence_hash':'source'}],
            'intake':[{'project_id':'a','evidence_complete':True,'memories_present':True}]}
        self.fields={'requirements':'Goal and acceptance','test_strategy':'Unit and browser checks',
                     'dependencies':'No dependencies identified','open_evidence':'Runtime not verified'}

    def test_acceptance_is_explicit_and_source_bound(self):
        from governor_workbench.intake import Intake
        book=Intake(self.store)
        self.assertFalse(book.accepted('a','source'))
        book.accept(self.context,'scope','a',self.fields)
        self.assertTrue(book.accepted('a','source'))
        self.assertFalse(book.accepted('a','changed'))

    def test_missing_fields_and_stale_context_rejected(self):
        from governor_workbench.intake import Intake
        book=Intake(self.store)
        with self.assertRaises(ValueError): book.accept(self.context,'old','a',self.fields)
        with self.assertRaises(ValueError): book.accept(self.context,'scope','a',{'requirements':'Goal'})
        with self.assertRaises(ValueError): book.accept(self.context,'scope','foreign',self.fields)
        self.fields['requirements']=' '*5000+'x'
        with self.assertRaises(ValueError): book.accept(self.context,'scope','a',self.fields)

    def test_incomplete_evidence_cannot_be_accepted(self):
        from governor_workbench.intake import Intake
        self.context['intake'][0]['evidence_complete']=False
        with self.assertRaises(ValueError): Intake(self.store).accept(self.context,'scope','a',self.fields)
