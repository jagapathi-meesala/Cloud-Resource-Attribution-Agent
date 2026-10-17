from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
REQUIRED=["agent.yaml","SOUL.md","README.md","AGENTS.md","DUTIES.md","RULES.md","EXPLAINABILITY.md","LICENSE","requirements.txt","core/engine.py","core/cli.py","tools/validate-cost-data.yaml","tools/attribute-cloud-costs.yaml","tools/generate-attribution-report.yaml","skills/cloud-cost-attribution/SKILL.md","skills/tag-quality-review/SKILL.md","skills/cost-reporting/SKILL.md","tests/test_engine.py","examples/cost_records.json"]
def main():
 missing=[x for x in REQUIRED if not (ROOT/x).is_file()]
 manifest=(ROOT/"agent.yaml").read_text()
 name_ok=bool(re.search(r"(?m)^name:\s*cloud-resource-attribution-agent\s*$",manifest))
 exp=(ROOT/"EXPLAINABILITY.md").read_text()
 headings=["## Purpose","## Inputs","## Decision","## Severity and Prioritization","## Outputs and Evidence","## Tool: validate-cost-data","## Tool: attribute-cloud-costs","## Tool: generate-attribution-report","## Human Review and Safety","## Auditability","## Global Limits"]
 exp_ok=all(h in exp.splitlines() for h in headings)
 print(f"Required files: {len(REQUIRED)-len(missing)}/{len(REQUIRED)}")
 print("Agent name valid: "+("PASS" if name_ok else "FAIL"))
 print("Explainability sections: "+("PASS" if exp_ok else "FAIL"))
 if missing: print("Missing files:",", ".join(missing))
 if not exp_ok: print("Missing headings:",", ".join(h for h in headings if h not in exp.splitlines()))
 return 1 if missing or not name_ok or not exp_ok else 0
if __name__=="__main__": raise SystemExit(main())
