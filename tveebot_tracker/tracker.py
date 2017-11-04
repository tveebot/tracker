from queue import Queue

from tveebot_tracker.episode_db import EpisodeDB
from tveebot_tracker.source import EpisodeSource
from tveebot_tracker.stoppable_thread import StoppableThread


class Tracker(StoppableThread):
    """
    The Tracker is the main component of the application. It connects
    everything together.

    Its job is to check episodes available to download, keep track of episodes
    that have already been downloaded, and download only new episodes. It does
    this for multiple TV Shows.
    """

    def __init__(self, source: EpisodeSource, episode_db: EpisodeDB,
                 download_queue: Queue, check_period: float):
        """
        Initialize the tracker with the necessary components.

        :param source:         source to obtain episode files from
        :param episode_db:     DB used to track episodes
        :param download_queue: queue shared with downloader to place new
                               episodes to be downloaded
        :param check_period:   period of time with which the tracker will
                               check for new episodes
        """
        super().__init__()
        self.source = source
        self.database = episode_db
        self._queue = download_queue
        self._check_period = check_period

    def run(self):
        pass
