import importlib.util
from pathlib import Path
from tests import test_maintenance21


class MaintenanceV2Tests(test_maintenance21.MaintenanceTests):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[1] / 'artifacts/server-maintenance21-v2.py'
        spec = importlib.util.spec_from_file_location('maint_v2', path)
        cls.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.m)
