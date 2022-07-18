#!/usr/bin/bash

input="in/input$1.txt"

while read line || [ -n "$line" ] ; do echo "$line" ; done < $input


mkdir -p out
/usr/bin/python3 main.py < $input > out/output$1.txt