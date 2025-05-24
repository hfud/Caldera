import os
import yaml
import uuid
from collections import defaultdict

CALDERA_ROOT = '.'
OUTPUT_DIR = os.path.join(CALDERA_ROOT, 'data', 'adversaries')
DEFAULT_OBJECTIVE = '495a9828-cab1-44dd-a0ca-66e58177d8cc'

print(f'[📁] Adversaries will be saved to: {OUTPUT_DIR}\n')

# Tactic → List of (technique_name, ability_id)
tactic_to_abilities = defaultdict(list)

# Browse all plugins
plugin_dir = os.path.join(CALDERA_ROOT, 'plugins')
for plugin in os.listdir(plugin_dir):
    ability_dir = os.path.join(plugin_dir, plugin, 'data', 'abilities')
    if not os.path.exists(ability_dir):
        continue

    for root, _, files in os.walk(ability_dir):
        for file in files:
            if file.endswith('.yml') or file.endswith('.yaml'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        abilities = yaml.safe_load(f)
                        if not isinstance(abilities, list):
                            abilities = [abilities]
                        for ab in abilities:
                            tactic = ab.get('tactic')
                            ability_id = ab.get('id')
                            tech_name = ab.get('technique_name') or ab.get('technique', {}).get('name') or 'zzz_unknown'

                            if tactic and ability_id:
                                tactic_to_abilities[tactic].append((tech_name.lower(), ability_id))
                    except Exception as e:
                        print(f'[!] Error reading {file}: {e}')

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Adversary for each tactic
for tactic, tech_ability_pairs in tactic_to_abilities.items():
    # Ability order
    sorted_pairs = sorted(tech_ability_pairs, key=lambda x: x[0])
    sorted_ability_ids = [ability_id for _, ability_id in sorted_pairs]

    adversary = {
        'name': tactic.capitalize(),
        'description': f'Auto-generated adversary for tactic: {tactic}',
        'atomic_ordering': sorted_ability_ids,
        'adversary_id': str(uuid.uuid4()),
        'objective': DEFAULT_OBJECTIVE
    }

    file_name = f'{tactic.lower().replace(" ", "_")}.yml'
    file_path = os.path.join(OUTPUT_DIR, file_name)

    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(adversary, f, sort_keys=False)

    print(f'[+] Created adversary: {file_name} ({len(sorted_ability_ids)} abilities)')