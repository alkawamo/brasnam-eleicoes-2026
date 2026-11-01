import json
import re

with open(r'C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026\data\master_exercito_do_lula.json', encoding='utf-8') as f:
    lula_msgs = json.load(f)['messages']

with open(r'C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026\data\master_tropa_do_flavio.json', encoding='utf-8') as f:
    flavio_msgs = json.load(f)['messages']

print('=== 25/10 EXÉRCITO DO LULA ===')
for m in lula_msgs:
    pre = m.get('pre_plain_text', '')
    if '25/10/2026' in pre:
        print(f"[{pre.strip()}]")
        print(m.get('text', ''))
        print(f"Reactions: {m.get('reactions')}")
        print('-'*50)

print('\n=== 25/10 TROPA DO FLÁVIO ===')
for m in flavio_msgs:
    pre = m.get('pre_plain_text', '')
    if '25/10/2026' in pre:
        print(f"[{pre.strip()}]")
        print(m.get('text', ''))
        print(f"Reactions: {m.get('reactions')}")
        print('-'*50)
