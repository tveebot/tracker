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


def from_title(title: str, tvshow_id: str) -> Episode:
    """
    Parses an title and returns the corresponding episode.

    :param title:     title to parse
    :param tvshow_id: ID to assign to the episode's TV Show
    :return: episode parsed from the given title
    """
    pass
