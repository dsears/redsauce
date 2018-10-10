#!/usr/bin/bash

python -u sync_omdb_rt.py 2>&1 | tee /tmp/sync_omdb_rt.log
tail -100 /tmp/sync_omdb_rt.log | mail -s sync_omdb_rt.log dsears@gmail.com
