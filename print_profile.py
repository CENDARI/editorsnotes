#!/usr/bin/env python
import pstats
p = pstats.Stats('cendari.profile')
p.strip_dirs().sort_stats('cumulative').print_stats()


