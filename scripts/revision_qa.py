#!/usr/bin/env python3
"""Revision-aware acceptance checks for edited PowerPoint slides.

This validates *measurable* user requests against a pinned previous deck spec.
It cannot decide whether subjective feedback was understood: human review remains
required. Logical slide numbers are used, never physical TOC-return positions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import unicodedata

from check_storyboard import reveal_sequence

ROOT = Path(__file__).resolve().parent.parent
VALID_KINDS = {
    "slide_changed", "text_removed", "text_added", "text_replaced",
    "title_equals", "layout_is", "image_changed", "animation_preserved"
}


def canonical(data):
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize(value):
    return " ".join(unicodedata.normalize("NFKC", str(value)).casefold().split())


def visible_text(slide):
    """Text that the viewer sees (notes and source URLs are not slide content)."""
    out = []
    text_keys = {"title", "subtitle", "text", "badge", "root", "group_label",
                 "bottom", "caption", "quote", "attribution", "eyebrow"}
    def visit(node):
        if isinstance(node, list):
            for item in node:
                visit(item)
        elif isinstance(node, dict):
            for key, item in node.items():
                if key in text_keys and isinstance(item, str):
                    out.append(item)
                elif key in ("cards", "events", "bullets", "entries", "items", "left",
                             "right", "chart_data", "labels", "series"):
                    visit(item)
        elif isinstance(node, str):
            out.append(node)
    visit(slide)
    return normalize(" ".join(out))


def images(slide):
    found = []
    def walk(node):
        if isinstance(node, list):
            for item in node:
                walk(item)
        if isinstance(node, dict):
            if isinstance(node.get("image"), str):
                found.append(node["image"])
            for key in ("cards", "events", "bullets", "entries", "left", "right"):
                if key in node:
                    walk(node[key])
    walk(slide)
    return sorted(found)


def animations_preserved(old, new, before_mode, after_mode):
    if before_mode != after_mode:
        return False
    if len(old.get("cards", old.get("events", []))) and old["type"] == new["type"]:
        key = "cards" if "cards" in old else "events"
        before = {item["title"]: item.get("reveal", "auto" if i == 0 else "click")
                  for i, item in enumerate(old[key])}
        after = {item["title"]: item.get("reveal", "auto" if i == 0 else "click")
                 for i, item in enumerate(new.get(key, []))}
        return all(after.get(title) == reveal for title, reveal in before.items()
                   if title in after)
    if old.get("type") in ("section", "split") and new.get("type") == old.get("type"):
        before = {item["title"]: item.get("reveal", "auto" if i == 0 else "click")
                  for i, item in enumerate(old.get("bullets", []))}
        after = {item["title"]: item.get("reveal", "auto" if i == 0 else "click")
                 for i, item in enumerate(new.get("bullets", []))}
        return all(after.get(title) == reveal for title, reveal in before.items()
                   if title in after)
    return reveal_sequence(old, before_mode) == reveal_sequence(new, after_mode)


def load_baseline(folder, baseline_commit, before_path=None):
    if before_path:
        return read_json(before_path)
    if not re.fullmatch(r"[0-9a-fA-F]{40}", baseline_commit or ""):
        raise ValueError("baseline_commit must be an exact 40-character Git SHA")
    folder = Path(folder).resolve()
    if not folder.is_relative_to(ROOT / "decks"):
        raise ValueError("Deck must be located below decks/ for Git baseline lookup")
    ancestry = subprocess.run(["git", "merge-base", "--is-ancestor", baseline_commit, "HEAD"],
                              cwd=ROOT, capture_output=True)
    if ancestry.returncode:
        raise ValueError("baseline_commit must be an ancestor of the current checkout")
    rel = folder.relative_to(ROOT).as_posix() + "/deck.json"
    result = subprocess.run(["git", "show", f"{baseline_commit}:{rel}"], cwd=ROOT,
                            capture_output=True, text=True)
    if result.returncode:
        raise ValueError("Cannot retrieve pinned baseline deck.json: " + result.stderr.strip())
    return json.loads(result.stdout)


def verify(deck_folder, before_path=None, report_path=None):
    folder = Path(deck_folder).resolve()
    manifest_file = folder / "revision_requests.json"
    if not manifest_file.exists():
        return None
    manifest = read_json(manifest_file)
    if manifest.get("version") != 1:
        raise ValueError("revision_requests.json version must be 1")
    requests = manifest.get("requests")
    if not isinstance(requests, list) or not requests:
        raise ValueError("revision_requests.json requires at least one request")
    old = load_baseline(folder, manifest.get("baseline_commit"), before_path)
    new = read_json(folder / "deck.json")
    if old.get("id") != new.get("id") or old.get("requested_slide_count") != new.get("requested_slide_count"):
        raise ValueError("Revision cannot silently change deck ID or logical slide count")
    before, after = old["slides"], new["slides"]
    if len(before) != len(after):
        raise ValueError("Revision changed slide count; explicit deck restructuring is required")
    n = len(after)
    changed = {i for i in range(1, n+1) if canonical(before[i-1]) != canonical(after[i-1])}
    meta_before = {k: v for k, v in old.items() if k != "slides"}
    meta_after = {k: v for k, v in new.items() if k != "slides"}
    meta_changed = canonical(meta_before) != canonical(meta_after)
    allowed = set()
    deck_wide = False
    checked = []
    errors = []
    ids = set()

    for request in requests:
        if not isinstance(request, dict) or not isinstance(request.get("id"), str):
            errors.append("Each request needs a string id")
            continue
        rid = request["id"]
        if rid in ids:
            errors.append(f"Duplicate request id: {rid}")
        ids.add(rid)
        scope = request.get("scope")
        slide_numbers = request.get("slides", [])
        if scope not in ("slide", "deck"):
            errors.append(f"{rid}: scope must be slide or deck")
            continue
        if scope == "slide":
            if not isinstance(slide_numbers, list) or not slide_numbers or any(
                    type(x) is not int or x < 1 or x > n for x in slide_numbers):
                errors.append(f"{rid}: slide scope needs valid logical slide numbers")
                continue
            if len(set(slide_numbers)) != len(slide_numbers):
                errors.append(f"{rid}: duplicate slide numbers")
                continue
            target = set(slide_numbers)
        else:
            target = set(range(1, n+1))
            deck_wide = True
        if not isinstance(request.get("feedback"), str) or len(request["feedback"].strip()) < 5:
            errors.append(f"{rid}: preserve the user's original feedback")
        if not isinstance(request.get("checks"), list) or not request["checks"]:
            errors.append(f"{rid}: explicit acceptance checks are required")
            continue
        if not deck_wide:
            allowed.update(target)
        touched = bool(changed & target) or (scope == "deck" and meta_changed)
        if not touched:
            errors.append(f"{rid}: no change detected in requested scope")
        for check in request["checks"]:
            if not isinstance(check, dict):
                errors.append(f"{rid}: invalid check")
                continue
            kind = check.get("kind")
            slide = check.get("slide")
            if kind not in VALID_KINDS or type(slide) is not int or slide not in target:
                errors.append(f"{rid}: invalid check kind or logical slide target: {check}")
                continue
            src, dst = before[slide-1], after[slide-1]
            old_text, new_text = visible_text(src), visible_text(dst)
            old_val = normalize(check.get("old", check.get("text", "")))
            new_val = normalize(check.get("new", check.get("text", "")))
            ok = False
            if kind == "slide_changed":
                ok = slide in changed
            elif kind == "text_removed":
                ok = bool(old_val) and old_val in old_text and old_val not in new_text
            elif kind == "text_added":
                ok = bool(new_val) and new_val in new_text and new_val not in old_text
            elif kind == "text_replaced":
                ok = bool(old_val and new_val) and old_val in old_text and old_val not in new_text and new_val in new_text
            elif kind == "title_equals":
                ok = bool(check.get("text")) and normalize(dst.get("title", "")) == new_val
            elif kind == "layout_is":
                ok = bool(check.get("value")) and src.get("type") != dst.get("type") and dst.get("type") == check["value"]
            elif kind == "image_changed":
                ok = images(src) != images(dst)
            elif kind == "animation_preserved":
                ok = (old.get("animation_mode") == new.get("animation_mode") and
                      old.get("morph_to_slides", []) == new.get("morph_to_slides", []) and
                      animations_preserved(src, dst,
                                           old.get("animation_mode", "presenter"),
                                           new.get("animation_mode", "presenter")))
            checked.append({"request_id": rid, "kind": kind, "logical_slide": slide, "passed": ok})
            if not ok:
                errors.append(f"{rid}: {kind} failed on logical slide {slide}")

    if deck_wide:
        allowed = set(range(1, n+1))
    outside = sorted(changed - allowed)
    if outside:
        errors.append(f"Unauthorized changes outside requested slides: {outside}")
    if meta_changed and not deck_wide:
        errors.append("Top-level deck metadata changed without a deck-wide request")
    if not changed and not meta_changed:
        errors.append("No deck changes detected")
    if not checked:
        errors.append("No valid acceptance checks were evaluated")

    report = {
        "machine_passed": not errors,
        "baseline_commit": manifest.get("baseline_commit"),
        "affected_logical_slides": sorted(changed),
        "authorized_logical_slides": sorted(allowed),
        "global_change": deck_wide,
        "checks": checked,
        "errors": errors,
        "semantic_review_required": True,
        "visual_review_required": True,
        "user_acceptance": "pending",
        "baseline_sha256": hashlib.sha256(canonical(old).encode("utf-8")).hexdigest(),
        "current_sha256": hashlib.sha256(canonical(new).encode("utf-8")).hexdigest(),
    }
    if report_path:
        path = Path(report_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if errors:
        raise ValueError("Revision QA failed:\n- " + "\n- ".join(errors))
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("folder", type=Path, help="decks/<slug>")
    ap.add_argument("--before", type=Path, help="Standalone test baseline; otherwise use baseline_commit")
    ap.add_argument("--report", type=Path)
    args = ap.parse_args()
    report = verify(args.folder, before_path=args.before, report_path=args.report)
    if report is None:
        print("REVISION QA: no revision_requests.json (initial generation)")
    else:
        print("REVISION QA MACHINE PASS:", len(report["checks"]), "checks;",
              "user acceptance and semantic/visual review still required")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        print("REVISION QA FAILED:", exc, file=sys.stderr)
        sys.exit(1)
