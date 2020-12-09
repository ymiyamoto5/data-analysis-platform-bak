import pstats
from pstats import SortKey

sts = pstats.Stats("profile.txt")
sts.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(20)

