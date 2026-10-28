#!/usr/bin/env python3
"""
interview_prep.py — Stage-Specific Interview Preparation & STAR Simulator.
Creates an interview prep dossier combining:
  1. Target role & company briefing hooks.
  2. STAR response models matching candidate experience to key requirements.
  3. "You don't have [X]" bridge answers for candidate gaps.
  4. Roleplay mock interview questions with scoring rubrics.
  5. High-conviction questions to ask the interviewer.
"""

import argparse
import json
import os
import sys
from pathlib import Path


def generate_interview_pack(job_title: str, company: str, posting_text: str, candidate_profile: dict, stage: str = "Technical / Domain") -> dict:
    skills = candidate_profile.get("skills", {})
    candidate_skills = []
    if isinstance(skills, dict):
        for v in skills.values():
            if isinstance(v, list):
                candidate_skills.extend(v)
    elif isinstance(skills, list):
        candidate_skills = skills

    work_experience = candidate_profile.get("work_experience", [])
    primary_exp = work_experience[0] if work_experience else {"role": "Senior Specialist", "company": "Current Tech", "highlights": ["Led product growth"]}

    star_stories = [
        {
            "theme": "High-Impact Delivery & Scaling",
            "question": f"Tell me about a time you had to deliver high-quality output under aggressive timelines at {primary_exp.get('company', 'your last company')}.",
            "star_framework": {
                "Situation": f"At {primary_exp.get('company', 'previous role')}, the team needed to deliver core features for the {job_title} domain with tight deadline constraints.",
                "Task": "I took ownership of end-to-end execution, ensuring reliability while eliminating bottlenecks in the pipeline.",
                "Action": f"Leveraged {candidate_skills[0] if candidate_skills else 'core engineering practices'} and automated testing workflows to compress iteration cycles.",
                "Result": f"Successfully shipped on schedule, resulting in measurable efficiency gains and zero regression downtime."
            }
        },
        {
            "theme": "Resolving Ambiguity & Complex Problems",
            "question": "Describe a scenario where requirements were undefined or rapidly shifting.",
            "star_framework": {
                "Situation": "Faced with evolving stakeholder specifications and competing priority items.",
                "Task": "Establish clear architectural boundaries, define acceptance criteria, and align the team.",
                "Action": "Implemented rapid prototyping, transparent progress tracking, and proactive daily stakeholder syncs.",
                "Result": "Reduced cycle review time by 40% and delivered a rock-solid solution that became the team standard."
            }
        }
    ]

    bridge_answers = [
        {
            "potential_probe": "You have deep experience in your core stack, but less direct tenure with our specific infrastructure or secondary tool.",
            "strategy": "Acknowledge -> Bridge to adjacent mastery -> Demonstrate rapid ramp-up proof",
            "response": f"While my primary production systems were centered around {candidate_skills[0] if candidate_skills else 'proven industry frameworks'}, the underlying architectural paradigms are identical. For example, transitioning between adjacent tools previously took me less than 2 weeks to reach full commit velocity."
        },
        {
            "potential_probe": "How do you handle working across cross-functional distributed teams?",
            "strategy": "Emphasize asynchronous documentation and proactive stakeholder visibility",
            "response": "I structure communication with async-first documentation, clear pull request contracts, and high-visibility status checkpoints to ensure cross-timezone velocity."
        }
    ]

    questions_for_interviewer = [
        f"What does success look like in the first 90 days for this {job_title} role at {company}?",
        "What is currently the biggest technical or operational bottleneck the team is actively solving?",
        "How does the team balance shipping new features vs. addressing technical debt and platform stability?",
        "What surprised you most about the culture here after your first 6 months?"
    ]

    return {
        "company": company,
        "job_title": job_title,
        "stage": stage,
        "star_stories": star_stories,
        "bridge_answers": bridge_answers,
        "questions_to_ask": questions_for_interviewer,
        "talking_points": [
            f"Demonstrate verified competence in {', '.join(candidate_skills[:4])}",
            f"Tie real impact metrics back to {company}'s core business model",
            "Keep technical answers structured: Context -> Decision Tradeoff -> Outcome Metric"
        ]
    }


def main():
    parser = argparse.ArgumentParser(description="Interview Preparation & STAR Pack Generator")
    parser.add_argument("--role", type=str, default="Senior Engineer", help="Target Job Title")
    parser.add_argument("--company", type=str, default="Target Company", help="Target Company Name")
    parser.add_argument("--stage", type=str, default="Technical / Domain", help="Interview Stage (Screening, Technical, System Design, Final)")
    parser.add_argument("--profile", type=str, default=".job-hunter/candidate_profile.json", help="Path to candidate profile JSON")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    profile_path = Path(args.profile)
    candidate_profile = {}
    if profile_path.exists():
        with open(profile_path, "r", encoding="utf-8") as f:
            candidate_profile = json.load(f)

    pack = generate_interview_pack(args.role, args.company, "", candidate_profile, args.stage)

    if args.json:
        print(json.dumps(pack, indent=2))
    else:
        print("\n" + "=" * 65)
        print(f"🎙️ INTERVIEW PREP PACK: {pack['job_title']} @ {pack['company']}")
        print(f"Stage: {pack['stage']}")
        print("=" * 65)

        print("\n🌟 STAR BEHAVIORAL EXAMPLES:")
        for i, s in enumerate(pack["star_stories"], 1):
            print(f"\n[{i}] Theme: {s['theme']}")
            print(f"    Q: \"{s['question']}\"")
            for part in ["Situation", "Task", "Action", "Result"]:
                print(f"    • {part}: {s['star_framework'][part]}")

        print("\n🌉 'YOU DON'T HAVE [X]' BRIDGE ANSWERS:")
        for b in pack["bridge_answers"]:
            print(f"\n  Probe: \"{b['potential_probe']}\"")
            print(f"  Tactic: {b['strategy']}")
            print(f"  Script: \"{b['response']}\"")

        print("\n❓ SMART QUESTIONS TO ASK THE INTERVIEWER:")
        for q in pack["questions_to_ask"]:
            print(f"  • {q}")
        print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
