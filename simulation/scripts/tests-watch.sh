#!/bin/bash

while inotifywait -e modify -qq -r .; do
	python3 test.py
done
