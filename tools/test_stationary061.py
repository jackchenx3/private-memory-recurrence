"""Interface tests only. Never call a production transition row or256-state solve."""
import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('portable061',ROOT/'tools/stationary061.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

class PortableTests(unittest.TestCase):
    def test_authentication_and_imports_are_read_only_and_restore_aliases(self):
        before={str(f.relative_to(ROOT)):p.digest(f) for f in (ROOT/'code/061').rglob('*') if f.is_file()}
        sentinel=types.ModuleType('numerics')
        with mock.patch.dict(sys.modules,{'numerics':sentinel}):
            with p.operators(ROOT) as (kernel,numerics,outcomes):
                self.assertNotEqual(numerics,sentinel)
                self.assertIs(sys.modules['numerics'],numerics)
                with mock.patch.object(kernel,'row',side_effect=AssertionError('Production row forbidden')):
                    self.assertEqual(p.smoke(kernel,numerics,outcomes)['status'],'PASS')
            self.assertIs(sys.modules['numerics'],sentinel)
        after={str(f.relative_to(ROOT)):p.digest(f) for f in (ROOT/'code/061').rglob('*') if f.is_file()}
        self.assertEqual(before,after)
        self.assertEqual(len(p.authenticate(ROOT)['files']),15)

    def test_new_output_and_overwrite_refusal(self):
        with tempfile.TemporaryDirectory() as t:
            dest=Path(t)/'new';p.reserve_output(dest,ROOT)
            with self.assertRaises(FileExistsError):p.reserve_output(dest,ROOT)
            (dest/'keep.txt').write_text('keep')
            with self.assertRaises(FileExistsError):p.reserve_output(dest,ROOT)
            self.assertEqual((dest/'keep.txt').read_text(),'keep')

    def test_protected_and_symlinked_source_paths(self):
        with self.assertRaises(ValueError):p.reserve_output(ROOT/'code/061/new-run',ROOT)
        with self.assertRaises(ValueError):p.reserve_output(ROOT,ROOT)
        with self.assertRaises(ValueError):p.reserve_output(ROOT.parent,ROOT)
        with tempfile.TemporaryDirectory() as t:
            link=Path(t)/'link'
            try:link.symlink_to(ROOT/'results',target_is_directory=True)
            except OSError:self.skipTest('Symlink permission unavailable')
            with self.assertRaises(ValueError):p.reserve_output(link/'new-run',ROOT)

    def test_store_no_overwrite_traversal_or_oversize_write(self):
        with tempfile.TemporaryDirectory() as t:
            store=p.Store(t);store.save('x.json',{'kept':True})
            with self.assertRaises(FileExistsError):store.save('x.json',{})
            with self.assertRaises(ValueError):store.save('../escape.json',{})
            with mock.patch.object(p,'OUTPUT_LIMIT_BYTES',16390):
                with self.assertRaises(ValueError):store.save('oversize.json',{'large':'x'*50})
            self.assertFalse((Path(t)/'oversize.json').exists())
            self.assertEqual(json.loads((Path(t)/'x.json').read_text()),{'kept':True})

    def test_changed_scientific_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'tools').mkdir();(root/'code/061').mkdir(parents=True)
            (root/'code/061/kernel.py').write_text('modified')
            (root/'tools/stationary061_sources.json').write_text(json.dumps({'baseline_commit':'651c4289b1ac34efb30d1a81560e88cd74b1609f','files':{'code/061/kernel.py':'0'*64}}))
            with self.assertRaisesRegex(ValueError,'Published source changed'):p.authenticate(root)

    def test_two_state_orchestration_and_retained_numerical_failure(self):
        # Injection affects this test only; public regeneration has no state-count option.
        A=[[3,1],[2,2]]
        rows=[]
        def row(state,name):rows.append((state,name));return A[state]
        fake=types.SimpleNamespace(D=4,row=row,check_matrix=lambda matrix,name:{'fixture':matrix==A})
        with p.operators(ROOT) as (_,num,__):
            with tempfile.TemporaryDirectory() as t:
                v,check=p.generate_one('ACTIVE_ZERO',fake,num,p.Store(t),states=range(2))
                self.assertEqual(v['status'],'COMPUTED');self.assertTrue(check['fixture'])
                self.assertEqual(rows,[(0,'ACTIVE_ZERO'),(1,'ACTIVE_ZERO')])
                self.assertTrue((Path(t)/'receipts/ACTIVE_ZERO-solve-intent.json').exists())
            with tempfile.TemporaryDirectory() as t, mock.patch.object(num,'solve',side_effect=ValueError('constructed failure')):
                v,_=p.generate_one('ACTIVE_ZERO',fake,num,p.Store(t),states=range(2))
                self.assertEqual(v['status'],'REJECTED');self.assertIn('constructed failure',v['reason'])
                saved=json.loads(gzip.decompress((Path(t)/'vectors/ACTIVE_ZERO.json.gz').read_bytes()))
                self.assertEqual(saved,v)

    def test_default_cli_runs_only_tiny_fixtures(self):
        with tempfile.TemporaryDirectory() as t:
            dest=Path(t)/'smoke'
            r=subprocess.run([sys.executable,'-B',str(ROOT/'tools/stationary061.py'),'--output',str(dest)],capture_output=True,text=True,timeout=30)
            self.assertEqual(r.returncode,0,r.stderr)
            status=json.loads((dest/'STATUS.json').read_text());result=json.loads((dest/'RESULT.json').read_text())
            self.assertEqual(status['mode'],'smoke');self.assertFalse(status['full_regeneration_requested'])
            self.assertEqual(result['production_rows'],0);self.assertEqual(result['production_stationary_solves'],0)
            r=subprocess.run([sys.executable,'-B',str(ROOT/'tools/stationary061.py'),'--output',str(dest)],capture_output=True,text=True,timeout=30)
            self.assertNotEqual(r.returncode,0)

    def test_timeout_terminates_worker_and_retains_request(self):
        child=mock.Mock()
        child.is_alive.side_effect=[True,False]
        child.exitcode=-15
        context=mock.Mock();context.Process.return_value=child
        with tempfile.TemporaryDirectory() as t, mock.patch.object(p.multiprocessing,'get_context',return_value=context):
            dest=Path(t)/'timed-out'
            self.assertEqual(p.main(['--output',str(dest)]),1)
            child.terminate.assert_called_once()
            self.assertEqual(json.loads((dest/'STATUS.json').read_text())['status'],'TIME_LIMIT')
            self.assertTrue((dest/'REQUEST.json').exists())
            self.assertFalse((dest/'RESULT.json').exists())

    def test_worker_failure_is_recorded_without_retry(self):
        with tempfile.TemporaryDirectory() as t, mock.patch.object(p,'smoke',side_effect=RuntimeError('constructed interface failure')) as fail:
            with self.assertRaises(RuntimeError):p.worker('smoke',str(ROOT),t)
            self.assertEqual(fail.call_count,1)
            receipt=json.loads((Path(t)/'FAILURE.json').read_text())
            self.assertEqual(receipt['error'],'constructed interface failure')
            self.assertFalse(receipt['automatic_retry'])

    def test_optimized_python_refused(self):
        with tempfile.TemporaryDirectory() as t:
            dest=Path(t)/'run'
            r=subprocess.run([sys.executable,'-O','-B',str(ROOT/'tools/stationary061.py'),'--output',str(dest)],capture_output=True,text=True,timeout=30)
            self.assertNotEqual(r.returncode,0);self.assertFalse(dest.exists());self.assertIn('Do not use -O',r.stderr)

if __name__=='__main__':unittest.main(verbosity=2)
