"""
Bake the Vibe BI header into each feature SVG in assets/.

For each feature SVG:
1. Inject the VIBE BI branding header (ASCII art, connection flow, install cmd)
2. Shift original content down by HEADER_HEIGHT
3. Write the updated SVG back to disk

Logos are referenced via <image> to preserve original dimensions.
"""

import re
import sys
from pathlib import Path

ASSETS_DIR = Path(__file__).parent.parent / "assets"
HEADER_HEIGHT = 210
SVG_WIDTH = 850

# Feature SVGs to process (same list as generate_images.py)
FEATURE_SVGS = [
    "before-after.svg",
    "architecture-flow.svg",
    "backup-restore.svg",
    "bulk-operations.svg",
    "chat-demo.svg",
    "dax-debugging.svg",
    "feature-grid.svg",
    "model-health-check.svg",
    "rls-testing.svg",
    "skills-hub.svg",
    "token-cost.svg",
    "how-it-works.svg",
    "dax-skill.svg",
    "modeling-skill.svg",
    "deploy-secure.svg",
    "docs-diagnostics.svg",
    "cta-start.svg",
    "report-layer.svg",
    "dual-layer.svg",
    "visual-types.svg",
    "report-workflow.svg",
    "auto-sync.svg",
    "chat-demo-report.svg",
    "commands.svg",
    "layers.svg",
    "release-vibe-bi.svg",
    "stats.svg",
    "workflow.svg",
]

# The Vibe BI header SVG fragment (210px tall, 850px wide)
HEADER_DEFS = """\
    <linearGradient id="hdr-bar1" x1="50%" y1="0%" x2="50%" y2="100%">
      <stop offset="0%" stop-color="#EBBB14"/>
      <stop offset="100%" stop-color="#B25400"/>
    </linearGradient>
    <linearGradient id="hdr-bar2" x1="50%" y1="0%" x2="50%" y2="100%">
      <stop offset="0%" stop-color="#F9E583"/>
      <stop offset="100%" stop-color="#DE9800"/>
    </linearGradient>
    <linearGradient id="hdr-bar3" x1="50%" y1="0%" x2="50%" y2="100%">
      <stop offset="0%" stop-color="#F9E68B"/>
      <stop offset="100%" stop-color="#F3CD32"/>
    </linearGradient>
    <linearGradient id="pbi-lg1" x1="50%" y1="0%" x2="50%" y2="100%">
      <stop offset="0%" stop-color="#EBBB14"/>
      <stop offset="100%" stop-color="#B25400"/>
    </linearGradient>
    <linearGradient id="pbi-lg2" x1="50%" y1="0%" x2="50%" y2="100%">
      <stop offset="0%" stop-color="#F9E583"/>
      <stop offset="100%" stop-color="#DE9800"/>
    </linearGradient>
    <linearGradient id="pbi-lg5" x1="50%" y1="0%" x2="50%" y2="100%">
      <stop offset="0%" stop-color="#F9E68B"/>
      <stop offset="100%" stop-color="#F3CD32"/>
    </linearGradient>"""

