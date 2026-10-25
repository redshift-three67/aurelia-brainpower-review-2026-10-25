import pytest
from radiworks.core.broadcast_policy import ExecutionPolicy, PolicyError
from radiworks.core.broadcast_target import BroadcastTarget
from radiworks.core.personal_context import prepare_identity,ContextSnapshot
from radiworks.scope import ScopeContext

def target(procedure='original-aetherone-v1'):
 s=ScopeContext('synthetic','client','job');c={'name':'Synthetic','focus':'calm'};prepare_identity(c)
 return BroadcastTarget.capture(scope=s,source={'kind':'direct'},snapshot=ContextSnapshot.capture(c,s).payload(),procedure=procedure)

def config(**b):return {'booleans':b,'integers':{},'strings':{'broadcast.optionsVersion':'options-v1'}}

def test_legacy_true_does_not_activate_without_version():
 p=ExecutionPolicy.capture({'booleans':{'dynamic.adjustments':True,'broadcast.delta.time':True},'integers':{},'strings':{}},target(),1000,500)
 assert not p.dynamic_enabled and p.seconds==1000

def test_delta_rule_is_original_seconds_minus_frozen_gv():
 t=target();p=ExecutionPolicy.capture(config(**{'broadcast.delta.time':True}),t,900,500)
 assert p.seconds==400 and p.payload()['requestedSeconds']==900 and p.payload()['referenceGv']==500
 assert ExecutionPolicy.capture(config(**{'broadcast.delta.time':True}),t,400,500).seconds==400

def test_original_followup_thresholds_and_explicit_cap():
 c=config(**{'dynamic.adjustments':True});c['integers']={'broadcast.adjustment.maxFollowups':2,'broadcast.adjustment.minSeconds':10}
 p=ExecutionPolicy.capture(c,target(),600,800);assert p.followup_seconds(700)==500
 child=p.child('a'*32,500);assert child.followup_seconds(700)==450
 grand=child.child('b'*32,450);assert grand.followup_seconds(700) is None
 assert p.followup_seconds(800) is None

def test_missing_original_gv_or_personal_matrix_never_becomes_original_gv():
 c=config(**{'dynamic.adjustments':True})
 assert not ExecutionPolicy.capture(c,target(),60,None).dynamic_enabled
 assert not ExecutionPolicy.capture(c,target('radi144-personal-v1'),60,800).dynamic_enabled

@pytest.mark.parametrize('value',[True,-1,4,'2'])
def test_invalid_followup_limit_refused(value):
 c=config(**{'dynamic.adjustments':True});c['integers']['broadcast.adjustment.maxFollowups']=value
 with pytest.raises(PolicyError):ExecutionPolicy.capture(c,target(),60,800)

def test_policy_detaches_settings_and_rejects_tampering():
 c=config(**{'dynamic.adjustments':True});p=ExecutionPolicy.capture(c,target(),60,800);c['booleans']['dynamic.adjustments']=False
 assert p.dynamic_enabled
 doc=p.payload();assert ExecutionPolicy.from_payload(doc)==p
 doc['referenceGv']=999
 with pytest.raises(PolicyError):ExecutionPolicy.from_payload(doc)
