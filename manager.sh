#!/usr/bin/bash
clientid=`awk -F"," '{print $1}' employee.csv`
city=`awk -F"," '{print $2}' employee.csv`
address=`awk -F"," '{print $6}' employee.csv`


if [ "$1" == "bonus" ];then
    for item in $clientid
    do
        if [ "$2" == "$item" ];then
            name=`awk -F , '$1 == '$2' { print $3 }' employee.csv`
            salary=`awk -F , '$1 == '$2' { print $5 }' employee.csv`
            echo "$name will get $(($salary * 5/100)) bonus"
            break
        fi
    done

elif [ "$1" == "city" ];then
    for item in $city
    do
        if [ "$2" == "$item" ];then
            id=`grep "$2" employee.csv | awk -F"," '{print $1}'`
            for ids in $id
            do
                name=`grep "$ids" employee.csv | awk -F"," '{print $3}'`
                mobile=`grep "$ids" employee.csv | awk -F"," '{print $4}'`
                echo "Customer Name: $name"
                echo "Mobile No: $mobile"
            done
            break
        fi
    done
else
    echo "error"
fi