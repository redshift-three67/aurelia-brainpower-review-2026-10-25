import sqlite3
import unittest
from tests import test_intake


class DraftTests(unittest.TestCase):
    def setUp(self):
        test_intake.IntakeTests.setUp(self)
        from governor_workbench.intake_drafts import IntakeDrafts
        self.book = IntakeDrafts(self.store)
        self.context.update(review_scope={'kind':'group','id':'team'}, governance_sources=[])
        self.context['projects'][0]['memories'] = [{'name':'strategy.md','sha256':'a'*64}]
        self.sources = [{'name':'strategy.md','sha256':'a'*64}]

    def save(self):
        return self.book.save(self.context,'scope','a',self.fields,self.sources)

    def test_draft_does_not_accept_intake_and_tracks_drift(self):
        from governor_workbench.intake import Intake
        draft = self.save()
        self.assertFalse(Intake(self.store).accepted('a','source'))
        self.assertTrue(self.book.list(self.context)[0]['current'])
        self.context['scope_hash'] = 'changed'
        self.assertFalse(self.book.list(self.context)[0]['current'])
        self.assertEqual(draft['id'],self.book.list(self.context)[0]['id'])

    def test_bad_source_hash_foreign_project_and_stale_save_rejected(self):
        for sources in ([], [{'name':'foreign.md','sha256':'a'*64}], [{'name':'strategy.md','sha256':'b'*64}]):
            with self.assertRaises(ValueError): self.book.save(self.context,'scope','a',self.fields,sources)
        with self.assertRaises(ValueError): self.book.save(self.context,'old','a',self.fields,self.sources)
        with self.assertRaises(ValueError): self.book.save(self.context,'scope','other',self.fields,self.sources)
        self.assertEqual([], self.book.list(self.context))

    def test_scope_isolation_and_immutable_history(self):
        draft = self.save()
        self.context['review_scope']['id'] = 'other'
        self.assertEqual([],self.book.list(self.context))
        for operation in ('DELETE FROM intake_drafts','UPDATE intake_drafts SET body=body'):
            with self.assertRaises(sqlite3.IntegrityError):
                with self.store.db() as c: c.execute(operation)
