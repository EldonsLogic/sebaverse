"""AUTH-007 exact exception boundaries; synthetic byte fixtures, no image/DB use."""
import copy
from datetime import datetime,timedelta,timezone
import hashlib,importlib.util,json,os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('openssl_checker',ROOT/'tools/security/check_reports.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class OpenSSLBoundary(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.now=datetime.now(timezone.utc)
        self.runtime={'type':'derived-oci','parent_platform_manifest':m.OPENSSL_PARENT}
        self.policy=json.loads((ROOT/'infra/synthetic-openssl-review.json').read_text())
        self.policy.update(review_status='reviewed',reviewed_at_utc=(self.now-timedelta(minutes=1)).isoformat(),expires_at_utc=(self.now+timedelta(days=1)).isoformat())
        for name in self.policy['source_inputs']:
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'synthetic reviewed bytes')
        self.refresh()
        env=patch.dict(os.environ,{'GITHUB_ACTIONS':'true'},clear=True);env.start();self.addCleanup(env.stop)

    def refresh(self):
        self.policy['source_inputs']={name:hashlib.sha256(p.read_bytes()).hexdigest() for name,p in m.openssl_exception_inputs(self.root).items()}

    def bind(self,path,expected):
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('Source changed')

    def check(self,scope='synthetic-ci'):
        return m.validate_openssl_exception(self.policy,self.runtime,self.root,self.bind,self.now,scope)

    def test_exact_review_only_permits_eight_high_image_pairs(self):
        self.assertEqual(len(self.check()),8)

    def test_standard_and_production_scope_are_refused(self):
        for scope in ['standard','production']:
            with self.subTest(scope=scope),self.assertRaises(ValueError):self.check(scope)
        os.environ['SEBAVERSE_ENV']='production'
        with self.assertRaises(ValueError):self.check()

    def test_non_ci_is_refused(self):
        os.environ.pop('GITHUB_ACTIONS')
        with self.assertRaises(ValueError):self.check()

    def test_pending_or_wrong_authority_is_refused(self):
        for key,value in [('authority','AUTH-005'),('review_status','pending')]:
            p=copy.deepcopy(self.policy);self.policy[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.check()
            self.policy=p

    def test_expired_future_and_overlong_reviews_are_refused(self):
        for key,value in [('expires_at_utc',self.now),('reviewed_at_utc',self.now+timedelta(seconds=1)),('expires_at_utc',self.now+timedelta(days=4))]:
            p=copy.deepcopy(self.policy);self.policy[key]=value.isoformat()
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):self.check()
            self.policy=p

    def test_changed_parent_or_non_derived_runtime_is_refused(self):
        for key,value in [('parent_platform_manifest','sha256:'+'1'*64),('type','production')]:
            r=copy.deepcopy(self.runtime);self.runtime[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.check()
            self.runtime=r

    def test_changed_recipe_tls_gss_or_workload_bytes_invalidates(self):
        for name in ['infra/local/postgres/Dockerfile','backend/config/environment.py','tools/run_postgres_smoke.py','.github/workflows/skeleton.yml']:
            p=self.root/name;original=p.read_bytes();p.write_bytes(original+b' changed')
            with self.subTest(name=name),self.assertRaises(ValueError):self.check()
            p.write_bytes(original)

    def test_added_backend_file_invalidates_workload_set(self):
        (self.root/'backend/unreviewed.py').write_text('new workload')
        with self.assertRaises(ValueError):self.check()

    def test_changed_id_version_severity_package_or_report_is_refused(self):
        for key,value in [('id','CVE-2026-OTHER'),('version','3.5.10-r0'),('severity','critical'),('package','openssl'),('report','system-native-cves.json')]:
            p=copy.deepcopy(self.policy);self.policy['findings'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.check()
            self.policy=p

    def test_only_exact_high_is_excepted_critical_unknown_and_unrelated_high_still_block(self):
        allowed=self.check();item=next(iter(allowed))
        block,kev,scoped=m.finding_flags(*item,{item[1]},set(),allowed)
        self.assertFalse(block);self.assertFalse(kev);self.assertTrue(scoped)
        for severity in ['critical','unknown']:
            block,_,_=m.finding_flags(*item[:4],severity,{item[1]},set(),allowed)
            self.assertTrue(block)
        item=('image-cves.json','CVE-2026-OTHER','libssl3','3.5.9-r0','high')
        self.assertTrue(m.finding_flags(*item,{item[1]},set(),allowed)[0])

    def test_kev_including_related_alias_still_blocks_exact_exception(self):
        allowed=self.check();item=next(iter(allowed))
        for ids,kev_ids in [({item[1]},{item[1]}),({item[1],'CVE-RELATED'},{'CVE-RELATED'})]:
            block,kev,_=m.finding_flags(*item,ids,kev_ids,allowed)
            self.assertTrue(block or kev)
