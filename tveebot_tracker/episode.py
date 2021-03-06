import re
from collections import namedtuple
from enum import Enum

from tveebot_tracker.exceptions import ParseError

TVShow = namedtuple("TVShow", "id name")
EpisodeFile = namedtuple("EpisodeFile", "title link quality")


class Quality(Enum):
    SD, HD, FHD = range(3)

    @property
    def tag(self) -> str:
        return _quality_to_tag[self]

    @staticmethod
    def from_tag(tag: str):
        return _quality_from_tag[tag]


_quality_to_tag = {
    Quality.SD: "480p",
    Quality.HD: "720p",
    Quality.FHD: "1080p",
}

_quality_from_tag = {
    "480p": Quality.SD,
    "720p": Quality.HD,
    "1080p": Quality.FHD,
}


class State(Enum):
    QUEUED, DOWNLOADING, DOWNLOADED = range(3)

    @property
    def tag(self) -> str:
        return _state_to_tag[self]

    @staticmethod
    def from_tag(tag: str):
        return _state_from_tag[tag]


_state_to_tag = {
    State.QUEUED: "queued",
    State.DOWNLOADING: "downloading",
    State.DOWNLOADED: "downloaded",
}

_state_from_tag = {
    "queued": State.QUEUED,
    "downloading": State.DOWNLOADING,
    "downloaded": State.DOWNLOADED,
}


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
