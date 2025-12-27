#!/usr/bin/env python3
"""
generate_proceedings.py

Author: Parth Mehta
GitHub: https://github.com/parth126
License: MIT

Description:
This script assembles the final volume, processes PDFs, and generates the TOC.
"""

__author__ = "Parth Mehta"
__copyright__ = "Copyright 2025, Parth Mehta"
__license__ = "MIT" 


import os
import yaml
import shutil
import argparse
from pypdf import PdfReader

def get_pdf_page_count(filepath):
    """Calculates page count of a PDF file using pypdf."""
    try:
        reader = PdfReader(filepath)
        return len(reader.pages)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return 0

def generate_proceedings(base_folder, output_folder):
    # 1. Load Configuration
    with open(os.path.join(base_folder, "conference-info.yaml"), 'r') as f:
        config = yaml.safe_load(f)
    
    # Create the output directory (e.g., FIRE2019)
    dir_name = output_folder if output_folder else config["acronym"].replace(" ", "")+config['year'].replace(" ", "")

    os.makedirs(dir_name, exist_ok=True)
    print(f"Creating volume in directory: {dir_name}")

    # 2. Read the base-index.html (the template you just finalized)
    template_path = os.path.join(base_folder, 'base-index.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 3. Process working-notes.info
    info_path = os.path.join(base_folder, 'working-notes-info.csv')
    with open(info_path, 'r') as f:
        # Skip header, read all lines
        all_info = [line.strip() for line in f if line.strip()][1:]

    # 4. Process Preface (First line after header)
    preface_parts = all_info[0].split(',')
    preface_title = preface_parts[1]
    preface_authors = [a for a in preface_parts[2:] if a]

    ###---- Disabled in 2025 because CEUR now needs a summary ----###

    #toc_lines = ["<ul>"]
    #toc_lines.append(f'  <li id="{preface_title}"><a href="{preface_title}.pdf">')
    #toc_lines.append('  <span class="CEURTITLE">Preface</span></a>')
    #toc_lines.append('  <br>')
    
    # author_spans = [f'<span class="CEURAUTHOR">{a}</span>' for a in preface_authors]
    # toc_lines.append(",\n  ".join(author_spans))
    # toc_lines.append("  </li>")
    # toc_lines.append("</ul>")

    # Insert Summary
    summary_html = (
        f'<p class="CEURSUMMARY">\n'
        f'This volume contains the {int(config["total_working_notes"]) + int(config["total_overviews"])} working notes that were peer-reviewed and accepted for publication at '
        f'{config["acronym"].replace(" ", "")} {config["year"].replace(" ", "")}. '
        f'Out of these, {config["total_overviews"]} are overviews of the shared tasks, and {config["total_working_notes"]} are the participants\' working notes. '
        f'</p>'
    )

    # Building the Preface list item
    toc_lines = [
        '<ul>',
        f'<li id="preface"><A href="Preface.pdf">Preface</A><BR>',
        f'{summary_html}</li>',
        '</ul><BR>'
    ] 
    # Copy Preface PDF
    shutil.copy(os.path.join(base_folder, 'Preface.pdf'), os.path.join(dir_name, f"{preface_title}.pdf"))

    # 5. Process Tracks and Papers
    last_track = ""
    track_num = 0
    total_pages = 0
    
    # Iterate through paper entries (starting from 2nd info line)
    for line in all_info[1:]:
        parts = line.split(',')
        current_track = parts[0]
        title = parts[1]
        authors = [a for a in parts[2:] if a]

        if current_track != last_track:
            paper_num = 1
            track_num += 1
            if track_num > 1:
                toc_lines.append("</ul>")
            
            toc_lines.append(f'<h3><span class="CEURSESSION">{current_track}</span></h3>')
            toc_lines.append("<ul>")
        
        # Renaming logic (e.g., T1-1.pdf)
        paper_id = f"T{track_num}-{paper_num}"
        src_pdf = os.path.join(base_folder, str(track_num), f"{paper_num}.pdf")
        dest_pdf = os.path.join(dir_name, f"{paper_id}.pdf")
        
        # Copy and calculate pages
        shutil.copy(src_pdf, dest_pdf)
        start_page = total_pages + 1
        current_pages = get_pdf_page_count(dest_pdf)
        end_page = total_pages + current_pages
        total_pages = end_page

        # Append entry to TOC
        toc_lines.append(f'  <li id="{paper_id}"><a href="{paper_id}.pdf">')
        toc_lines.append(f'  <span class="CEURTITLE">{title}</span></a>')
        toc_lines.append(f'  <span class="CEURPAGES">{start_page}-{end_page}</span> <br>')
        
        auth_html = [f'<span class="CEURAUTHOR">{a}</span>' for a in authors]
        toc_lines.append("  " + ",\n  ".join(auth_html))
        toc_lines.append("  </li>")

        last_track = current_track
        paper_num += 1

    toc_lines.append("</ul>")
    final_toc_html = "\n".join(toc_lines)

    # 6. Final Injection
    # Replaces the TOC placeholder in your base-index.html
    final_html = html_content.replace("XXXTOCPLACEHOLDERXXX", final_toc_html)

    # Save the final index.html
    output_index = os.path.join(dir_name, 'index.html')
    with open(output_index, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print(f"Success! Proceedings generated in: {dir_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assemble CEUR Proceedings")
    parser.add_argument("-b", "--base", required=True, help="Base folder (e.g., 'sample')")
    parser.add_argument("-o", "--output", help="Optional output folder name (defaults to conference acronym)")
    args = parser.parse_args()
    
    generate_proceedings(args.base, args.output)