import re
from collections import namedtuple
from enum import Enum

from tveebot_tracker.exceptions import ParseError

TVShow = namedtuple("TVShow", "id name")
EpisodeFile = namedtuple("EpisodeFile", "tvshow title link quality")

# The statements below are perfectly correct, as described in
# https://docs.python.org/3/library/enum.html#functional-api
# noinspection PyArgumentList
Quality = Enum('Quality', 'FHD HD SD')

# noinspection PyArgumentList
State = Enum('State', 'QUEUED DOWNLOADING DOWNLOADED')


class Episode:
    """ Data class representing an Episode """

    def __init__(self, tvshow: TVShow, title: str, season: int, number: int):
        self.tvshow = tvshow
        self.title = title
        self.season = season
        self.number = number

    def __eq__(self, other):
        return self.tvshow == other.tvshow and \
               self.title == other.title and \
               self.season == other.season and \
               self.number == other.number

    def __str__(self):
        return f"Episode({self.tvshow}, {self.title}, {self.season}, " \
               f"{self.number})"

    def __repr__(self):
        return str(self)

    _episode_pattern = re.compile('\d+x\d+\Z')
    _tags = {'PROPER', 'REPACK', 'TBA'}

    @staticmethod
    def from_file(file: EpisodeFile):
        """
        Obtains the episode corresponding to the specified file.

        :param file: episode file to obtain corresponding episode from
        :return: episode parsed from the given title
        """
        raw_title: str = file.title

        words = raw_title.split(" ")
        for index, word in enumerate(words):
            match = Episode._episode_pattern.match(word)
            if match:
                # Parse season and number from this word
                season, number = map(int, match.group().split('x'))

                # The remainder corresponds to the episode's title
                # except some flags
                remainder = words[index + 1:]

                # Remove flags
                while remainder and remainder[-1] in Episode._tags:
                    remainder = remainder[:-1]

                # join the remainder without the flags to complete the title
                title = " ".join(remainder)

                return Episode(file.tvshow, title, season, number)

        raise ParseError(f"The file '{file}' did not map to an episode")
