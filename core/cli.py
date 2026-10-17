import argparse,json,sys
from pathlib import Path
from .engine import load_records,validate_records,attribute_records
def main(argv=None):
    p=argparse.ArgumentParser(description="Local cloud cost attribution")
    s=p.add_subparsers(dest="command",required=True)
    v=s.add_parser("validate"); v.add_argument("input")
    a=s.add_parser("attribute"); a.add_argument("input"); a.add_argument("--output",default="attribution-report.json")
    args=p.parse_args(argv)
    try:
        records=load_records(args.input)
        if args.command=="validate":
            issues=validate_records(records); print(json.dumps({"valid":not issues,"record_count":len(records),"issues":issues},indent=2)); return 0 if not issues else 2
        report=attribute_records(records); Path(args.output).write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
        print(json.dumps({"status":report["status"],"record_count":report["record_count"],"invalid_record_count":report["invalid_record_count"],"totals_by_currency":report["totals_by_currency"],"output":args.output},indent=2))
        return 0 if report["invalid_record_count"]==0 else 2
    except (OSError,ValueError,json.JSONDecodeError) as e:
        print(f"error: {e}",file=sys.stderr); return 2
if __name__=="__main__": raise SystemExit(main())