HEADER_BODY = """\
  <!-- ==================== VIBE BI HEADER ==================== -->

  <!-- "VIBE BI" block art (shadow) -->
  <text font-family="'Courier New', Courier, monospace" font-size="9" fill="#7A6508" xml:space="preserve">
    <tspan x="296" y="22">██╗   ██╗ ██╗ ██████╗  ███████╗     ██████╗  ██╗</tspan>
    <tspan x="296" y="33">██║   ██║ ██║ ██╔══██╗ ██╔════╝     ██╔══██╗ ██║</tspan>
    <tspan x="296" y="44">██║   ██║ ██║ ██████╔╝ █████╗       ██████╔╝ ██║</tspan>
    <tspan x="296" y="55">╚██╗ ██╔╝ ██║ ██╔══██╗ ██╔══╝       ██╔══██╗ ██║</tspan>
    <tspan x="296" y="66"> ╚████╔╝  ██║ ██████╔╝ ███████╗     ██████╔╝ ██║</tspan>
    <tspan x="296" y="77">  ╚═══╝   ╚═╝ ╚═════╝  ╚══════╝     ╚═════╝  ╚═╝</tspan>
  </text>
  <!-- "VIBE BI" block art (main) -->
  <text font-family="'Courier New', Courier, monospace" font-size="9" fill="#F2C811" xml:space="preserve">
    <tspan x="295" y="21">██╗   ██╗ ██╗ ██████╗  ███████╗     ██████╗  ██╗</tspan>
    <tspan x="295" y="32">██║   ██║ ██║ ██╔══██╗ ██╔════╝     ██╔══██╗ ██║</tspan>
    <tspan x="295" y="43">██║   ██║ ██║ ██████╔╝ █████╗       ██████╔╝ ██║</tspan>
    <tspan x="295" y="54">╚██╗ ██╔╝ ██║ ██╔══██╗ ██╔══╝       ██╔══██╗ ██║</tspan>
    <tspan x="295" y="65"> ╚████╔╝  ██║ ██████╔╝ ███████╗     ██████╔╝ ██║</tspan>
    <tspan x="295" y="76">  ╚═══╝   ╚═╝ ╚═════╝  ╚══════╝     ╚═════╝  ╚═╝</tspan>
  </text>

  <!-- Separator -->
  <line x1="60" y1="84" x2="790" y2="84" stroke="#F2C811" stroke-opacity="0.15" stroke-width="1"/>

  <!-- Tagline -->
  <text x="425" y="100" font-family="'Segoe UI', Arial, sans-serif" font-size="13" fill="#e6edf3" text-anchor="middle" font-weight="600">The First CLI for Both Power BI Modeling and Reporting</text>

  <!-- ===== Connection Flow: Claude > PBI-CLI > Power BI ===== -->

  <!-- Claude AI logo (inline, original 1200x1200, displayed as 50x50, centered at x=110) -->
  <svg x="85" y="110" width="50" height="50" viewBox="0 0 1200 1200">
    <path fill="#d97757" d="M 233.959793 800.214905 L 468.644287 668.536987 L 472.590637 657.100647 L 468.644287 650.738403 L 457.208069 650.738403 L 417.986633 648.322144 L 283.892639 644.69812 L 167.597321 639.865845 L 54.926208 633.825623 L 26.577238 627.785339 L 3.3e-05 592.751709 L 2.73832 575.27533 L 26.577238 559.248352 L 60.724873 562.228149 L 136.187973 567.382629 L 249.422867 575.194763 L 331.570496 580.026978 L 453.261841 592.671082 L 472.590637 592.671082 L 475.328857 584.859009 L 468.724915 580.026978 L 463.570557 575.194763 L 346.389313 495.785217 L 219.543671 411.865906 L 153.100723 363.543762 L 117.181267 339.060425 L 99.060455 316.107361 L 91.248367 266.01355 L 123.865784 230.093994 L 167.677887 233.073853 L 178.872513 236.053772 L 223.248367 270.201477 L 318.040283 343.570496 L 441.825592 434.738342 L 459.946411 449.798706 L 467.194672 444.64447 L 468.080597 441.020203 L 459.946411 427.409485 L 392.617493 305.718323 L 320.778564 181.932983 L 288.80542 130.630859 L 280.348999 99.865845 C 277.369171 87.221436 275.194641 76.590698 275.194641 63.624268 L 312.322174 13.20813 L 332.8591 6.604126 L 382.389313 13.20813 L 403.248352 31.328979 L 434.013519 101.71814 L 483.865753 212.537048 L 561.181274 363.221497 L 583.812134 407.919434 L 595.892639 449.315491 L 600.40271 461.959839 L 608.214783 461.959839 L 608.214783 454.711609 L 614.577271 369.825623 L 626.335632 265.61084 L 637.771851 131.516846 L 641.718201 93.745117 L 660.402832 48.483276 L 697.530334 24.000122 L 726.52356 37.852417 L 750.362549 72 L 747.060486 94.067139 L 732.886047 186.201416 L 705.100708 330.52356 L 686.979919 427.167847 L 697.530334 427.167847 L 709.61084 415.087341 L 758.496704 350.174561 L 840.644348 247.490051 L 876.885925 206.738342 L 919.167847 161.71814 L 946.308838 140.29541 L 997.61084 140.29541 L 1035.38269 196.429626 L 1018.469849 254.416199 L 965.637634 321.422852 L 921.825562 378.201538 L 859.006714 462.765259 L 819.785278 530.41626 L 823.409424 535.812073 L 832.75177 534.92627 L 974.657776 504.724915 L 1051.328979 490.872559 L 1142.818848 475.167786 L 1184.214844 494.496582 L 1188.724854 514.147644 L 1172.456421 554.335693 L 1074.604126 578.496765 L 959.838989 601.449829 L 788.939636 641.879272 L 786.845764 643.409485 L 789.261841 646.389343 L 866.255127 653.637634 L 899.194702 655.409424 L 979.812134 655.409424 L 1129.932861 666.604187 L 1169.154419 692.537109 L 1192.671265 724.268677 L 1188.724854 748.429688 L 1128.322144 779.194641 L 1046.818848 759.865845 L 856.590759 714.604126 L 791.355774 698.335754 L 782.335693 698.335754 L 782.335693 703.731567 L 836.69812 756.885986 L 936.322205 846.845581 L 1061.073975 962.81897 L 1067.436279 991.490112 L 1051.409424 1014.120911 L 1034.496704 1011.704712 L 924.885986 929.234924 L 882.604126 892.107544 L 786.845764 811.48999 L 780.483276 811.48999 L 780.483276 819.946289 L 802.550415 852.241699 L 919.087341 1027.409424 L 925.127625 1081.127686 L 916.671204 1098.604126 L 886.469849 1109.154419 L 853.288696 1103.114136 L 785.073914 1007.355835 L 714.684631 899.516785 L 657.906067 802.872498 L 650.979858 806.81897 L 617.476624 1167.704834 L 601.771851 1186.147705 L 565.530212 1200 L 535.328857 1177.046997 L 519.302124 1139.919556 L 535.328857 1066.550537 L 554.657776 970.792053 L 570.362488 894.68457 L 584.536926 800.134277 L 592.993347 768.724976 L 592.429626 766.630859 L 585.503479 767.516968 L 514.22821 865.369263 L 405.825531 1011.865906 L 320.053711 1103.677979 L 299.516815 1111.812256 L 263.919525 1093.369263 L 267.221497 1060.429688 L 287.114136 1031.114136 L 405.825531 880.107361 L 477.422913 786.52356 L 523.651062 732.483276 L 523.328918 724.671265 L 520.590698 724.671265 L 205.288605 929.395935 L 149.154434 936.644409 L 124.993355 914.01355 L 127.973183 876.885986 L 139.409409 864.80542 L 234.201385 799.570435 L 233.879227 799.8927 Z"/>
  </svg>
  <text x="110" y="175" font-family="'Segoe UI', Arial, sans-serif" font-size="11" fill="#d97757" text-anchor="middle" font-weight="600">Claude Code</text>

  <!-- Left arrow -->
  <line x1="155" y1="135" x2="290" y2="135" stroke="#F2C811" stroke-width="2" stroke-dasharray="6,4" stroke-opacity="0.5"/>
  <polygon points="294,135 286,130 286,140" fill="#F2C811" fill-opacity="0.5"/>

  <!-- PBI-CLI block art (shadow) -->
  <text font-family="'Courier New', Courier, monospace" font-size="7" fill="#7A6508" xml:space="preserve">
    <tspan x="316" y="118">██████╗  ██████╗  ██╗         ██████╗ ██╗      ██╗</tspan>
    <tspan x="316" y="128">██╔══██╗ ██╔══██╗ ██║        ██╔════╝ ██║      ██║</tspan>
    <tspan x="316" y="138">██████╔╝ ██████╔╝ ██║  ███╗  ██║      ██║      ██║</tspan>
    <tspan x="316" y="148">██╔═══╝  ██╔══██╗ ██║  ╚══╝  ██║      ██║      ██║</tspan>
    <tspan x="316" y="158">██║      ██████╔╝ ██║        ╚██████╗ ███████╗ ██║</tspan>
    <tspan x="316" y="168">╚═╝      ╚═════╝  ╚═╝         ╚═════╝ ╚══════╝ ╚═╝</tspan>
  </text>
  <!-- PBI-CLI block art (main) -->
  <text font-family="'Courier New', Courier, monospace" font-size="7" fill="#F2C811" xml:space="preserve">
    <tspan x="315" y="117">██████╗  ██████╗  ██╗         ██████╗ ██╗      ██╗</tspan>
    <tspan x="315" y="127">██╔══██╗ ██╔══██╗ ██║        ██╔════╝ ██║      ██║</tspan>
    <tspan x="315" y="137">██████╔╝ ██████╔╝ ██║  ███╗  ██║      ██║      ██║</tspan>
    <tspan x="315" y="147">██╔═══╝  ██╔══██╗ ██║  ╚══╝  ██║      ██║      ██║</tspan>
    <tspan x="315" y="157">██║      ██████╔╝ ██║        ╚██████╗ ███████╗ ██║</tspan>
    <tspan x="315" y="167">╚═╝      ╚═════╝  ╚═╝         ╚═════╝ ╚══════╝ ╚═╝</tspan>
  </text>

  <!-- Right arrow -->
  <line x1="560" y1="135" x2="655" y2="135" stroke="#F2C811" stroke-width="2" stroke-dasharray="6,4" stroke-opacity="0.5"/>
  <polygon points="659,135 651,130 651,140" fill="#F2C811" fill-opacity="0.5"/>

  <!-- Power BI logo (inline, original 630x630, displayed as 50x50, centered at x=700) -->
  <svg x="675" y="110" width="50" height="50" viewBox="0 0 630 630">
    <g transform="translate(77.5, 0)">
      <rect fill="url(#pbi-lg1)" x="256" y="0" width="219" height="630" rx="26"/>
      <path fill="url(#pbi-lg2)" d="M346,604 L346,630 L320,630 L153,630 C138.64,630 127,618.36 127,604 L127,183 C127,168.64 138.64,157 153,157 L320,157 C334.36,157 346,168.64 346,183 L346,604 Z"/>
      <path fill="url(#pbi-lg5)" d="M219,604 L219,630 L193,630 L26,630 C11.64,630 0,618.36 0,604 L0,341 C0,326.64 11.64,315 26,315 L193,315 C207.36,315 219,326.64 219,341 L219,604 Z"/>
    </g>
  </svg>
  <text x="700" y="175" font-family="'Segoe UI', Arial, sans-serif" font-size="11" fill="#F2C811" text-anchor="middle" font-weight="600">Power BI</text>

  <!-- Modeling + Reporting pills -->
  <rect x="308" y="176" width="100" height="20" rx="10" fill="#58a6ff" fill-opacity="0.1" stroke="#58a6ff" stroke-width="1"/>
  <text x="358" y="190" font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#58a6ff" text-anchor="middle" font-weight="600">Modeling</text>
  <text x="420" y="190" font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#8b949e" text-anchor="middle">+</text>
  <rect x="432" y="176" width="100" height="20" rx="10" fill="#06d6a0" fill-opacity="0.1" stroke="#06d6a0" stroke-width="1"/>
  <text x="482" y="190" font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#06d6a0" text-anchor="middle" font-weight="600">Reporting</text>

  <!-- Bottom separator -->
  <line x1="60" y1="200" x2="790" y2="200" stroke="#F2C811" stroke-opacity="0.25" stroke-width="2"/>

  <!-- ==================== END HEADER ==================== -->"""


