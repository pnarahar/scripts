#!/bin/tcsh
grep -E '^[^/]*\s*[a-zA-Z0-9]+\s+[a-zA-Z0-9]+\s*(#\s*\([^\)]*\))?\s*\(' -ni $1
