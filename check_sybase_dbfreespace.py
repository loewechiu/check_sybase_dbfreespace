#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:           itqiuw
# Released Date:    2020-10-10
# Purpose: this script is to check the sybase dbfreespace
# normally we do in local: sdal05v113 /sybase/STD% isql -Usapsa -Psdbwein -SSTD
# and then related sql commands and with "go" behind
# Here we'll use python ODBC with devart ASE driver to connect
# Prerequiste: 1. rpm -i devart-odbc-ase.x86_64.rpm
#              2. pip3 install --proxy 10.134.254.52:8080 pyodbc
#              3. let network team open port 4901,4902,... (/sybase/<SID>/interfaces)
# Reference: https://www.devart.com/odbc/ase/docs/python.htm
# Sample:  ./check_sybase_dbfreespace.py -H 1.1.1.1 -d STD -u myuser -p mypwd -P 4901


import os,sys
import pyodbc
import getopt

exitdic = {'UNKNOWN':3,  #-1 is also UNKNOWN
           'OK':0,
           'WARNING':1,
           'CRITICAL':2
           }

def usage():
    print('Usage: ' + sys.argv[0] + " [-d][-H][-u][-p][-h][-P]")
    print("""
    -d, --database ... database id
    -H, --host     ... host of the database server
    -u, --user     ... user
    -p, --pass     ... password
    -P, --port     ... port
    -h, --help     ... help information
    """)

def command_args(argv):
    global g_sid,g_host,g_user,g_pass,g_port
    try:
        #: means should be parameter followed
        opts, args = getopt.getopt(argv, 'hd:H:u:p:P:', ['help','database','host','user','pass','port'])
    except getopt.GetoptError:
        usage()
        sys.exit(3)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(1)
        elif opt in ('-d','--database'):
            g_sid = arg
        elif opt in ('-H','--host'):
            g_host = arg
        elif opt in ('-u','--user'):
            g_user = arg
        elif opt in ('-p','--pass'):
            g_pass = arg
        elif opt in ('-P','--port'):
            g_port = arg
        else:
            usage()
            sys.exit(3)

if __name__ == '__main__':
    g_sid = ''
    g_host = ''
    g_user = ''
    g_pass = ''
    g_port = '4901'

    command_args(sys.argv[1:])
    g_sid = g_sid.upper()
    rc = 'OK'
    perf = '|'
    desc = ""

    if g_sid  == "" or g_host == "":
        print("Unkown - Missing arguments!")
        sys.exit(3)

    ### Connection of database

    cnxn = pyodbc.connect('DRIVER={Devart ODBC Driver for ASE};Server='+g_host+';Port='+str(g_port)+';Database='+g_sid+';User ID='+g_user+';Password='+g_pass+';String Types=Unicode')
    cursor = cnxn.cursor()
    cursor.execute('select convert(char(16), db_name(d.dbid)) + "|Data_Total_MB=" + convert(char(9), ceiling (sum(case when u.segmap != 4 then u.size/1048576.*@@maxpagesize end ))) + "|Free_MB=" + convert(char(14), (convert(numeric(8,1), ((sum(case when u.segmap != 4 then u.size/1048576.*@@maxpagesize end ))) - (sum(case when u.segmap != 4 then size - curunreservedpgs(u.dbid, u.lstart, u.unreservedpgs) end)/1048576.*@@maxpagesize)))) + "|Used=" + rtrim(convert(char(9), (convert(numeric(12,2),100 * (1 - 1.0 * sum(case when u.segmap != 4 then curunreservedpgs(u.dbid, u.lstart, u.unreservedpgs) end) / sum(case when u.segmap != 4 then u.size end)))))) from master..sysdatabases d, master..sysusages u where u.dbid = d.dbid  and d.status not in (256,4096) group by d.dbid order by db_name(d.dbid)')
    row = cursor.fetchone()
    while row:
      #print (row)
      tmp = row[0]
      dbname = tmp.split("|")[0].strip(' ')
      db_perc = tmp.split("|Used=")[1]
      size = tmp.split("|Data_Total_MB=")[1].split("|")[0]
      size = int(size)
      if size >= 500000:   #unit MB
          prozent = 97
      if size < 500000:
          prozent = 95
      if size < 175000:
          prozent = 90
      if size < 75000:
          prozent = 85
      if size < 25000:
          prozent = 80
      if float(db_perc) > prozent:
          rc = "CRITICAL"
          desc = desc + tmp.replace('|',' ') + ' exceeding limit\n'
      else:
          desc = desc + tmp.replace('|',' ') + '\n'
      perf = perf + dbname + "=" + db_perc + "%;;;;"
      row = cursor.fetchone()

    ###Output part
    output = rc + " - \n" + desc + perf
    print(output)
    sys.exit(exitdic[rc])
                                                                            