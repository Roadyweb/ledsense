#!/bin/bash

python3 -m coverage run --source=. test.py
python3 -m coverage report -m
python3 -m coverage html

