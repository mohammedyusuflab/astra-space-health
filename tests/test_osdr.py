from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from astra.osdr import (
    DEFAULT_CSV,
    OSDRDataError,
    build_osd569_dataset,
    write_osd569_json,
)


class OSDRDatasetTests(unittest.TestCase):
    def test_bundled_nasa_dataset_has_expected_shape_and_provenance(self):
        dataset = build_osd569_dataset(DEFAULT_CSV)
        summary = dataset["summary"]
        self.assertEqual(summary["record_count"], 553)
        self.assertEqual(summary["sample_count"], 28)
        self.assertEqual(summary["subject_count"], 4)
        self.assertEqual(summary["analyte_count"], 20)
        self.assertEqual(summary["subjects"], ["C001", "C002", "C003", "C004"])
        self.assertEqual(len(summary["timepoints"]), 7)
        self.assertEqual(dataset["dataset"]["id"], "OSD-569")
        self.assertEqual(
            dataset["dataset"]["provider"],
            "NASA Open Science Data Repository (OSDR)",
        )

    def test_samples_are_preflight_or_postflight_only(self):
        dataset = build_osd569_dataset(DEFAULT_CSV)
        phases = {item["phase"] for item in dataset["summary"]["timepoints"]}
        self.assertEqual(phases, {"pre-flight", "post-flight"})
        self.assertTrue(all(
            item["relative_to"] in {"launch", "return"}
            for item in dataset["summary"]["timepoints"]
        ))

    def test_suspect_sample_is_flagged_without_rewriting_source_values(self):
        dataset = build_osd569_dataset(DEFAULT_CSV)
        self.assertEqual(dataset["summary"]["suspect_sample_count"], 1)
        self.assertEqual(dataset["summary"]["suspect_record_count"], 19)
        self.assertEqual(dataset["quality_flags"][0]["subject_id"], "C003")
        self.assertEqual(dataset["quality_flags"][0]["timepoint"], "L-92")
        suspect = [
            item for item in dataset["records"]
            if item["subject_id"] == "C003" and item["timepoint"] == "L-92"
        ]
        self.assertEqual(len(suspect), 19)
        neutrophils = next(
            item for item in suspect
            if item["analyte_id"] == "absolute_neutrophils"
        )
        self.assertEqual(neutrophils["value"], 10.1)
        self.assertEqual(neutrophils["quality"], "suspect")

    def test_missing_analytes_are_not_filled(self):
        dataset = build_osd569_dataset(DEFAULT_CSV)
        sample = [
            item for item in dataset["records"]
            if item["subject_id"] == "C004" and item["timepoint"] == "L-92"
        ]
        self.assertEqual(len(sample), 19)
        self.assertNotIn(
            "mch", {item["analyte_id"] for item in sample}
        )

    def test_normalized_json_can_be_written_and_reloaded(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "nested" / "osd569.json"
            document = write_osd569_json(DEFAULT_CSV, target)
            self.assertTrue(target.is_file())
            loaded = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(loaded["summary"], document["summary"])


    def test_changed_source_file_is_rejected_by_checksum(self):
        with tempfile.TemporaryDirectory() as folder:
            changed = Path(folder) / "changed.csv"
            original = DEFAULT_CSV.read_text(encoding="utf-8")
            changed.write_text(original + "\\n", encoding="utf-8")
            with self.assertRaisesRegex(OSDRDataError, "checksum mismatch"):
                build_osd569_dataset(changed)

    def test_malformed_csv_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            bad = Path(folder) / "bad.csv"
            bad.write_text(
                "subject_id,value\nC001,2\n",
                encoding="utf-8",
            )
            with self.assertRaises(OSDRDataError):
                build_osd569_dataset(bad)


if __name__ == "__main__":
    unittest.main()
