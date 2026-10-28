#!/usr/bin/env python3
"""
upskill_planner.py — Career Gap Analysis & Upskilling Heatmap.
Analyzes market requirements across scraped/ranked jobs vs. candidate profile,
ranks skill gaps by market demand frequency, and generates actionable learning paths.
"""

import argparse
import collections
import json
import os
import re
import sys
from pathlib import Path


def generate_upskill_plan(candidate_profile: dict, job_postings: list) -> dict:
    skills_data = candidate_profile.get("skills", {})
    candidate_skills = set()
    if isinstance(skills_data, dict):
        for sub in skills_data.values():
            if isinstance(sub, list):
                candidate_skills.update([s.lower().strip() for s in sub])
            elif isinstance(sub, str):
                candidate_skills.add(sub.lower().strip())
    elif isinstance(skills_data, list):
        candidate_skills.update([s.lower().strip() for s in skills_data])

    # Common high-value tech skills catalog with recommended resources
    TECH_CATALOG = {
        "docker": {"category": "DevOps & Cloud", "est_hours": 15, "resource": "Docker Getting Started & Labs"},
        "kubernetes": {"category": "DevOps & Cloud", "est_hours": 30, "resource": "Kubernetes the Hard Way / Mumshad CKA"},
        "aws": {"category": "Cloud Architecture", "est_hours": 40, "resource": "AWS Certified Solutions Architect Associate Labs"},
        "system design": {"category": "Architecture", "est_hours": 25, "resource": "Alex Xu System Design Interview Volume 1 & 2"},
        "graphql": {"category": "APIs & Backend", "est_hours": 12, "resource": "HowToGraphQL Tutorial & Apollo Odyssey"},
        "redis": {"category": "Databases & Caching", "est_hours": 10, "resource": "Redis University RU101"},
        "postgresql": {"category": "Databases & Caching", "est_hours": 20, "resource": "PostgreSQL Mastery by The Art of PostgreSQL"},
        "tailwind": {"category": "Frontend UI", "est_hours": 8, "resource": "Tailwind CSS Official Labs & Refactoring UI"},
        "typescript": {"category": "Core Languages", "est_hours": 20, "resource": "Total TypeScript by Matt Pocock"},
        "next.js": {"category": "Frontend & Fullstack", "est_hours": 25, "resource": "Next.js Official App Router Course"},
        "llm": {"category": "AI / ML Engineering", "est_hours": 30, "resource": "DeepLearning.AI LangChain & LLM Ops Courses"},
        "ci/cd": {"category": "DevOps", "est_hours": 10, "resource": "GitHub Actions Official Certification Guide"}
    }

    # Count occurrences across all scraped job postings
    skill_mentions = collections.Counter()
    total_postings = len(job_postings) or 1

    for post in job_postings:
        text = (post.get("full_text") or post.get("description") or "").lower()
        for tech in TECH_CATALOG:
            if re.search(r"\b" + re.escape(tech) + r"\b", text):
                skill_mentions[tech] += 1

    # Filter out skills candidate already has
    gap_skills = []
    for tech, count in skill_mentions.most_common():
        if tech not in candidate_skills:
            info = TECH_CATALOG.get(tech, {})
            demand_pct = int((count / total_postings) * 100) if total_postings > 0 else 50
            priority = "High" if demand_pct >= 40 else ("Medium" if demand_pct >= 20 else "Low")
            gap_skills.append({
                "skill": tech.title(),
                "category": info.get("category", "General"),
                "frequency": count,
                "demand_percentage": max(demand_pct, 15),
                "priority": priority,
                "est_learning_hours": info.get("est_hours", 20),
                "recommended_resource": info.get("resource", "Official Documentation & Sandbox")
            })

    # Sort gaps by priority
    gap_skills.sort(key=lambda x: x["frequency"], reverse=True)

    return {
        "candidate_skills_count": len(candidate_skills),
        "postings_analyzed": len(job_postings),
        "top_gaps": gap_skills[:8],
        "estimated_total_upskill_hours": sum(g["est_learning_hours"] for g in gap_skills[:5]),
        "recommended_first_focus": gap_skills[0]["skill"] if gap_skills else "None (Core Stack Complete)"
    }


def main():
    parser = argparse.ArgumentParser(description="Upskill Heatmap & Career Roadmap Generator")
    parser.add_argument("--profile", type=str, default=".job-hunter/candidate_profile.json", help="Candidate Profile JSON")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    profile_path = Path(args.profile)
    candidate_profile = {}
    if profile_path.exists():
        with open(profile_path, "r", encoding="utf-8") as f:
            candidate_profile = json.load(f)

    # Sample baseline postings for demo / fallback analysis
    sample_postings = [
        {"description": "Looking for a fullstack engineer with TypeScript, Next.js, Docker, Kubernetes, and AWS microservices experience."},
        {"description": "Senior Developer needed. Must know Python, PostgreSQL, Redis, Docker, System Design, and LLM prompt integrations."},
        {"description": "Frontend specialist required. Deep knowledge of React, Next.js, TypeScript, Tailwind CSS, and CI/CD pipelines."},
        {"description": "Backend engineer needed for high scale distributed systems using Go, AWS, Kubernetes, GraphQL, and Redis."}
    ]

    plan = generate_upskill_plan(candidate_profile, sample_postings)

    if args.json:
        print(json.dumps(plan, indent=2))
    else:
        print("\n" + "=" * 65)
        print("📈 CAREER GAP ANALYSIS & UPSKILLING HEATMAP")
        print("=" * 65)
        print(f"Postings Analyzed: {plan['postings_analyzed']}")
        print(f"Top Recommended Focus: 🎯 {plan['recommended_first_focus']}")
        print(f"Est. Hours to Bridge Top 5 Gaps: {plan['estimated_total_upskill_hours']} hours")
        print("\n🔥 HIGH DEMAND SKILL GAPS:")
        print(f"{'Skill':<18} {'Category':<22} {'Market Demand':<15} {'Hours':<8} {'Resource'}")
        print("-" * 75)
        for g in plan["top_gaps"]:
            print(f"{g['skill']:<18} {g['category']:<22} {g['demand_percentage']}% ({g['frequency']} jobs)  {g['est_learning_hours']}h     {g['recommended_resource']}")
        print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
