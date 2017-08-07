#################################################################
#								#
# download-data.sh						#
#								#
# BASH script to download the defaulters PDF files and convert  #
# the PDFs to text for later processing.			#
#								#
# Version 0.1							#
#################################################################

#!/bin/bash
BIN="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DIR="$(dirname "$BIN")"
LOGFILE="$DIR/log/pdf-download.log"

# Start the script
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
echo "$TIMESTAMP - Starting scraping Script.">> $LOGFILE

# File date prefix
DATE=$(date +"%Y%m%d")

# Input file
INPUT_FILE=$DIR/data/input_$DATE.pdf

# Clean up data directory
rm -f $DIR/data/*.pdf
rm -f $DIR/data/*.txt

# Function to download and conver the PDFs
getPDF () {
	echo "Processing... $2.pdf"

	wget --quiet $1 -O $DIR/data/$2.pdf
	FILESIZE=$(du -k "$DIR/data/$2.pdf" | cut -f 1)
	TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
        echo "$TIMESTAMP - PDF file $2.pdf downloaded, size $FILESIZE kb" >> $LOGFILE

        pdftotext -layout -q -nopgbrk $DIR/data/$2.pdf
	LINES=$(wc -l "$DIR/data/$2.txt" | cut -d' ' -f 1)
	TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
        echo "$TIMESTAMP - PDF converted to TXT $2.txt with $LINES lines" >> $LOGFILE
	rm -f $DIR/data/$2.pdf
}

#2017
getPDF http://www.revenue.ie/en/corporate/press-office/list-of-defaulters/2017/defaulters-list1-june2017.pdf march_1_2017

#2016
getPDF http://www.revenue.ie/en/corporate/press-office/list-of-defaulters/2016/defaulters-list1-december2016.pdf december_1_2016
getPDF http://www.revenue.ie/en/corporate/press-office/list-of-defaulters/2016/defaulters-list1-september2016.pdf september_1_2016
getPDF http://www.revenue.ie/en/corporate/press-office/list-of-defaulters/2016/defaulters-list1-june2016.pdf june_1_2016
getPDF http://www.revenue.ie/en/corporate/press-office/list-of-defaulters/2016/defaulters-list1-march2016.pdf march_1_2016

#2015
getPDF http://www.revenue.ie/en/corporate/press-office/list-of-defaulters/2015/defaulters-list1-december2015.pdf december_1_2015
getPDF http://www.revenue.ie/en/corporate/press-office/list-of-defaulters/2015/defaulters-list1-september2015.pdf september_1_2015
getPDF http://www.revenue.ie/en/corporate/press-office/list-of-defaulters/2015/defaulters-list1-june2015.pdf june_1_2015