def get_svg_height(svg_text: str) -> int:
    """Extract height from SVG viewBox (expects '0 0 W H' format)."""
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


def extract_defs_content(svg_text: str) -> str:
    """Extract the content inside <defs>...</defs> if present."""
    match = re.search(r"<defs>(.*?)</defs>", svg_text, re.DOTALL)
    return match.group(1) if match else ""


def remove_bg_rect(svg_inner: str) -> str:
    """Remove the first background rect (fill='#0d1117') from the SVG inner content."""
    return re.sub(
        r'\s*<rect[^>]*fill="#0d1117"[^/]*/>\s*',
        "\n",
        svg_inner,
        count=1,
    )


def remove_defs_block(svg_inner: str) -> str:
    """Remove the <defs>...</defs> block from SVG inner content."""
    return re.sub(r"\s*<defs>.*?</defs>\s*", "\n", svg_inner, flags=re.DOTALL)


def is_already_baked(svg_text: str) -> bool:
    """Check if the SVG already contains the Vibe BI header."""
    return "VIBE BI HEADER" in svg_text


def unbake_header(svg_text: str) -> str:
    """Strip the baked header and reconstruct the original feature SVG."""
    # Extract the feature content from inside <g transform="translate(0, 210)">...</g>
    match = re.search(
        r'<g transform="translate\(0, 210\)">\s*(.*?)\s*</g>\s*</svg>',
        svg_text,
        re.DOTALL,
    )
    if not match:
        return svg_text

    feature_inner = match.group(1)
    original_height = get_svg_height(svg_text) - HEADER_HEIGHT

    # Extract feature-specific defs (skip header gradient defs)
    all_defs = extract_defs_content(svg_text)
    # Remove header-specific defs (hdr-bar* and pbi-lg*)
    feature_defs = re.sub(
        r'\s*<linearGradient id="(hdr-bar|pbi-lg)[^"]*"[^>]*>.*?</linearGradient>',
        "",
        all_defs,
        flags=re.DOTALL,
    )
    feature_defs = feature_defs.strip()

    defs_block = ""
    if feature_defs:
        defs_block = f"\n  <defs>\n{feature_defs}\n  </defs>\n"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{original_height}" viewBox="0 0 {SVG_WIDTH} {original_height}">
{defs_block}
  <rect width="100%" height="100%" fill="#0d1117" rx="8"/>
{feature_inner}
</svg>"""


def bake_header(svg_text: str) -> str:
    """Inject the Vibe BI header into a feature SVG."""
    original_height = get_svg_height(svg_text)
    new_height = original_height + HEADER_HEIGHT

    # Extract parts
    feature_inner = extract_svg_inner(svg_text)
    feature_defs = extract_defs_content(svg_text)

    # Clean feature inner: remove defs block and background rect
    clean_inner = remove_defs_block(feature_inner)
    clean_inner = remove_bg_rect(clean_inner)

    # Merge defs
    all_defs = HEADER_DEFS
    if feature_defs.strip():
        all_defs += "\n" + feature_defs

    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{SVG_WIDTH}" height="{new_height}" viewBox="0 0 {SVG_WIDTH} {new_height}">
  <defs>
{all_defs}
  </defs>

  <!-- Full background -->
  <rect width="100%" height="100%" fill="#0d1117"/>

{HEADER_BODY}

  <!-- Feature content (shifted down by {HEADER_HEIGHT}px) -->
  <g transform="translate(0, {HEADER_HEIGHT})">
{clean_inner}
  </g>
</svg>"""


