from reportlab.lib.units import inch
from reportlab.platypus import Paragraph

from plugins.debrief.app.utility.base_report_section import BaseReportSection
from plugins.debrief.app.debrief_svc import DebriefService

class DebriefReportSection(BaseReportSection):
    def __init__(self):
        super().__init__()
        self.id = 'tactic-technique-table'
        self.display_name = 'Tactic and Technique Table'
        self.section_title = 'TACTICS AND TECHNIQUES'
        self.description = ''

    async def generate_section_elements(self, styles, **kwargs):
        flowable_list = []
        if 'operations' in kwargs:
            operations = kwargs.get('operations', [])
            ttps = DebriefService.generate_ttps_nested(operations)
            flowable_list.append(self.group_elements([
                Paragraph(self.section_title, styles['Heading2']),
                self._generate_ttps_table(ttps)
            ]))
        return flowable_list

    def _generate_ttps_table(self, ttps):
        ttp_data = [['Tactics', 'Techniques', 'Abilities']]

        for tactic in ttps.values():
            tactic_name = tactic['name'].capitalize()
            first_row = True

            for technique_name, technique_data in tactic['techniques'].items():
                tech_title = f"{technique_data['id']}: {technique_name}"
                ability_lines = []

                for op_name, abilities in technique_data['abilities'].items():
                    ability_lines.append(f"<b>{op_name}</b>")
                    for ab in abilities:
                        ability_lines.append(f"&nbsp;&nbsp;&nbsp;{ab}")

                ttp_data.append([
                    tactic_name if first_row else '',
                    tech_title,
                    '<br/>'.join(ability_lines)
                ])
                first_row = False

        return self.generate_table(ttp_data, [1.25 * inch, 3.25 * inch, 2 * inch])

    @staticmethod
    def _get_operation_ttps(operations):
        ttps = dict()
        for op in operations:
            for link in op.chain:
                if not link.cleanup:
                    tactic_name = link.ability.tactic
                    if tactic_name not in ttps.keys():
                        tactic = dict(name=tactic_name,
                                      techniques={link.ability.technique_name: link.ability.technique_id},
                                      steps={op.name: [link.ability.name]})
                        ttps[tactic_name] = tactic
                    else:
                        if link.ability.technique_name not in ttps[tactic_name]['techniques'].keys():
                            ttps[tactic_name]['techniques'][link.ability.technique_name] = link.ability.technique_id
                        if op.name not in ttps[tactic_name]['steps'].keys():
                            ttps[tactic_name]['steps'][op.name] = [link.ability.name]
                        elif link.ability.name not in ttps[tactic_name]['steps'][op.name]:
                            ttps[tactic_name]['steps'][op.name].append(link.ability.name)
        return dict(sorted(ttps.items()))
