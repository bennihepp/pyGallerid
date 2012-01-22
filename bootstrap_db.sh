#!/bin/bash

username="hepp"
email="benjamin.hepp@gmail.com"
config=$1
password=$2

bin/init_gallery $1 $username $email $2
for category in `ls data/pictures/original`; do
    for album in `ls data/pictures/original/$category`; do
        bin/import_album $1 $category $username data/pictures/original/$category/$album
    done
done

