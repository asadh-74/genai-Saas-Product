import json
import pytest
from fastapi.testclient import TestClient
import main
@pytest.fixture
def client(monkeypatch):
 monkeypatch.delenv('GEMINI_API_KEY',raising=False)
 monkeypatch.delenv('AI_ACCESS_TOKEN',raising=False)
 main._ai_calls.clear()
 return TestClient(main.app)
def test_health_and_security_headers(client):
 r=client.get('/');assert r.status_code==200;assert 'frame-ancestors' in r.headers['content-security-policy']
 assert client.get('/health').json()['ai_available'] is False
 assert client.get('/static/app.js').status_code==200
def test_ai_unconfigured_preserves_template(client):
 assert client.post('/api/refine',json=payload()).status_code==503
 assert client.post(ENDPOINT,json=payload()).status_code==200
def test_ai_requires_owner_token(client,monkeypatch):
 monkeypatch.setenv('GEMINI_API_KEY','test-key');monkeypatch.setenv('AI_ACCESS_TOKEN','a'*24)
 assert client.post('/api/refine',json=payload()).status_code==401
 assert client.post('/api/refine',json=payload(),headers={'X-AI-Token':'wrong'}).status_code==401
def test_ai_validated_and_budgeted(client,monkeypatch):
 monkeypatch.setenv('GEMINI_API_KEY','test-key');monkeypatch.setenv('AI_ACCESS_TOKEN','a'*24)
 class Fake:
  def __enter__(self):return self
  def __exit__(self,*a):pass
  def read(self,*a):return json.dumps({'candidates':[{'content':{'parts':[{'text':json.dumps({'summary':'A summary grounded in supplied inputs.'})}]}}]}).encode()
 monkeypatch.setattr(main,'urlopen',lambda *a,**k:Fake())
 r=client.post('/api/refine',json=payload(),headers={'X-AI-Token':'a'*24});assert r.status_code==200;assert r.json()['summary']
 main._ai_calls[:]=[main.time.time()]*10
 assert client.post('/api/refine',json=payload(),headers={'X-AI-Token':'a'*24}).status_code==429
def test_ai_failure_does_not_expose_exception(client,monkeypatch):
 monkeypatch.setenv('GEMINI_API_KEY','private-test-secret');monkeypatch.setenv('AI_ACCESS_TOKEN','a'*24)
 def fail(*a,**k):raise RuntimeError('private-test-secret')
 monkeypatch.setattr(main,'urlopen',fail)
 r=client.post('/api/refine',json=payload(),headers={'X-AI-Token':'a'*24});assert r.status_code==502;assert 'private-test-secret' not in r.text
ENDPOINT='/api/proposal'
def payload():return {'client':'Example Studio','title':'Workflow automation','objective':'Capture enquiries and prevent duplicate customer records.','rate':'19.99','currency':'USD','items':[{'name':'Discovery','hours':'1.25'},{'name':'Implementation','hours':'2.50'}]}
def test_money_rounding_and_milestones(client):
 d=client.post(ENDPOINT,json=payload()).json();assert d['items'][0]['amount']=='24.99';assert d['items'][1]['amount']=='49.98';assert d['total']=='74.97';assert len(d['milestones'])==3;assert d['status']=='draft'
@pytest.mark.parametrize('rate',['0','-1','NaN','Infinity','0.001','10001'])
def test_invalid_rates(client,rate):
 p=payload();p['rate']=rate;assert client.post(ENDPOINT,json=p).status_code==422
def test_invalid_items_currency_and_blank(client):
 p=payload();p['items']=[];assert client.post(ENDPOINT,json=p).status_code==422
 p=payload();p['currency']='XXX';assert client.post(ENDPOINT,json=p).status_code==422
 p=payload();p['client']=' '*10;assert client.post(ENDPOINT,json=p).status_code==422

@pytest.mark.parametrize('field,value',[('client',' x '),('title',' x    '),('objective',' x                    ')])
def test_padded_short_text_rejected(client,field,value):
 p=payload();p[field]=value
 assert client.post(ENDPOINT,json=p).status_code==422

def test_padded_short_item_rejected(client):
 p=payload();p['items'][0]['name']=' x '
 assert client.post(ENDPOINT,json=p).status_code==422

def test_nontext_name_rejected(client):
 p=payload();p['items'][0]['name']=123
 assert client.post(ENDPOINT,json=p).status_code==422