def process_file(svg_file: str, dry_run: bool = False, force: bool = False) -> None:
    """Process a single feature SVG file."""
    filepath = ASSETS_DIR / svg_file
    if not filepath.exists():
        print(f"  SKIP {svg_file} (not found)")
        return

    svg_text = filepath.read_text(encoding="utf-8")

    if is_already_baked(svg_text):
        if force:
            svg_text = unbake_header(svg_text)
            print(f"  STRIP {svg_file} (removed old header)")
        else:
            print(f"  SKIP {svg_file} (already has header, use --force)")
            return

    original_height = get_svg_height(svg_text)

    result = bake_header(svg_text)
    new_height = original_height + HEADER_HEIGHT

    if dry_run:
        print(f"  DRY  {svg_file}: {original_height} -> {new_height}px")
    else:
        filepath.write_text(result, encoding="utf-8")
        print(f"  OK   {svg_file}: {original_height} -> {new_height}px")


def main():
    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv
    targets = sys.argv[1:]
    targets = [t for t in targets if not t.startswith("--")]

    if not targets:
        targets = FEATURE_SVGS

    mode = "DRY RUN" if dry_run else ("FORCE REBAKE" if force else "BAKING")
    print(f"\n{mode}: Injecting Vibe BI header into {len(targets)} SVGs\n")

    for svg_file in targets:
        process_file(svg_file, dry_run=dry_run, force=force)

    print(f"\nDone! Processed {len(targets)} files.")


if __name__ == "__main__":
    main()
