#!/bin/bash

VERSION=2.0.2

if [ -e Doxyfile_en ]; then
	    rm Doxyfile_en
	        rm -rf ClassReference-en
fi
if [ -e Doxyfile_jp ]; then
	    rm Doxyfile_jp
	        rm -rf ClassReference-jp
fi

sed -e "s/__VERSION__/${VERSION}/g" Doxyfile_en.in > Doxyfile_en
sed -e "s/__VERSION__/${VERSION}/g" Doxyfile_jp.in > Doxyfile_jp

doxygen Doxyfile_en
doxygen Doxyfile_jp

