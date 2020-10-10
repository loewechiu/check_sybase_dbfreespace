# check_sybase_dbfreespace

# Prerequiste: 
1. rpm -i devart-odbc-ase.x86_64.rpm
2. pip3 install pyodbc
3. let network team open port 4901,4902,... (/sybase/<SID>/interfaces)
# Reference: https://www.devart.com/odbc/ase/docs/python.htm
# Sample:
./check_sybase_dbfreespace.py -H 1.1.1.1 -d STD -u myuser -p mypwd -P 4901
