import os
import yaml
import uuid

ADVERSARY_DIR = './data/adversaries'
OUTPUT_FILE = os.path.join(ADVERSARY_DIR, 'mitre.yml')
DEFAULT_OBJECTIVE = '495a9828-cab1-44dd-a0ca-66e58177d8cc'

MITRE_TACTIC_ORDER = [
    'reconnaissance',
    'resource development',
    'initial access',
    'execution',
    'persistence',
    'privilege escalation',
    'defense evasion',
    'credential access',
    'discovery',
    'lateral movement',
    'collection',
    'command and control',
    'exfiltration',
    'impact'
]

tactic_to_abilities = {}

# Load all existing tactic-based adversaries
for filename in os.listdir(ADVERSARY_DIR):
    if not filename.endswith('.yml'):
        continue
    filepath = os.path.join(ADVERSARY_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            adv = yaml.safe_load(f)
            name = adv.get('name', '').lower().replace('-', ' ')
            abilities = adv.get('atomic_ordering', []) or adv.get('atomic_order', [])
            if name and abilities:
                tactic_to_abilities[name] = abilities
        except Exception as e:
            print(f'[!] Error reading {filename}: {e}')

full_chain = []
for tactic in MITRE_TACTIC_ORDER:
    abilities = tactic_to_abilities.get(tactic, [])
    full_chain.extend(abilities)

adversary = {
    'name': 'MITRE ATT&CK',
    'description': 'A combined adversary containing all tactics in MITRE ATT&CK order',
    'atomic_ordering': full_chain,
    'adversary_id': str(uuid.uuid4()),
    'objective': DEFAULT_OBJECTIVE
}

# Write to file
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    yaml.dump(adversary, f, sort_keys=False)

print(f'[+] Created MITRE full-chain adversary with {len(full_chain)} abilities:')
print(f'    -> {OUTPUT_FILE}')
