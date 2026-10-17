import unittest
from core.engine import validate_records,attribute_records
def row(**kw):
 d={"record_id":"r1","resource_id":"vm1","service":"compute","cost":"10.25","currency":"USD","tags":{"team":"platform","project":"portal","environment":"prod"}}; d.update(kw); return d
class Tests(unittest.TestCase):
 def test_valid(self): self.assertEqual(validate_records([row()]),[])
 def test_tag_attribution(self): self.assertEqual(attribute_records([row()])["records"][0]["attribution"]["team"],"platform")
 def test_missing_tag_unallocated(self): self.assertEqual(attribute_records([row(tags={"project":"portal"})])["unallocated_cost_by_currency"]["USD"],"10.25")
 def test_currency_totals_separate(self): self.assertEqual(attribute_records([row(),row(record_id="r2",currency="EUR")])["totals_by_currency"],{"EUR":"10.25","USD":"10.25"})
 def test_negative_invalid(self): self.assertEqual(attribute_records([row(cost="-1")])["invalid_record_count"],1)
 def test_missing_field(self):
  r=row(); del r["service"]; self.assertTrue(any(x["field"]=="service" for x in validate_records([r])))
 def test_duplicate_id(self): self.assertTrue(any("duplicate record_id" in x["message"] for x in attribute_records([row(),row(resource_id="vm2")])["validation_issues"]))
 def test_bad_tags(self): self.assertTrue(any(x["field"]=="tags" for x in validate_records([row(tags="bad")])))
 def test_bad_currency(self): self.assertTrue(any(x["field"]=="currency" for x in validate_records([row(currency="US")])))
 def test_no_currency_conversion(self): self.assertEqual(set(attribute_records([row(),row(record_id="r2",currency="EUR")])["totals_by_currency"]),{"USD","EUR"})
if __name__=="__main__": unittest.main()
