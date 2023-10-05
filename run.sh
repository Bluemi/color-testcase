#!/bin/bash

case "$1" in 
	b)
		python3 color_testcase/black_bodies.py
		;;
	*)
		poetry run color_testcase/main.py
		;;
esac
