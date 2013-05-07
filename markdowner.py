#!/usr/bin/env python3
import sys, os
from runpy import run_module

HERE = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, HERE)

os.environ["KDEDIRS"] = os.path.join(HERE, 'i18n')

run_module('markdowner')