from app.normalizer import normalize_events
from app.simulator import generate_scenario
from app.agents import run_agents
from app.guardrails import classify_action

def test_multi_agent_analysis():
    result=run_agents(normalize_events(generate_scenario('payment-db-timeout')))
    assert result['confidence']>=80
    assert len(result['agent_trace'])>=7
    assert result['rag_context']

def test_default_deny_guardrail():
    assert classify_action('unknown-command')['status']=='BLOCKED'
    assert classify_action('rollback_deployment')['risk']=='APPROVAL'
