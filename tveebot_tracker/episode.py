from collections import namedtuple
from enum import Enum

TVShow = namedtuple("TVShow", "id name")
Episode = namedtuple("Episode", "tvshow title season number")
EpisodeFile = namedtuple("EpisodeFile", "tvshow_name title link quality")

# The statements below are perfectly correct, as described in
# https://docs.python.org/3/library/enum.html#functional-api
# noinspection PyArgumentList
Quality = Enum('Quality', 'FHD HD SD')

# noinspection PyArgumentList
State = Enum('State', 'QUEUED DOWNLOADING DOWNLOADED')