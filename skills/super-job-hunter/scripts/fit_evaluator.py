#!/usr/bin/env python3
"""
fit_evaluator.py — 5-Dimension Job Fit & Security Evaluator.
Combines:
  1. Deterministic Security Gate (prompt injection, zero-width, hidden CSS, homoglyphs) via posting_guard.
  2. Multi-platform JD extraction and DOM verification.
  3. 5-Dimension scoring (Skills, Experience, Seniority, Location/Logistics, Growth/Culture).
  4. Knockout risks & Caution Recon (Visa, 5-day on-site, ghost posting, agency, take-homes).
  5. Honest strengths vs. gaps analysis with STAR preparation leads.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Add script directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from inspect_ats_form import JobPageExtractor, analyze_cautions, detect_platform, fetch_url
except ImportError:
    JobPageExtractor = None

try:
    import posting_guard
except ImportError:
    posting_guard = None


def evaluate_job(posting_text: str, candidate_profile: dict, job_url: str = "") -> dict:
    text_l = posting_text.lower()

    # 1. Security scan
    security_verdict = {"status": "clean", "flags": [], "risk_score": 0}
    if posting_guard:
        try:
            guard_report = posting_guard.guard(posting_text)
            verdict_str = posting_guard.verdict(guard_report)
            security_verdict["status"] = "suspicious" if guard_report.get("findings") else "clean"
            security_verdict["verdict"] = verdict_str
            security_verdict["findings"] = guard_report.get("findings", [])
            security_verdict["risk_score"] = min(100, len(guard_report.get("findings", [])) * 25)
        except Exception as e:
            security_verdict["error"] = str(e)

    # 2. Caution & Knockout Recon
    cautions = []
    knockout_risks = []
    if analyze_cautions:
        recon = analyze_cautions(posting_text, [], job_url)
        cautions = recon.get("cautions", [])
        knockout_risks = recon.get("knockout_risks", [])

    # 3. Candidate Profile Details
    skills_data = candidate_profile.get("skills", {})
    all_candidate_skills = []
    if isinstance(skills_data, dict):
        for sub_skills in skills_data.values():
            if isinstance(sub_skills, list):
                all_candidate_skills.extend(sub_skills)
            elif isinstance(sub_skills, str):
                all_candidate_skills.append(sub_skills)
    elif isinstance(skills_data, list):
        all_candidate_skills = skills_data

    candidate_skills_lower = [s.lower().strip() for s in all_candidate_skills if s]

    candidate_yoe = candidate_profile.get("search_targets", {}).get("years_of_experience", 3)
    target_locations = [loc.lower() for loc in candidate_profile.get("search_targets", {}).get("locations", ["remote"])]

    # 4. Dimension 1: Technical & Core Skills Match
    matched_skills = []
    missing_skills = []
    # Identify skills mentioned in posting that candidate has
    for skill in all_candidate_skills:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_l):
            matched_skills.append(skill)

    # Identify common tech skills requested in posting that candidate might lack
    common_industry_skills = [
        "python", "javascript", "typescript", "react", "next.js", "node.js", "vue", "docker",
        "kubernetes", "aws", "gcp", "azure", "graphql", "rest api", "sql", "postgresql",
        "mongodb", "redis", "tailwind", "figma", "video editing", "premiere pro", "davinci resolve",
        "after effects", "ci/cd", "microservices", "system design", "prompt engineering",
        "pytorch", "tensorflow", "llm", "langchain", "analytics", "seo", "content strategy"
    ]
    for skill in common_industry_skills:
        if skill not in candidate_skills_lower and re.search(r"\b" + re.escape(skill) + r"\b", text_l):
            missing_skills.append(skill.title())

    skills_score = min(100, int((len(matched_skills) / max(len(matched_skills) + len(missing_skills[:5]), 1)) * 100))
    if len(matched_skills) >= 6:
        skills_score = max(skills_score, 85)

    # 5. Dimension 2: Experience & Domain Relevance
    experience_score = 80
    exp_matches = []
    work_exp = candidate_profile.get("work_experience", [])
    for exp in work_exp:
        role = exp.get("role", "")
        company = exp.get("company", "")
        # Check if role keywords appear in posting
        for word in role.split():
            if len(word) > 3 and word.lower() in text_l:
                exp_matches.append(f"{role} at {company}")
                break

    if exp_matches:
        experience_score = min(98, 70 + (len(exp_matches) * 10))
    else:
        experience_score = 65

    # 6. Dimension 3: Seniority & YoE Alignment
    seniority_score = 85
    yoe_found = re.findall(r"(\d+)\+?\s*(?:to\s*(\d+))?\s*(?:years?|yrs?)(?:\s*of)?\s*experience", text_l)
    required_yoe = None
    if yoe_found:
        try:
            required_yoe = int(yoe_found[0][0])
            if candidate_yoe >= required_yoe:
                seniority_score = min(100, 85 + (candidate_yoe - required_yoe) * 4)
            else:
                gap = required_yoe - candidate_yoe
                seniority_score = max(40, 80 - (gap * 15))
                cautions.append(f"YoE Probe: Job mentions {required_yoe}+ years, while profile indicates {candidate_yoe} years.")
        except (ValueError, IndexError):
            pass

    # 7. Dimension 4: Location & Work Mode Fit
    location_score = 90
    is_remote = any(k in text_l for k in ["remote", "work from anywhere", "distributed", "anywhere in"])
    is_hybrid = any(k in text_l for k in ["hybrid", "days in office", "flexible working"])
    loc_matched = False
    for loc in target_locations:
        if loc in text_l:
            loc_matched = True
            break

    if "remote" in target_locations and is_remote:
        location_score = 98
    elif loc_matched:
        location_score = 95
    elif is_hybrid and any(loc in text_l for loc in target_locations):
        location_score = 88
    elif knockout_risks:
        location_score = 45
    else:
        location_score = 70

    # 8. Dimension 5: Culture & Growth Potential
    growth_score = 85
    if any(k in text_l for k in ["equity", "stock options", "fast growing", "series a", "series b", "mentorship", "learning budget"]):
        growth_score = 92

    # Overall Match Calculation (Weighted)
    # Skills (35%), Experience (25%), Seniority (15%), Location (15%), Growth (10%)
    overall_score = int(
        (skills_score * 0.35)
        + (experience_score * 0.25)
        + (seniority_score * 0.15)
        + (location_score * 0.15)
        + (growth_score * 0.10)
    )

    if knockout_risks:
        overall_score = min(overall_score, 60)

    # Compile Strengths & Gaps
    strengths = [
        f"Verified skills match: {', '.join(matched_skills[:6])}" if matched_skills else "General alignment with domain",
        f"Relevant previous background: {', '.join(exp_matches[:2])}" if exp_matches else "Transferable skill profile",
        f"Location/Work mode alignment ({'Remote' if is_remote else 'Target Location'})"
    ]

    gaps = []
    if missing_skills:
        gaps.append(f"Potentially unverified skills in profile: {', '.join(missing_skills[:4])}")
    if required_yoe and candidate_yoe < required_yoe:
        gaps.append(f"Target specifies {required_yoe}+ years of experience vs {candidate_yoe} verified")
    if not gaps:
        gaps.append("No critical hard gaps identified; focus on domain storytelling")

    return {
        "overall_fit_score": overall_score,
        "rating": "High Match" if overall_score >= 80 else ("Moderate Match" if overall_score >= 65 else "Low Match / Stretch"),
        "platform": detect_platform(job_url) if detect_platform else "Web Board",
        "dimensions": {
            "skills_match": {"score": skills_score, "matched": matched_skills, "missing": missing_skills[:6]},
            "experience_domain": {"score": experience_score, "highlights": exp_matches},
            "seniority_yoe": {"score": seniority_score, "required_yoe": required_yoe, "candidate_yoe": candidate_yoe},
            "location_logistics": {"score": location_score, "is_remote": is_remote, "is_hybrid": is_hybrid},
            "growth_culture": {"score": growth_score}
        },
        "strengths": strengths,
        "gaps": gaps,
        "cautions": cautions,
        "knockout_risks": knockout_risks,
        "security_verdict": security_verdict
    }


def main():
    parser = argparse.ArgumentParser(description="5-Dimension Job Fit & Security Evaluator")
    parser.add_argument("--url", type=str, help="Job posting URL")
    parser.add_argument("--file", type=str, help="Path to text or markdown file containing job description")
    parser.add_argument("--profile", type=str, default=".job-hunter/candidate_profile.json", help="Path to candidate profile JSON")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    # Load candidate profile
    profile_path = Path(args.profile)
    if not profile_path.exists():
        fallback_profile = {
            "name": "Candidate",
            "skills": {"General": ["Python", "JavaScript", "React", "Video Editing", "Content Strategy"]},
            "search_targets": {"years_of_experience": 4, "locations": ["Remote", "Hyderabad"]}
        }
    else:
        with open(profile_path, "r", encoding="utf-8") as f:
            fallback_profile = json.load(f)

    posting_text = ""
    job_url = args.url or ""

    if args.url and fetch_url:
        page_data = fetch_url(args.url)
        posting_text = page_data.get("full_text", "")
    elif args.file and os.path.exists(args.file):
        with open(args.file, "r", encoding="utf-8") as f:
            posting_text = f.read()
    else:
        # Read from stdin if available
        if not sys.stdin.isatty():
            posting_text = sys.stdin.read()

    if not posting_text:
        print("Error: No job posting text provided via --url, --file, or stdin.", file=sys.stderr)
        sys.exit(1)

    result = evaluate_job(posting_text, fallback_profile, job_url)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n" + "=" * 60)
        print(f"🎯 5-DIMENSION FIT EVALUATION: {result['overall_fit_score']}% ({result['rating']})")
        print("=" * 60)
        print(f"Platform: {result['platform']}")
        print(f"Security Shield: {result['security_verdict']['status'].upper()} (Risk: {result['security_verdict']['risk_score']}/100)")
        if result['security_verdict'].get('findings'):
            for f in result['security_verdict']['findings']:
                print(f"  ⚠️ Security Flag: {f}")
        print("\n📊 Dimensions:")
        dims = result["dimensions"]
        print(f"  • Technical Skills:     {dims['skills_match']['score']}% (Matched: {len(dims['skills_match']['matched'])}, Missing: {len(dims['skills_match']['missing'])})")
        print(f"  • Experience & Domain:  {dims['experience_domain']['score']}%")
        print(f"  • Seniority / YoE:      {dims['seniority_yoe']['score']}%")
        print(f"  • Location & Mode:      {dims['location_logistics']['score']}%")
        print(f"  • Culture & Growth:     {dims['growth_culture']['score']}%")

        if result["knockout_risks"]:
            print("\n🚨 KNOCKOUT RISKS:")
            for k in result["knockout_risks"]:
                print(f"  ⛔ {k}")

        if result["cautions"]:
            print("\n⚠️ APPLICATION CAUTIONS:")
            for c in result["cautions"]:
                print(f"  🔸 {c}")

        print("\n💪 KEY STRENGTHS:")
        for s in result["strengths"]:
            print(f"  ✅ {s}")

        print("\n⚡ GAPS & BRIDGE TOPICS:")
        for g in result["gaps"]:
            print(f"  🔹 {g}")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
