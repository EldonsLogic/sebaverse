"""Planning-only arithmetic. No vendor calls or student data."""
from pathlib import Path
import json, copy
ROOT=Path(__file__).resolve().parents[1]
p=json.loads((ROOT/'economics/inputs.json').read_text())
def costs(p):
    assert 0 <= p['cache_fraction'] <= 1 and 0 <= p['voice_student_share'] <= 1
    turns=p['sessions']*p['turns']
    rate=(1-p['cache_fraction'])*p['input_usd_per_million']+p['cache_fraction']*p['cached_input_usd_per_million']
    base=turns*(p['input_tokens_per_turn']*rate+p['output_tokens_per_turn']*p['output_usd_per_million'])/1e6
    reserve=p['auxiliary_multiplier']; other=p['other_ai_usd_per_learner'];mins=p['voice_connected_minutes']; share=p['voice_student_share']
    text=(base+other)*reserve
    cascade=text+reserve*mins*(share*p['stt_usd_per_minute']+(1-share)*p['tts_usd_per_minute'])
    live=text+reserve*mins*p['realtime_usd_per_connected_minute']
    return dict(text=text,cascade=cascade,realtime=live)
base=costs(p)
required=['fx_egp_per_usd','paid_learners','payment_percent','payment_fixed_egp','price_inclusive_tax_rate','refund_fraction','human_support_usd_per_learner','educator_usd_per_learner','rights_usd_per_learner','messaging_usd_per_learner','other_fixed_usd']
missing=[k for k in required if p[k] is None]
scenarios=[]
for n,fixed in zip(p['active_learners'],p['fixed_infrastructure_usd']):
    s={'active_learners':n,'assumed_fixed_usd':fixed,'partial_monthly_cost_usd':{k:round(n*v+fixed,4) for k,v in base.items()},'missing_full_margin_inputs':missing,'full_margin_egp':None}
    if not missing:
        paid=p['paid_learners'];fx=p['fx_egp_per_usd'];price=p['monthly_price_egp_hypothesis'];tax=p['price_inclusive_tax_rate'];refund=p['refund_fraction']
        assert fx>0 and tax>=0 and 0<=refund<=1 and paid>=0
        revenue=paid*price*(1-refund)/(1+tax)-paid*(price*p['payment_percent']+p['payment_fixed_egp'])
        nonai=sum(p[k] for k in ['human_support_usd_per_learner','educator_usd_per_learner','rights_usd_per_learner','messaging_usd_per_learner'])
        s['full_margin_egp']={k:round(revenue-(n*(v+nonai)+fixed+p['other_fixed_usd'])*fx,2) for k,v in base.items()}
    if p['successful_independent_activities_per_learner']:
        s['partial_cost_usd_per_independent_activity']={k:round((n*v+fixed)/(n*p['successful_independent_activities_per_learner']),6) for k,v in base.items()}
    scenarios.append(s)
variants=[('baseline',{}),('sessions doubled',{'sessions':p['sessions']*2,'voice_connected_minutes':p['voice_connected_minutes']*2}),('large context',{'input_tokens_per_turn':8000,'output_tokens_per_turn':1000}),('half input cached',{'cache_fraction':.5}),('voice 100 minutes',{'voice_connected_minutes':100}),('voice 800 minutes',{'voice_connected_minutes':800}),('speech rates doubled',{'stt_usd_per_minute':p['stt_usd_per_minute']*2,'tts_usd_per_minute':p['tts_usd_per_minute']*2}),('text model rates doubled',{'input_usd_per_million':p['input_usd_per_million']*2,'cached_input_usd_per_million':p['cached_input_usd_per_million']*2,'output_usd_per_million':p['output_usd_per_million']*2})]
sens=[]
for name,overrides in variants:
    q=copy.deepcopy(p);q.update(overrides);sens.append({'scenario':name,**costs(q)})
gkeys=['gpu_monthly_usd','gpu_ops_monthly_usd','gpu_noncompute_monthly_usd','gpu_variable_usd_per_activity','hosted_usd_per_activity']
break_even=None
if all(p[k] is not None for k in gkeys):
    delta=p['hosted_usd_per_activity']-p['gpu_variable_usd_per_activity']
    if delta>0:break_even=sum(p[k] for k in gkeys[:3])/delta
result={'warning':'Illustrative partial costs; no measured prices or quality; no full margin with missing inputs','per_active_learner_ai_usd':base,'scales':scenarios,'sensitivities':sens,'gpu_break_even_activities':break_even}
(ROOT/'economics/scenarios.json').write_text(json.dumps(result,indent=2)+'\n')
md='# Sensitivity results\n\nGenerated from editable assumptions; USD/month per active learner, AI only. Not verified current tariffs or full costs.\n\n| Scenario | Text | Cascade | Realtime |\n|---|---:|---:|---:|\n'
for s in sens:md+=f"| {s['scenario']} | {s['text']:.4f} | {s['cascade']:.4f} | {s['realtime']:.4f} |\n"
md+='\n## Partial operating cost by scale\n\n| Active | Text | Cascade | Realtime |\n|---:|---:|---:|---:|\n'
for s in scenarios:
    a=s['partial_monthly_cost_usd'];md+=f"| {s['active_learners']} | {a['text']:.2f} | {a['cascade']:.2f} | {a['realtime']:.2f} |\n"
md+='\nFull EGP margin withheld while unknown: '+', '.join(missing)+'.\n'
(ROOT/'economics/sensitivity.md').write_text(md)
print('Recomputed planning scenarios; unknown full-cost inputs remain explicit.')
