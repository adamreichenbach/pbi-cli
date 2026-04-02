"""Skill triggering evaluation -- verify prompts match expected skills.

This is NOT a pytest test. Run directly:
    python tests/test_skill_triggering.py

Uses keyword-based scoring to simulate which skill description best matches
each user prompt, without requiring an LLM call.
"""

from __future__ import annotations

import importlib.resources
import re

import yaml


def _load_skills() -> dict[str, str]:
    """Load all skill names and descriptions from bundled skills."""
    skills_pkg = importlib.resources.files("pbi_cli.skills")
    skills: dict[str, str] = {}
    for item in skills_pkg.iterdir():
        if item.is_dir() and (item / "SKILL.md").is_file():
            content = (item / "SKILL.md").read_text(encoding="utf-8")
            match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            if match:
                fm = yaml.safe_load(match.group(1))
                skills[item.name] = fm.get("description", "").lower()
    return skills


def _score_prompt(prompt: str, description: str) -> int:
    """Score how well a prompt matches a skill description using word overlap."""
    prompt_words = set(re.findall(r"[a-z]+", prompt.lower()))
    desc_words = set(re.findall(r"[a-z]+", description))
    # Weight longer matching words higher (domain terms matter more)
    score = 0
    for word in prompt_words & desc_words:
        if len(word) >= 5:
            score += 3
        elif len(word) >= 3:
            score += 1
    return score


def _find_best_skill(prompt: str, skills: dict[str, str]) -> str:
    """Find the skill with the highest keyword overlap score."""
    scores = {name: _score_prompt(prompt, desc) for name, desc in skills.items()}
    return max(scores, key=lambda k: scores[k])


# Test cases: (prompt, expected_skill)
TEST_CASES: list[tuple[str, str]] = [
    # power-bi-visuals
    ("Add a bar chart to the overview page showing sales by region", "power-bi-visuals"),
    ("I need to bind Sales[Revenue] to the value field on my KPI visual", "power-bi-visuals"),
    ("What visual types does pbi-cli support? I need a scatter plot", "power-bi-visuals"),
    ("Resize all the card visuals on the dashboard page to 200x120", "power-bi-visuals"),
    # power-bi-pages
    ("Add a new page called Regional Detail to my report", "power-bi-pages"),
    ("Hide the drillthrough page from the navigation bar", "power-bi-pages"),
    ("Create a bookmark for the current executive view", "power-bi-pages"),
    # power-bi-themes
    ("Apply our corporate brand colours to the entire report", "power-bi-themes"),
    (
        "I want conditional formatting on the revenue column green for high red for low",
        "power-bi-themes",
    ),
    ("Compare this new theme JSON against what is currently applied", "power-bi-themes"),
    # power-bi-filters
    ("Filter the overview page to show only the top 10 products by revenue", "power-bi-filters"),
    ("Add a date filter for the last 30 days on the Sales page", "power-bi-filters"),
    ("What filters are currently on my dashboard page", "power-bi-filters"),
    # power-bi-report
    ("Create a new PBIR report project for our sales dashboard", "power-bi-report"),
    ("Validate the report structure to make sure everything is correct", "power-bi-report"),
    ("Start the preview server so I can see the layout", "power-bi-report"),
    # Should NOT trigger report skills
    ("Create a measure called Total Revenue equals SUM of Sales Amount", "power-bi-modeling"),
    ("Export the semantic model to TMDL for version control", "power-bi-deployment"),
    ("Set up row-level security for regional managers", "power-bi-security"),
]


def main() -> None:
    skills = _load_skills()
    passed = 0
    failed = 0

    print(f"Testing {len(TEST_CASES)} prompts against {len(skills)} skills\n")
    print(f"{'#':<3} {'Result':<6} {'Expected':<22} {'Got':<22} Prompt")
    print("-" * 100)

    for i, (prompt, expected) in enumerate(TEST_CASES, 1):
        got = _find_best_skill(prompt, skills)
        ok = got == expected
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
        short_prompt = prompt[:45] + "..." if len(prompt) > 45 else prompt
        print(f"{i:<3} {status:<6} {expected:<22} {got:<22} {short_prompt}")

    print(f"\n{passed}/{len(TEST_CASES)} passed, {failed} failed")


if __name__ == "__main__":
    main()
