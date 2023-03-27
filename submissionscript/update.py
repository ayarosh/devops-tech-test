"""
Algorithm:
1. Collect the dict from filenames by regex '^([0-9]+).*'; separate the number as key and filename as a value
   s_dic = {
     "01": "01.createPersonLink.sql",
     "02": "02.someTableinsert.sql",
     "04": "04 app table.sql",
     "33": "33. appTable data.sql"
   }
2. get the current versionTable.version from mysql_container
3. loop: if [ current_ver < s_dic[] ]; then apply mysql script && update the versionTable.version = s_dic[]
"""
import os
import re
import mysql.connector

file_pattern = "^([0-9]+).*"
db_host = "mysql_container"
db_user = os.environ.get("MYSQL_USER")
db_pass = os.environ.get("MYSQL_PASSWORD")
db_name = os.environ.get("MYSQL_DATABASE")


def executeScriptsFromFile(cnx, filename):
    cursor = cnx.cursor()

    fd = open(filename, "r")
    sqlFile = fd.read()
    fd.close()
    sqlCommands = sqlFile.split(";")

    for command in sqlCommands:
        try:
            if command.strip() != "":
                cursor.execute(command)
                cnx.commit()
        except IOError:
            print("Command skipped")
    cursor.close


f_list = os.listdir("/scripts/")
sorted_list = sorted(f_list)

s_dic = {}
for file in sorted_list:
    try:
        file_num = re.match(file_pattern, file).group(1)
        s_dic.update({file_num: file})
    except AttributeError:
        file_num = re.match(file_pattern, file)
print(s_dic)

cnx = mysql.connector.connect(
    host=db_host, user=db_user, passwd=db_pass, database=db_name
)
cursor = cnx.cursor()

cursor.execute("SELECT max(version) as version FROM versionTable;")
cur_version = cursor.fetchone()
print("db version: {}".format(cur_version[0]))

for upd_version in s_dic:
    if str(cur_version[0]) < upd_version:
        print("APPLY script {}".format(s_dic[upd_version]))
        executeScriptsFromFile(cnx, "/scripts/" + s_dic[upd_version])
        print("UPDATE db to version {}".format(upd_version))
        cursor.execute(
            "UPDATE versionTable SET version = %s",
            upd_version.split(sep=None, maxsplit=-1),
        )
        cnx.commit()

cnx.close()
