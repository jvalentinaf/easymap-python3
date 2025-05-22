#!src/Python-3.12.3/.localpython/bin/python3

import os
import cgi, cgitb
cgitb.enable()

arguments = cgi.FieldStorage()
projectName = str(arguments['p'].value).strip()

print("Content-type:text/html\r\n\r\n")

file_path = os.path.join('user_projects', projectName, '3_workflow_output', 'rfeed.html')

if os.path.exists(file_path):
    try:
        with open(file_path) as reportFile:
            for line in reportFile:
                print(line)
    except Exception as e:
        print(f"<h1>Error al leer el archivo: {e}</h1>")
else:
    print(f"<h1>Archivo no encontrado: {file_path}</h1>")
