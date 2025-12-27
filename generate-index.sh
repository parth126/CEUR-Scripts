#!/bin/bash

## Replace these details with that of current year and run the script.  

Acronym="FIRE 2019"
Year="2019"
City="Kolkata"
StartDate="12"
EndDate="15"
Month="December"

## Submission Date has to be in YYYY-MM-DD format
SubmissionDate="2019-12-06"

## The person who uploads the proceedings has to be one of the editors

SubmittedBy="Parth Mehta"

#---------#---------#---------#---------#---------#---------#---------#---------#---------#---------#
#---------#---------#---------#---------# Code Begins Here  #---------#---------#---------#---------#
#---------#---------#---------#---------#---------#---------#---------#---------#---------#---------#

## Creating FIRExxxx directory if it does not exist

DirName=$(echo $Acronym | sed 's/ //g')
if [ -d "$DirName" ]
then
	echo ""
else
	mkdir $DirName
fi

## Replacing the conference details with that of current year.

sed "s/XXXACRONYMXXX/${Acronym}/g" base-index.html | sed "s/XXXYEARXXX/${Year}/g" | sed "s/XXXCITYXXX/${City}/g" | sed "s/XXXSTARTDATEXXX/${StartDate}/g" | sed "s/XXXENDDATEXXX/${EndDate}/g" | sed "s/XXXMONTHXXX/${Month}/g" | sed "s/XXXSUBMISSIONDATEXXX/${SubmissionDate}/g" | sed "s/XXXSUBMITTEDBYXXX/${SubmittedBy}/g" > ./$DirName/index.html

## Generating Editor Information
### I was too lazy to write this part of the code.
### Editor Information needs to be provided in a separate file editor.info. Since it uses html tags as required, it is best to edit last year's editor.info file.

## Generating Preface and Initializing TOC

echo > TOC
info=$(head -n 2 working-notes.info | tail -n 1)
Title=$(echo $info | cut -d ',' -f 2)
AuthorID=$(echo $info | cut -d ',' -f 3 | rev | cut -d ' ' -f 1| rev | cut -d '-' -f 1)
NumberOfAuthors=$(echo $info | cut -d ',' -f 3- | sed 's/,*$//g' | awk -F',' '{ print NF }')
echo "<ul>" >> TOC
echo "<li id=\""$Title"\"><a href=\""$Title".pdf\">" >> TOC
echo "<span class=\"CEURTITLE\">Preface</span></a>" >> TOC 
echo "<br>" >> TOC
for (( i=1; i <= $NumberOfAuthors; i++ ))
do
	Author=$(echo $info | cut -d ',' -f $(($i+2)))
	if [ "$i" != "$NumberOfAuthors" ]
	then
		echo "<span class=\"CEURAUTHOR\">"$Author"</span>," >> TOC
	else
		echo "<span class=\"CEURAUTHOR\">"$Author"</span>" >> TOC
	fi
done
echo "</li>" >> TOC
echo "</ul>" >> TOC	
cp ./Preface.pdf ./$DirName/$Title.pdf


## Generating Table of Content (TOC)

LastTrack=""
N=0
TotalPages=0
awk "NR > 2" working-notes.info | 
while read info
do
	CurrentTrack=$(echo $info | cut -d ',' -f 1)
	Title=$(echo $info | cut -d ',' -f 2)
#	Start=$(echo $info | cut -d ',' -f 3)
#	End=$(echo $info | cut -d ',' -f 4)
	NumberOfAuthors=$(echo $info | cut -d ',' -f 3- | sed 's/,*$//g' | awk -F',' '{ print NF }')
	AuthorID=$(echo $info | cut -d ',' -f 3 | rev | cut -d ' ' -f 1| rev | cut -d '-' -f 1) 
	if [ "$CurrentTrack" != "$LastTrack" ]
	then
		M=1
		N=$((N+1))
		if [ "$N" != 1 ]
		then
			echo >> TOC
			echo "</ul>" >> TOC
			echo >> TOC
			echo >> TOC
		fi
		echo "<h3><span class=\"CEURSESSION\">"$CurrentTrack"</span></h3>" >> TOC
		echo >> TOC
		echo "<ul>" >> TOC
		echo >> TOC
	fi
	Id=$(echo "T"$N"-"$M)
	cp ./$N/$M.pdf ./$DirName/$Id.pdf
	Start=$(($TotalPages+1))
	CurrentPages=$(pdfinfo ./$DirName/$Id.pdf | grep Pages | awk '{print $2}')	
	End=$(($TotalPages + $CurrentPages))
	TotalPages=$End
	LastTrack=$CurrentTrack
	echo "<li id=\""$Id"\"><a href=\""$Id".pdf\">" >> TOC
	echo "<span class=\"CEURTITLE\">"$Title"</span></a>" >> TOC
	echo "<span class=\"CEURPAGES\">"$Start"-"$End"</span> <br>" >> TOC
	for (( i=1; i <= $NumberOfAuthors; i++ ))
	do
		Author=$(echo $info | cut -d ',' -f $(($i+2)))
		if [ "$i" != "$NumberOfAuthors" ]
		then
			echo "<span class=\"CEURAUTHOR\">"$Author"</span>," >> TOC
		else
			echo "<span class=\"CEURAUTHOR\">"$Author"</span>" >> TOC
		fi
	done
	echo "</li>" >> TOC
	M=$((M+1))
done

echo >> TOC
echo "</ul>" >> TOC
echo >> TOC
echo >> TOC


## Replacing Editor Info and TOC in index.html
	
sed -i -e "/XXXEDITORINFOPLACEHOLDERXXX/r editor.info" -e "s///" ./$DirName/index.html
sed -i -e "/XXXTOCPLACEHOLDERXXX/r TOC" -e "s///" ./$DirName/index.html
