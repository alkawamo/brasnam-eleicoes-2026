import json

with open(r'C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026\data\master_tropa_do_flavio.json', encoding='utf-8') as f:
    flavio = json.load(f)['messages']

print('--- LAST 6 MESSAGES IN TROPA DO FLAVIO ---')
for i, m in enumerate(flavio[-6:]):
    print(f"[{i}] ID: {m.get('id')}")
    print(f"  pre: {m.get('pre_plain_text')}")
    print(f"  text: {repr(m.get('text', ''))}")
    print(f"  urls: {m.get('urls')}")
    print(f"  media: {m.get('media')}")
    print(f"  reactions: {m.get('reactions')}")
    print('-'*50)

with open(r'C:\Users\alkaw\.gemini\antigravity\scratch\brasnam-eleicoes-2026\data\master_exercito_do_lula.json', encoding='utf-8') as f:
    lula = json.load(f)['messages']

print('\n--- LAST 10 MESSAGES IN EXERCITO DO LULA (SORTED BY DATE/TIME) ---')
# Let's see messages from 25/10 and 26/10
lula_recent = []
for m in lula:
    pre = m.get('pre_plain_text', '')
    if '25/10/2026' in pre or '26/10/2026' in pre:
        lula_recent.append(m)

print(f'Total messages on 25/10 and 26/10 in Lula: {len(lula_recent)}')
for m in lula_recent[-10:]:
    print(f"[{m.get('pre_plain_text', '').strip()}]")
    print(m.get('text', '')[:160])
    print(f"Reactions: {m.get('reactions')}")
    print('-'*50)
