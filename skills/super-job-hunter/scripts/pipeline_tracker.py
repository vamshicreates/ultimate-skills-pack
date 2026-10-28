#!/usr/bin/env python3
"""
pipeline_tracker.py — Application Lifecycle & Outreach Manager.
Manages application states (Discovered, Tailored, Ready, Applied, Interview, Offer, Rejected),
tracks dates, follow-up cadence, and generates stage-appropriate communication.
"""

import argparse
import csv
import datetime
import json
import os
import sys
from pathlib import Path

DEFAULT_TRACKER_PATH = Path(".job-hunter/pipeline_tracker.json")


def load_tracker(path: Path = DEFAULT_TRACKER_PATH) -> list:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_tracker(records: list, path: Path = DEFAULT_TRACKER_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def add_or_update(job_data: dict, path: Path = DEFAULT_TRACKER_PATH):
    records = load_tracker(path)
    url = job_data.get("url", "")
    updated = False
    now_iso = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    for r in records:
        if (url and r.get("url") == url) or (r.get("company") == job_data.get("company") and r.get("role") == job_data.get("role")):
            r.update(job_data)
            r["updated_at"] = now_iso
            updated = True
            break

    if not updated:
        job_data["created_at"] = now_iso
        job_data["updated_at"] = now_iso
        if "status" not in job_data:
            job_data["status"] = "discovered"
        records.append(job_data)

    save_tracker(records, path)
    return records


def check_quiet_applications(records: list, quiet_days: int = 10) -> list:
    quiet = []
    now = datetime.datetime.now()
    for r in records:
        if r.get("status") == "applied":
            applied_date_str = r.get("applied_date") or r.get("updated_at")
            if applied_date_str:
                try:
                    dt = datetime.datetime.strptime(applied_date_str[:10], "%Y-%m-%d")
                    diff = (now - dt).days
                    if diff >= quiet_days:
                        quiet.append({**r, "days_silent": diff})
                except ValueError:
                    pass
    return quiet


def draft_follow_up(company: str, role: str, contact: str = "Hiring Team") -> str:
    return (
        f"Subject: Following up on Application – {role} – {company}\n\n"
        f"Hi {contact},\n\n"
        f"I hope you are having a productive week. I am following up on my application submitted recently for the {role} role at {company}.\n\n"
        f"I remain very excited about {company}'s roadmap and would welcome the chance to discuss how my hands-on background and verified outcomes can support your team's immediate milestones.\n\n"
        f"Please let me know if any additional details or work references would be helpful at this stage.\n\n"
        f"Best regards,\n[Your Name]"
    )


def draft_thank_you(company: str, role: str, interviewer_name: str = "Interviewer", topic_discussed: str = "team priorities") -> str:
    return (
        f"Subject: Thank you – {role} interview with {company}\n\n"
        f"Dear {interviewer_name},\n\n"
        f"Thank you very much for taking the time to speak with me today about the {role} position at {company}.\n\n"
        f"I particularly enjoyed our discussion around {topic_discussed}. It reinforced my enthusiasm for the team's mission, and I am confident that my experience will allow me to hit the ground running.\n\n"
        f"Looking forward to the next steps. Have a great rest of your week!\n\n"
        f"Warm regards,\n[Your Name]"
    )


def main():
    parser = argparse.ArgumentParser(description="Application Pipeline Lifecycle Manager")
    parser.add_argument("--list", action="store_true", help="List all tracked applications")
    parser.add_argument("--status", type=str, help="Filter by status (discovered, tailored, ready, applied, interview, offer, rejected)")
    parser.add_argument("--check-quiet", action="store_true", help="Find applications with >10 days without update")
    parser.add_argument("--followup", nargs=2, metavar=("COMPANY", "ROLE"), help="Draft follow-up email")
    parser.add_argument("--thankyou", nargs=3, metavar=("COMPANY", "ROLE", "INTERVIEWER"), help="Draft thank you note")
    parser.add_argument("--export-csv", type=str, help="Export pipeline to CSV file")

    args = parser.parse_args()
    records = load_tracker()

    if args.list:
        filtered = [r for r in records if not args.status or r.get("status") == args.status]
        print(f"\n📋 PIPELINE TRACKER ({len(filtered)} applications):")
        print("-" * 75)
        for r in filtered:
            print(f"• [{r.get('status', 'unknown').upper()}] {r.get('role', 'Role')} @ {r.get('company', 'Company')} | Fit: {r.get('fit_score', 'N/A')}% | Updated: {r.get('updated_at', '')}")
            if r.get("job_url"):
                print(f"  URL: {r.get('job_url')}")
        print("-" * 75 + "\n")

    elif args.check_quiet:
        quiet = check_quiet_applications(records)
        print(f"\n⏳ QUIET APPLICATIONS (>10 days since submission): {len(quiet)}")
        for q in quiet:
            print(f"• {q.get('role')} @ {q.get('company')} — Silent for {q.get('days_silent')} days. (Applied: {q.get('applied_date', 'N/A')})")
        print("\n")

    elif args.followup:
        print("\n" + draft_follow_up(args.followup[0], args.followup[1]) + "\n")

    elif args.thankyou:
        print("\n" + draft_thank_you(args.thankyou[0], args.thankyou[1], args.thankyou[2]) + "\n")

    elif args.export_csv:
        if records:
            keys = list(records[0].keys())
            with open(args.export_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(records)
            print(f"Exported {len(records)} records to {args.export_csv}")
        else:
            print("No records to export.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
