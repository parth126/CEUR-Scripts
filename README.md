# CEUR-Scripts
This repository consists of scripts for automating the creation of CEUR Proceedings

**Author:** [Parth Mehta](https://www.linkedin.com/in/parthmehta126/)  
**Organization:** Parmonic 

## Step by Step Usage

### 1. Collect Data
- Collect all data in a folder e.g. <FIRE_PAPERS> (similar to what is shown in sample folder)
- Add preface.pdf (placeholder if you have been to lazy to complete the preface so far).
- Each track should have one folder ordered as 1, 2, 3..
- Each paper in a track should be named 1.pdf, 2.pdf, ...
- working_notes_info.csv should is of the format Track Name,Title,Authors
- Authors are a list of authors separated by a comma
- No paper title should contain a comma. This is not supported so far and will break the index file.

### 2. Update conference details  
Edit the conference-info.yaml file to match the conference details

### 3. Create the base index file.  

```sh
python generate_base_index.py --base <FIRE_PAPERS>
```
- This step fetches latest CEUR index template and creates a skeleton with conference details.  
- The current script is tested on 27-12-2025 and is not guaranteed to work if CEUR updates the HTML index.html template in future.  

**Note:** It is important that you verify the conference details in the resulting base-index.html file at this point

### 4. Create the proceedings folder

```sh
python generate_proceedings.py --base <FIRE_PAPERS> --output <ACRONYM><YEAR>
# e.g. python generate_proceedings.py --base FIRE_SUBMISSIONS --output FIRE2019
```
- This creates a folder names <ACRONYM><YEAR> (e.g FIRE2019) which is supposed to be zipped and submitted to CEUR.
- This script iterates over the working-notes_info.csv file and adds paper titles, page number and author names to the index file.
- It also creates a copy of the papers in TA_B.pdf format (A = track id and B = paper id). So T2_1.pdf is the first paper in track 2.     

**Note:** It is important that you verify the resulting index.html file for any errors in paper titles or author names at this point

### 5. Run CEUR Checks

CEUR requires 3 checks before uploading the proceedings.

**1. Checking the pdfs**.
- The script needs to be copied inside the folder containing PDFs to be evaluated and then run using the command below
```sh
bash check-pdf-errors
```

**2. Checking the index.html**.
- The script needs to be copied inside the folder containing PDFs and index.html to be evaluated and then run using the command below
```sh
bash check-pdf-errors
```
**Note: ** This command can only be run after generating index as well as proceedings.

**3. W3C Validaiton**
- This can be done by using the tool here: https://validator.w3.org/nu/#file
- Simply upload your index.html file and check
