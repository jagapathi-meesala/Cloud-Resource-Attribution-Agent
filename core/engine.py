import csv, json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

REQUIRED = ("record_id","resource_id","service","cost","currency","tags")
DEFAULT_TAG_KEYS = {"team":"team","project":"project","environment":"environment"}

def load_records(path):
    p=Path(path)
    if p.suffix.lower()==".json":
        data=json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data,list): raise ValueError("JSON input must be a list.")
        return data
    if p.suffix.lower()==".csv":
        rows=[]
        with p.open(newline="",encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                try: row["tags"]=json.loads(row.get("tags") or "{}")
                except json.JSONDecodeError: row["tags"]=row.get("tags")
                rows.append(row)
        return rows
    raise ValueError("Use .json or .csv input.")

def _cost(v):
    if isinstance(v,bool): raise ValueError("cost must be finite and non-negative")
    try: d=Decimal(str(v))
    except (InvalidOperation,ValueError): raise ValueError("cost must be finite and non-negative")
    if not d.is_finite() or d<0: raise ValueError("cost must be finite and non-negative")
    return d

def validate_records(records):
    issues=[]
    if not isinstance(records,list): return [{"record_index":None,"field":"$","message":"input must be a list"}]
    seen=set()
    for i,r in enumerate(records):
        if not isinstance(r,dict):
            issues.append({"record_index":i,"field":"$","message":"record must be an object"}); continue
        for f in REQUIRED:
            if f not in r: issues.append({"record_index":i,"field":f,"message":"required field missing"})
        for f in ("record_id","resource_id","service","currency"):
            if f in r and (not isinstance(r[f],str) or not r[f].strip()):
                issues.append({"record_index":i,"field":f,"message":"must be a non-empty string"})
        if isinstance(r.get("currency"),str) and r["currency"].strip() and (len(r["currency"].strip())!=3 or not r["currency"].strip().isalpha()):
            issues.append({"record_index":i,"field":"currency","message":"must be a three-letter currency code"})
        if "cost" in r:
            try: _cost(r["cost"])
            except ValueError as e: issues.append({"record_index":i,"field":"cost","message":str(e)})
        if "tags" in r and not isinstance(r["tags"],dict):
            issues.append({"record_index":i,"field":"tags","message":"must be an object/map"})
        if isinstance(r.get("tags"),dict) and any(not isinstance(k,str) or not isinstance(v,str) for k,v in r["tags"].items()):
            issues.append({"record_index":i,"field":"tags","message":"tag keys and values must be strings"})
        rid=r.get("record_id")
        if isinstance(rid,str) and rid.strip():
            if rid in seen: issues.append({"record_index":i,"field":"record_id","message":f"duplicate record_id: {rid}"})
            seen.add(rid)
    return issues

def _fmt(d): return str(d.quantize(Decimal("0.01"),rounding=ROUND_HALF_UP))

def attribute_records(records, tag_keys=None):
    keys=tag_keys or DEFAULT_TAG_KEYS
    issues=validate_records(records)
    invalid={x["record_index"] for x in issues if x["record_index"] is not None}
    by_idx={}
    for x in issues:
        if x["record_index"] is not None: by_idx.setdefault(x["record_index"],[]).append(x)
    output=[]; totals={}; unalloc={}
    for i,r in enumerate(records):
        if not isinstance(r,dict) or i in invalid:
            output.append({"record_index":i,"record_id":r.get("record_id") if isinstance(r,dict) else None,"status":"invalid","issues":by_idx.get(i,[])}); continue
        amount=_cost(r["cost"]); currency=r["currency"].strip().upper()
        dims={}; evidence={}
        for dim,key in keys.items():
            raw=r["tags"].get(key); value=raw.strip() if isinstance(raw,str) else ""
            dims[dim]=value or "unallocated"
            evidence[dim]={"tag_key":key,"tag_value":raw or None}
        totals[currency]=totals.get(currency,Decimal("0"))+amount
        if "unallocated" in dims.values(): unalloc[currency]=unalloc.get(currency,Decimal("0"))+amount
        output.append({"record_index":i,"record_id":r["record_id"],"resource_id":r["resource_id"],"service":r["service"],"cost":_fmt(amount),"currency":currency,"attribution":dims,"evidence":evidence,"status":"review_required" if "unallocated" in dims.values() else "attributed"})
    return {"status":"review_required" if issues or unalloc else "complete","record_count":len(records),"valid_record_count":sum(x.get("status") in ("attributed","review_required") for x in output),"invalid_record_count":sum(x.get("status")=="invalid" for x in output),"totals_by_currency":{c:_fmt(v) for c,v in sorted(totals.items())},"unallocated_cost_by_currency":{c:_fmt(v) for c,v in sorted(unalloc.items())},"records":output,"validation_issues":issues,"limitations":["Uses supplied records only; no provider API queried.","No currency conversion or cross-currency aggregation.","Unallocated costs and duplicate IDs require human review.","Not an official invoice or accounting entry."]}
