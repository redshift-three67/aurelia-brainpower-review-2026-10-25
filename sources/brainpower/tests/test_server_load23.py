import importlib.util
from pathlib import Path
import unittest

class LoadGuardTests(unittest.TestCase):
    def test_guard(self):
        path=Path(__file__).resolve().parents[1]/'artifacts/server-load23.py'
        self.assertTrue(path.exists(), 'load guard not implemented')
        spec=importlib.util.spec_from_file_location('load23',path)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        good={'healthy':True,'time_utc':'2026-09-23T21:00:00+00:00'}
        now=1758661200
        now=m.datetime.datetime.fromisoformat(good['time_utc']).timestamp()
        m.guard(good,now,{'k10temp':40,'nvme0':35},8192)
        for h,t,temps,mem in [(good,now+481,{'k10temp':40},8192),
                (dict(good,healthy=False),now,{'k10temp':40},8192),
                (good,now,{'k10temp':85},8192),(good,now,{'k10temp':40,'nvme0':65},8192),
                (good,now,{'nvme0':30},8192),(good,now,{'k10temp':40},1024)]:
            with self.assertRaises(ValueError):m.guard(h,t,temps,mem)

if __name__=='__main__':unittest.main()
