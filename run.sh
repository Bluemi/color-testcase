#!/bin/bash

case "$1" in 
	b)
		python3 color_testcase/black_bodies.py
		;;
	*)
		python3 color_testcase/main.py
		;;
esac
