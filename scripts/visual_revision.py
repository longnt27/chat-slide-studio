#!/usr/bin/env python3
"""Render the pinned previous deck and compare it with edited slide previews.

This supplements source-level revision assertions. A missing baseline asset or
rendering dependency is reported as NOT_RUN rather than pretending visual QA ran.
It does not replace human visual review or Microsoft PowerPoint playback.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops, ImageStat

from revision_qa import load_baseline, verify, visible_text, images

ROOT = Path(__file__).resolve().parent.parent


def run(*args):
    subprocess.run([str(a) for a in args], cwd=ROOT, check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def compare(deck_dir, report_path=None):
    folder = Path(deck_dir).resolve()
    revision = verify(folder)
    if revision is None:
        return None
    dist = folder / "dist"
    output = dist / "revision-comparison"
    output.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "NOT_RUN",
        "reason": "",
        "visual_review_required": True,
        "native_powerpoint_playback_tested": False,
        "slide_diffs": [],
        "regression_errors": [],
    }
    try:
        old = load_baseline(folder, revision["baseline_commit"])
        new = json.loads((folder / "deck.json").read_text(encoding="utf-8"))
        current_route = json.loads((dist / "slide-route.json").read_text(encoding="utf-8"))
        src_assets = folder / "verified-assets"
        with tempfile.TemporaryDirectory(prefix="slide-revision-before-") as tmp:
            tmpdir = Path(tmp)
            (tmpdir / "deck.json").write_text(
                json.dumps(old, ensure_ascii=False), encoding="utf-8")
            if src_assets.exists():
                (tmpdir / "verified-assets").symlink_to(src_assets, target_is_directory=True)
            run(sys.executable, ROOT / "scripts/presentation_profile.py", tmpdir / "deck.json")
            original_route = json.loads((tmpdir / "dist" / "slide-route.json").read_text(encoding="utf-8"))
            if original_route["physical_slides"] != current_route["physical_slides"]:
                raise ValueError("Physical slide route changed; cannot compare pages 1:1")
            run("node", ROOT / "scripts/build_deck.cjs", tmpdir)
            slug = old["id"]
            run(sys.executable, ROOT / "scripts/render_deck.py",
                tmpdir / "dist" / f"{slug}.base.pptx",
                "--out", tmpdir / "preview",
                "--expected", current_route["physical_count"])

            from PIL import ImageDraw
            targets = set(revision["authorized_logical_slides"])
            for entry in current_route["physical_slides"]:
                physical = int(entry["physical"])
                logical = int(entry["logical"])
                before_img = tmpdir / "preview" / "slides" / f"slide-{physical:02d}.png"
                after_img = dist / "preview" / "slides" / f"slide-{physical:02d}.png"
                if not before_img.exists() or not after_img.exists():
                    raise FileNotFoundError(f"Missing before/after slide preview {physical}")
                with Image.open(before_img) as left, Image.open(after_img) as right:
                    before_rgb = left.convert("RGB")
                    after_rgb = right.convert("RGB")
                    if before_rgb.size != after_rgb.size:
                        raise ValueError(f"Different render resolutions at slide {physical}")
                    difference = ImageChops.difference(before_rgb, after_rgb)
                    mean = sum(ImageStat.Stat(difference).mean) / 3
                    changed = mean > 0.25  # 8-bit mean channel difference
                    allowed = logical in targets
                    report["slide_diffs"].append({
                        "physical_slide": physical,
                        "logical_slide": logical,
                        "mean_absolute_rgb_difference": round(mean, 4),
                        "visually_changed": changed,
                        "authorized_to_change": allowed,
                    })
                    visible_change_required = (
                        visible_text(old["slides"][logical-1]) != visible_text(new["slides"][logical-1])
                        or images(old["slides"][logical-1]) != images(new["slides"][logical-1])
                        or old["slides"][logical-1].get("type") != new["slides"][logical-1].get("type")
                    )
                    if allowed and visible_change_required and not changed:
                        report["regression_errors"].append(
                            f"Physical slide {physical} (logical {logical}) did not reflect its requested visible change")
                    if changed and not allowed:
                        report["regression_errors"].append(
                            f"Physical slide {physical} (logical {logical}) changed unexpectedly")
                    if allowed:
                        scale = min(1, 900 / before_rgb.width)
                        w, h = int(before_rgb.width * scale), int(before_rgb.height * scale)
                        left_small = before_rgb.resize((w, h))
                        right_small = after_rgb.resize((w, h))
                        combined = Image.new("RGB", (w * 2 + 16, h), "#dfe4ea")
                        combined.paste(left_small, (0, 0))
                        combined.paste(right_small, (w + 16, 0))
                        combined.save(output / f"physical-{physical:02d}-logical-{logical:02d}-before-after.png")
            report["status"] = "PASS" if not report["regression_errors"] else "FAIL"
    except (OSError, ValueError, subprocess.CalledProcessError, KeyError) as exc:
        report["reason"] = str(exc)
        if report["status"] != "FAIL":
            report["status"] = "NOT_RUN"
    if report_path:
        Path(report_path).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                     encoding="utf-8")
    if report["status"] == "FAIL":
        raise ValueError("Visual revision regression: " + "; ".join(report["regression_errors"]))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = compare(args.folder, args.report)
    print("VISUAL REVISION:", result["status"] if result else "not a revision",
          result.get("reason", "") if result else "")
