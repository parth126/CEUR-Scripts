#!/usr/bin/env python3
"""
generate_base_index.py

Author: Parth Mehta
GitHub: https://github.com/parth126
License: MIT

Description:
Fetches index template from https://ceur-ws.org/Vol-XXX/index.html and creates a conference specific base-index
"""

__author__ = "Parth Mehta"
__copyright__ = "Copyright 2025, Parth Mehta"
__license__ = "MIT" 

import os
import re
import yaml
import requests
import argparse

def create_base_template(base_folder):
    # Load configuration
    with open(os.path.join(base_folder, "conference-info.yaml"), 'r') as f:
        config = yaml.safe_load(f)
    
    # Load your specific editor info snippet
    editor_html = generate_editor_html(config)

    # Fetch official CEUR-WS template
    url = "https://ceur-ws.org/Vol-XXX/index.html"
    print(f"Fetching official template from {url}...")
    html = requests.get(url).text

    # 1. STRIP ALL COMMENTS AND INSTRUCTIONS FIRST
    # This prevents unclosed ", "", html, flags=re.DOTALL)
    html = re.sub(r"<pre>#.*?</pre>", "", html, flags=re.DOTALL)

    # 2. METADATA REPLACEMENTS
    html = html.replace("Proceedings of the Workshop on Publishing Papers with CEUR-WS", config['volume_title_long'])
    html = html.replace("Publishing Papers with CEUR-WS YYYY", config['volume_title_short'])
    html = html.replace("NNNN", config['acronym'])
    
    # Replace year placeholders (JJJJ/YYYY)
    html = html.replace("JJJJ", str(config['year']))
    html = html.replace("YYYY", str(config['year']))

    # 3. LOCATION AND DATE LINE
    # Replaces: "Aachen, Germany, October 21-22, YYYY" with your full details
    loc_pattern = r"(Aachen, Germany, October 21-22|City, Country, Month Day), (2019|YYYY|JJJJ|\d{4})"
    new_loc = f"{config['city']}, {config['country']}, {config['month']} {config['start_date']}-{config['end_date']}, {config['year']}"
    html = re.sub(loc_pattern, new_loc, html)

    # 4. REMOVE CO-LOCATION LINE (robust)
    # Remove both the optional comment and the visible "co-located with ..." line (including trailing <br>)
    coloc_pattern = r"(?is)\s*<!--\s*co-located with.*?-->\s*co-located with.*?<br\s*/?>\s*"

    if config.get("colocation"):
        # If you ever DO want it, insert a clean line (optional)
        html = re.sub(coloc_pattern, f'<br>\nco-located with {config["colocation"]}<br>\n', html)
    else:
        html = re.sub(coloc_pattern, "", html)

    # 5. REMOVE SAMPLE EDITORS AND INSERT YOURS
    # This specifically targets the Mary Editor/Peter Coeditor block and its affiliations.
    # We replace everything between 'Edited by' and the next section.
    editor_clean_pattern = r"(<b>\s*Edited by\s*</b>\s*<p>).*?(<hr>)"
    new_editor_block = f"\\1\n{editor_html}\n<br>\n\\2"
    html = re.sub(editor_clean_pattern, new_editor_block, html, flags=re.DOTALL)

    # 6. SANITIZE TABLE OF CONTENTS
    # Wipes all Session examples and dummy papers.
    toc_div_pattern = r"(<div class=\"CEURTOC\">\s*<h2> Table of Contents </h2>).*?(</div>)"
    toc_replacement = r"\1\n\nXXXTOCPLACEHOLDERXXX\n\n\2"
    html = re.sub(toc_div_pattern, toc_replacement, html, flags=re.DOTALL)

    # 7. SUBMISSION METADATA (FOOTER)
    # Targets: "2019-MM-DD: submitted by Peter Coeditor" or "YYYY-MM-DD..."
    footer_sub_pattern = r"(\d{4}|YYYY)-MM-DD: submitted by Peter Coeditor"
    new_footer = f"{config['submission_date']}: submitted by {config['submitted_by']}"
    html = re.sub(footer_sub_pattern, new_footer, html)

    # Final cleanup of any lingering template names
    html = html.replace("Mary Editor", "").replace("Peter Coeditor", "")
    # Remove excessive blank lines
    html = re.sub(r'\n\s*\n', '\n\n', html)

    # Save the base-index.html
    output_path = os.path.join(base_folder, "base-index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"Clean base-index.html generated at: {output_path}")


def generate_editor_html(config):
    """Generates the CEUR editor HTML block from YAML data."""
    editors = config.get('editors', [])
    affiliations = config.get('affiliations', [])
    
    html = ["<h3>"]
    # Build the list of editors with asterisks
    for ed in editors:
        # Create asterisk string (0 -> *, 1 -> **, etc.)
        stars = "*" * (ed['affiliation_index'] + 1)
        html.append(
            f'   <a href="{ed["link"]}" target="_blank">'
            f'<span class="CEURVOLEDITOR">{ed["name"]}</span></a> {stars}<br>'
        )
    html.append("</h3>\n")
    
    # Build the affiliation key below
    for i, aff in enumerate(affiliations):
        stars = "*" * (i + 1)
        html.append(
            f'{stars} <a href="{aff["link"]}" target="_blank">{aff["name"]}</a>, '
            f'{aff["city"]}, {aff["country"]}<br>'
        )
    
    html.append("  <br>")
    return "\n".join(html)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--base", default="sample", help="Folder containing input files")
    args = parser.parse_args()
    create_base_template(args.base)
