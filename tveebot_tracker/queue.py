from pathlib import Path

from tveebot_tracker.episode import Episode


class EpisodeQueue:
    """
    Implementation of a persistent queue for episodes.
    This queue will include episode files to be downloaded.
    """

    def __init__(self, queue_file: Path):
        self._file = queue_file

    def put(self, link: str, episode: Episode):
        pass

    def get(self) -> (str, Episode):
        pass
