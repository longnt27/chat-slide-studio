"""Regression tests: internal planning and measurable slide-edit acceptance."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from revision_qa import verify
from check_storyboard import validate_production_plan, validate_plan, check_deck_against_plan
from new_deck import new_deck


def fixture():
    old = {
        "id": "sample", "title": "Sample Presentation",
        "requested_slide_count": 3,
        "tier": "studio", "animation_mode": "presenter",
        "slides": [
            {"type": "cover", "title": "Introduction", "notes": "Speaker notes for the introduction."},
            {"type": "cards", "title": "Research outcomes",
             "cards": [
                {"title": "Strong evidence", "text": "Strong supporting evidence", "reveal": "auto"},
                {"title": "Weak evidence", "text": "Outdated assumptions", "reveal": "click"},
                {"title": "New findings", "text": "Current research observations", "reveal": "click"}
             ], "notes": "Introduce each finding in sequence."},
            {"type": "thanks", "title": "Thank you", "notes": "Thank the audience and invite questions."}
        ]
    }
    return old


def write_case(path, old, new, requests):
    path.mkdir(parents=True, exist_ok=True)
    (path / "deck.json").write_text(json.dumps(new), encoding="utf-8")
    (path / "before.json").write_text(json.dumps(old), encoding="utf-8")
    (path / "revision_requests.json").write_text(json.dumps({
        "version": 1, "baseline_commit": "f" * 40, "requests": requests
    }), encoding="utf-8")
    return path / "before.json"


class RevisionQATests(unittest.TestCase):
    def test_one_slide_edit_exact_removal_and_preserve_animation(self):
        old = fixture()
        new = deepcopy(old)
        del new["slides"][1]["cards"][1]
        requests = [{
            "id": "CR-001", "scope": "slide", "slides": [2],
            "feedback": "Remove the outdated assumptions card on slide 2.",
            "checks": [
                {"kind": "text_removed", "slide": 2, "text": "Outdated assumptions"},
                {"kind": "animation_preserved", "slide": 2}
            ]
        }]
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "sample"
            before = write_case(folder, old, new, requests)
            report = verify(folder, before_path=before, report_path=folder / "revision-report.json")
            self.assertTrue(report["machine_passed"])
            self.assertEqual(report["affected_logical_slides"], [2])
            self.assertEqual(report["authorized_logical_slides"], [2])
            self.assertTrue(report["visual_review_required"])
            self.assertEqual(report["user_acceptance"], "pending")

    def test_noop_edit_is_rejected(self):
        old = fixture()
        req = [{"id": "CR-002", "scope": "slide", "slides": [2],
                "feedback": "Remove outdated assumptions",
                "checks": [{"kind": "text_removed", "slide": 2, "text": "Outdated assumptions"}]}]
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "sample"
            before = write_case(folder, old, deepcopy(old), req)
            with self.assertRaisesRegex(ValueError, "no change detected"):
                verify(folder, before_path=before)

    def test_wrong_slide_changed_is_rejected(self):
        old = fixture()
        new = deepcopy(old)
        new["slides"][0]["title"] = "Unexpectedly rewritten"
        new["slides"][1]["cards"][1]["text"] = "Revised assumptions"
        req = [{"id": "CR-003", "scope": "slide", "slides": [2],
                "feedback": "Remove outdated assumptions",
                "checks": [{"kind": "text_removed", "slide": 2, "text": "Outdated assumptions"}]}]
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "sample"
            before = write_case(folder, old, new, req)
            with self.assertRaisesRegex(ValueError, "Unauthorized changes"):
                verify(folder, before_path=before)

    def test_missing_original_text_cannot_fake_removal(self):
        old = fixture()
        new = deepcopy(old)
        new["slides"][1]["title"] = "Rewritten research findings"
        req = [{"id": "CR-004", "scope": "slide", "slides": [2],
                "feedback": "Remove the thing that was never there",
                "checks": [{"kind": "text_removed", "slide": 2, "text": "nonexistent"}]}]
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "sample"
            before = write_case(folder, old, new, req)
            with self.assertRaisesRegex(ValueError, "text_removed failed"):
                verify(folder, before_path=before)

    def test_title_and_replacement_are_verifiable(self):
        old = fixture()
        new = deepcopy(old)
        new["slides"][1]["cards"][1]["text"] = "Verified methods"
        req = [{"id": "CR-005", "scope": "slide", "slides": [2],
                "feedback": "Replace outdated assumptions with verified methods",
                "checks": [{"kind": "text_replaced", "slide": 2,
                            "old": "Outdated assumptions", "new": "Verified methods"}]}]
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "sample"
            before = write_case(folder, old, new, req)
            self.assertEqual(len(verify(folder, before_path=before)["checks"]), 1)

    def test_deck_wide_change_allows_multiple_slides(self):
        old = fixture()
        new = deepcopy(old)
        new["theme"] = {"preset": "science"}
        new["slides"][0]["title"] = "New cover"
        new["slides"][1]["title"] = "Updated findings"
        req = [{"id": "CR-006", "scope": "deck",
                "feedback": "Refresh the whole presentation's appearance and language",
                "checks": [{"kind": "slide_changed", "slide": 1},
                           {"kind": "slide_changed", "slide": 2}]}]
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "sample"
            before = write_case(folder, old, new, req)
            report = verify(folder, before_path=before)
            self.assertTrue(report["global_change"])
            self.assertEqual(report["authorized_logical_slides"], [1, 2, 3])

    def test_internal_plan_does_not_forge_user_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = new_deck("internal-test", "Internal deck planning", slides=3,
                              root=root, tier="basic")
            plan = json.loads((folder / "storyboard.json").read_text())
            for slide in plan["slides"]:
                slide["takeaway"] = "A relevant audience takeaway"
                slide["composition"] = "Centered layout with a clean heading"
                slide["visual"] = "Relevant photo or typographic motif"
                if slide["layout"] == "section":
                    slide["title"] = "Key message"
            (folder / "storyboard.json").write_text(json.dumps(plan))
            result = validate_production_plan(folder)
            self.assertEqual(result["approval_channel"], "internal")
            self.assertFalse((folder / "approval.json").exists())
            new_deck("internal-test", "", root=root, from_internal_plan=True)
            self.assertTrue((folder / "deck.json").exists())
            self.assertTrue(check_deck_against_plan(folder, validate_plan(folder)))


if __name__ == "__main__":
    unittest.main()
