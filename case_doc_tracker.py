#!/usr/bin/env python3
"""
case_doc_tracker.py
Track necessary case documents. Mark items as received or rejected, and
generate a status report.

Live demo: https://biancabcarlson.github.io/Case-Doc-Tracker/

Usage:
    python case_doc_tracker.py checklist.json -o status_report.md

Input (checklist.json) — SYNTHETIC EXAMPLE:
{
  "case_id": "CASE-DEMO-0091",
  "items": [
    {"category": "Government-issued ID", "status": "received", "notes": "Received via email 8/29"},
    {"category": "Last 3 months bank statements", "status": "received", "notes": ""},
    {"category": "Proof of address", "status": "rejected", "notes": "Submitted photo was cropped/unreadable"},
    {"category": "Correspondence log", "status": "not_collected", "notes": ""}
  ]
}

"status" is one of: "received", "rejected", "not_collected". Mark each
item's status directly. "Rejected" means the submitted document needs
to be resubmitted.

Backward compatible with the old boolean format
({"collected": true/false}) — that's treated as "received"/"not_collected".
"""

import json
import argparse
from datetime import datetime, timezone


def item_status(item):
    if "status" in item:
        return item["status"]
    return "received" if item.get("collected") else "not_collected"


def build_report(data):
    items = data.get("items", [])
    received = [i for i in items if item_status(i) == "received"]
    rejected = [i for i in items if item_status(i) == "rejected"]
    not_collected = [i for i in items if item_status(i) == "not_collected"]

    lines = [f"# Documentation Status — {data.get('case_id', 'Unknown Case')}", ""]
    lines.append(f"Updated: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"Progress: {len(received)}/{len(items)} received"
                 + (f" · {len(rejected)} rejected, awaiting resend" if rejected else ""))
    lines.append("")

    lines.append("## ✅ Received")
    if received:
        for i in received:
            note = f" — {i['notes']}" if i.get("notes") else ""
            lines.append(f"- {i['category']}{note}")
    else:
        lines.append("_None yet._")
    lines.append("")

    lines.append("## ❌ Rejected — please resend")
    if rejected:
        for i in rejected:
            note = f" — {i['notes']}" if i.get("notes") else ""
            lines.append(f"- {i['category']}{note}")
    else:
        lines.append("_None._")
    lines.append("")

    lines.append("## ⬜ Not yet collected")
    if not_collected:
        for i in not_collected:
            note = f" — {i['notes']}" if i.get("notes") else ""
            lines.append(f"- {i['category']}{note}")
    else:
        lines.append("_Nothing outstanding._")

    return "\n".join(lines)


def build_shareable_summary(data):
    items = data.get("items", [])
    received = [i["category"] for i in items if item_status(i) == "received"]
    rejected = [i["category"] for i in items if item_status(i) == "rejected"]
    not_collected = [i["category"] for i in items if item_status(i) == "not_collected"]
    case_id = data.get("case_id", "Unknown Case")

    still_needed = [f"- {c}" for c in not_collected] + [f"- {c} (resend — previous submission rejected)" for c in rejected]

    lines = [f"Case {case_id} — Documentation Status", ""]
    lines.append("Still needed from customer:")
    lines += still_needed if still_needed else ["- Nothing outstanding"]
    lines.append("")
    lines.append("Already received:")
    lines += [f"- {c}" for c in received] if received else ["- Nothing yet"]

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Generate a documentation status report from a checklist.")
    ap.add_argument("input", help="Path to checklist JSON file")
    ap.add_argument("-o", "--output", default="status_report.md")
    ap.add_argument("--summary", help="Optional path to also write a plain-text shareable summary")
    args = ap.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    report = build_report(data)
    with open(args.output, "w") as f:
        f.write(report)
    print(f"Report written to {args.output}")

    if args.summary:
        summary = build_shareable_summary(data)
        with open(args.summary, "w") as f:
            f.write(summary)
        print(f"Shareable summary written to {args.summary}")


if __name__ == "__main__":
    main()
