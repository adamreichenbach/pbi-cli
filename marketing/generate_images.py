"""
Generate 4K marketing PNG images for pbi-cli.

Each feature SVG already has the Vibe BI header baked in.
This script:
1. Reads each feature SVG as-is
2. Adds a footer with mina-saad.com/pbi-cli
3. Renders at 4K width (3840px) via Playwright
4. Saves as PNG to marketing/images/
"""

import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ASSETS_DIR = Path(__file__).parent.parent / "assets"
OUTPUT_DIR = Path(__file__).parent / "images"
TARGET_WIDTH = 3840  # 4K width

# Feature SVGs to process (filename -> output name)
FEATURE_SVGS = {
    "before-after.svg": "before-after",
    "architecture-flow.svg": "architecture-flow",
    "backup-restore.svg": "backup-restore",
    "bulk-operations.svg": "bulk-operations",
    "chat-demo.svg": "chat-demo",
    "dax-debugging.svg": "dax-debugging",
    "feature-grid.svg": "feature-grid",
    "model-health-check.svg": "model-health-check",
    "rls-testing.svg": "rls-testing",
    "skills-hub.svg": "skills-hub",
    "token-cost.svg": "token-cost",
    "how-it-works.svg": "how-it-works",
    "dax-skill.svg": "dax-skill",
    "modeling-skill.svg": "modeling-skill",
    "deploy-secure.svg": "deploy-secure",
    "docs-diagnostics.svg": "docs-diagnostics",
    "cta-start.svg": "cta-start",
    # Report layer (v3)
    "report-layer.svg": "report-layer",
    "dual-layer.svg": "dual-layer",
    "visual-types.svg": "visual-types",
    "report-workflow.svg": "report-workflow",
    "auto-sync.svg": "auto-sync",
    "chat-demo-report.svg": "chat-demo-report",
    # Additional assets
    "commands.svg": "commands",
    "layers.svg": "layers",
    "release-vibe-bi.svg": "release-vibe-bi",
    "stats.svg": "stats",
    "workflow.svg": "workflow",
}

FOOTER_HEIGHT = 60
SVG_WIDTH = 850


def read_svg_content(filepath: Path) -> str:
    return filepath.read_text(encoding="utf-8")


def get_svg_height(svg_text: str) -> int:
    """Extract height from SVG viewBox or height attribute."""
    match = re.search(r'viewBox="0 0 \d+ (\d+)"', svg_text)
    if match:
        return int(match.group(1))
    match = re.search(r'height="(\d+)"', svg_text)
    if match:
        return int(match.group(1))
    return 400


def extract_svg_inner(svg_text: str) -> str:
    """Extract everything between <svg ...> and </svg> tags."""
    inner = re.sub(r"<\?xml[^>]*\?>\s*", "", svg_text)
    inner = re.sub(r"<svg[^>]*>", "", inner, count=1)
    inner = re.sub(r"</svg>\s*$", "", inner)
    return inner


def extract_defs(svg_text: str) -> str:
    """Extract <defs>...</defs> block if present."""
    match = re.search(r"<defs>.*?</defs>", svg_text, re.DOTALL)
    return match.group(0) if match else ""


def build_final_svg(feature_svg: str, feature_height: int) -> str:
    """Build final SVG: feature content (with baked header) + footer."""
    total_height = feature_height + FOOTER_HEIGHT

    feature_inner = extract_svg_inner(feature_svg)
    feature_defs = extract_defs(feature_svg)
    # Remove defs from inner since we place them at top level
    feature_inner_clean = re.sub(
        r"<defs>.*?</defs>", "", feature_inner, flags=re.DOTALL
    )

    defs_block = ""
    if feature_defs:
        defs_content = re.search(
            r"<defs>(.*?)</defs>", feature_defs, re.DOTALL
        )
        if defs_content:
            defs_block = f"  <defs>{defs_content.group(1)}</defs>"

    footer_y = feature_height + 40

    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{SVG_WIDTH}" height="{total_height}" viewBox="0 0 {SVG_WIDTH} {total_height}">
{defs_block}

  <!-- Full background -->
  <rect width="100%" height="100%" fill="#0d1117"/>

  <!-- Feature section (header already baked in) -->
  <svg x="0" y="0" width="{SVG_WIDTH}" height="{feature_height}" viewBox="0 0 {SVG_WIDTH} {feature_height}">
{feature_inner_clean}
  </svg>

  <!-- Footer -->
  <rect x="0" y="{feature_height}" width="{SVG_WIDTH}" height="{FOOTER_HEIGHT}" fill="#0d1117"/>
  <line x1="60" y1="{feature_height + 8}" x2="790" y2="{feature_height + 8}" stroke="#F2C811" stroke-opacity="0.25" stroke-width="2"/>
  <text x="425" y="{footer_y}" font-family="'Segoe UI', Arial, sans-serif" font-size="18" fill="#58a6ff" text-anchor="middle" font-weight="bold">mina-saad.com/pbi-cli</text>
</svg>"""


def render_svg_to_png(svg_content: str, output_path: Path, page) -> None:
    """Render an SVG string to a 4K PNG using Playwright."""
    match = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg_content)
    svg_w, svg_h = int(match.group(1)), int(match.group(2))

    scale = TARGET_WIDTH / svg_w
    target_h = int(svg_h * scale)

    html = f"""<!DOCTYPE html>
<html>
<head>
<style>
  * {{ margin: 0; padding: 0; }}
  body {{ background: #0d1117; width: {TARGET_WIDTH}px; height: {target_h}px; overflow: hidden; }}
  svg {{ display: block; width: {TARGET_WIDTH}px; height: {target_h}px; }}
</style>
</head>
<body>
{svg_content}
</body>
</html>"""

    page.set_viewport_size({"width": TARGET_WIDTH, "height": target_h})
    page.set_content(html, wait_until="networkidle")
    page.screenshot(path=str(output_path), full_page=True, type="png")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for svg_file, output_name in FEATURE_SVGS.items():
            svg_path = ASSETS_DIR / svg_file
            if not svg_path.exists():
                print(f"  SKIP {svg_file} (not found)")
                continue

            feature_svg = read_svg_content(svg_path)
            feature_height = get_svg_height(feature_svg)

            composite = build_final_svg(feature_svg, feature_height)

            output_path = OUTPUT_DIR / f"{output_name}.png"
            render_svg_to_png(composite, output_path, page)

            total_h = feature_height + FOOTER_HEIGHT
            scale = TARGET_WIDTH / SVG_WIDTH
            print(
                f"  OK {output_name}.png "
                f"({TARGET_WIDTH}x{int(total_h * scale)})"
            )

        browser.close()

    print(f"\nDone! {len(FEATURE_SVGS)} images saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
