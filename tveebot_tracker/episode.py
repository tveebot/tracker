import re
from collections import namedtuple
from enum import Enum

from tveebot_tracker.exceptions import ParseError

TVShow = namedtuple("TVShow", "id name")
EpisodeFile = namedtuple("EpisodeFile", "title link quality")

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
    def from_title(title: str, tvshow_id: str):
        """
        Parses the *title*, obtaining the episode's information. The only
        information that is not available from the title is the TV show ID
        that must be provided in a separate argument.

        :param title: full episode title to parse
        :param tvshow_id: ID of the tv show the episode belongs to
        :return: episode parsed from the given title
        """
        words = title.split(" ")
        for index, word in enumerate(words):
            match = Episode._episode_pattern.match(word)
            if match:
                # Parse season and number from this word
                season, number = map(int, match.group().split('x'))

                # The previous words compose the TV Show name
                tvshow_name = " ".join(words[:index])

                # The remainder corresponds to the episode's title
                # except some flags
                remainder = words[index + 1:]

                # Remove flags
                while remainder and remainder[-1] in Episode._tags:
                    remainder = remainder[:-1]

                # join the remainder without the flags to complete the title
                episode_title = " ".join(remainder)

                return Episode(TVShow(tvshow_id, tvshow_name),
                               episode_title, season, number)

        raise ParseError(f"failed to parse title '{title}'")
