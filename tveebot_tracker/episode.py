from collections import namedtuple
from enum import Enum

TVShow = namedtuple("TVShow", "id name")
Episode = namedtuple("Episode", "tvshow title season number")
EpisodeFile = namedtuple("EpisodeFile", "tvshow_name title link quality")

# The state below is perfectly correct, as described in
# https://docs.python.org/3/library/enum.html#functional-api
# noinspection PyArgumentList
Quality = Enum('Quality', '1080p 720p 480p')

