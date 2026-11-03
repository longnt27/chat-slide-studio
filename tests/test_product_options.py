"""Tier, brand color/style and branch-isolation regression tests."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from new_deck import new_deck
from check_storyboard import validate_plan, check_deck_against_plan
from presentation_profile import TIERS, motion_of, compile_route

class ProductTierTests(unittest.TestCase):
    def test_new_tier_order_and_defaults(self):
        self.assertEqual(TIERS,("basic","studio","pro"))
        self.assertEqual(motion_of({"tier":"basic"}),"none")
        self.assertEqual(motion_of({"tier":"studio"}),"presenter")
        self.assertEqual(motion_of({"tier":"pro"}),"presenter")
        # Existing demo fixture omitted tier and must remain animated.
        self.assertEqual(motion_of({}),"presenter")

    def test_parallel_projects_have_separate_scopes_and_design(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for tier,slug,color,style in (
                ("basic","first-deck","#2648D8","Swiss minimalist"),
                ("studio","second-deck","#FF8800","corporate"),
                ("pro","third-deck","#3AA88F","editorial")):
                branch=f"decks/{slug}"
                folder=new_deck(slug,f"{slug} presentation",slides=3,root=root,
                    tier=tier,branch=branch,primary_color=color,style=style)
                plan=json.loads((folder/"storyboard.json").read_text())
                self.assertEqual(plan["branch"],branch)
                self.assertEqual(plan["design"],{"primary_color":color,"style":style})
                for slide in plan["slides"]:
                    slide["takeaway"]="A verifiable message about the subject"
                    slide["composition"]="Balanced image and text composition"
                    slide["visual"]="Relevant photo and an editable layout"
                    if slide["layout"]=="section":
                        slide["title"]="Supporting evidence"
                        slide["content_units"]=1
                        slide["reveal_sequence"]=["static" if tier=="basic" else "auto"
                (folder/"storyboard.json").write_text(json.dumps(plan),encoding="utf-8")
                self.assertTrue(validate_plan(folder))
                new_deck(slug,"",root=root,from_internal_plan=True)
                deck=json.loads((folder/"deck.json").read_text())
                self.assertEqual(deck["branch"],branch)
                self.assertEqual(deck["design"],plan["design"])
                self.assertEqual(deck["tier"],tier)
                self.assertEqual(deck["animation_mode"],"none" if tier=="basic" else "presenter")
                self.assertTrue(check_deck_against_plan(folder,plan))
                self.assertEqual(compile_route(deck)["tier"],tier)
                for kind in ("storyboard","deck"):
                    schema=json.loads((ROOT/"schemas"/f"{kind}.schema.json").read_text())
                    Draft202012Validator(schema).validate(plan if kind=="storyboard" else deck)
            self.assertEqual(len(list((root/"decks").iterdir())),3)

    def test_bad_color_branch_or_style_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            cases=[
                {"primary_color":"blue"},
                {"primary_color":"#0AF"},
                {"branch":"main"},
                {"branch":"bad branch"},
                {"style":""}
            ]
            for i,overrides in enumerate(cases):
                with self.subTest(case=overrides):
                    with self.assertRaises(ValueError):
                        new_deck(f"invalid-{i}","Invalid options example",slides=3,
                                 root=root,**overrides)

    def test_design_locked_to_internal_plan_until_deck_wide_revision(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);folder=new_deck("design-lock","Design contract deck",
                        slides=3,root=root,primary_color="#F97316",
                        style="editorial magazine")
            plan=json.loads((folder/"storyboard.json").read_text())
            for slide in plan["slides"]:
                slide.update(takeaway="Subject takeaway",composition="Editorial grid",
                             visual="Sourced photo")
                if slide["layout"]=="section":slide["title"]="Detailed evidence"
            (folder/"storyboard.json").write_text(json.dumps(plan))
            new_deck("design-lock","",root=root,from_internal_plan=True)
            deck=json.loads((folder/"deck.json").read_text())
            deck["design"]["primary_color"]="#1D4ED8"
            (folder/"deck.json").write_text(json.dumps(deck))
            with self.assertRaisesRegex(ValueError,"design differs"):
                check_deck_against_plan(folder,plan)
            self.assertTrue(check_deck_against_plan(folder,plan,
                                                   allow_design_change=True))

    def test_renderer_uses_selected_brand_color_in_real_slide(self):
        # Tests actual native PptxGenJS build; optional when local npm deps absent.
        if not (ROOT/"node_modules"/"pptxgenjs").exists():
            self.skipTest("npm dependencies not installed")
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)/"brand-smoke";folder.mkdir()
            sample={
              "id":"brand-smoke","title":"Brand color test deck",
              "tier":"basic","animation_mode":"none",
              "requested_slide_count":3,
              "design":{"primary_color":"#FF8500","style":"editorial"},
              "slides":[
                {"type":"cover","title":"Test Introduction","notes":"Intro speaker notes"},
                {"type":"section","title":"Meaningful Evidence","subtitle":"Valid technical brief",
                 "bullets":[{"title":"One point","text":"Evidence","reveal":"static"}],
                 "notes":"Speaker notes for evidence"},
                {"type":"thanks","title":"Thank you","notes":"Closing notes"}]
            }
            (folder/"deck.json").write_text(json.dumps(sample),encoding="utf-8")
            run=subprocess.run(["node",str(ROOT/"scripts"/"build_deck.cjs"),str(folder)],
                               cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stdout+" "+run.stderr)
            base=folder/"dist"/"brand-smoke.base.pptx"
            self.assertTrue(base.exists())
            with ZipFile(base) as z:
                slides=" ".join(z.read(f"ppt/slides/slide{i}.xml").decode("utf-8")
                                for i in range(1,4))
                self.assertIn("FF8500",slides)
                self.assertIn("Noto Serif",z.read("ppt/theme/theme1.xml").decode("utf-8"))

if __name__=="__main__":
    unittest.main()
