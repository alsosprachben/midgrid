#!/bin/sh
python3 midgrid_parser.py "${1}".midgrid "${1}".mid
timidity "${1}".mid
play "${1}".ogg
