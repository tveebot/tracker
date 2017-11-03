from tveebot_tracker.downloader import Downloader
from tveebot_tracker.episode_db import EpisodeDB
from tveebot_tracker.source import EpisodeSource


class Tracker:
    """
    The Tracker is the main component of the application. It connects
    everything together.

    Its job is to check episodes available to download, keep track of episodes
    that have already been downloaded, and download only new episodes. It does
    this for multiple TV Shows.
    """

    def __init__(self, source: EpisodeSource, episode_db: EpisodeDB,
                 downloader: Downloader):
        self.source = source
        self.episode_db = episode_db
        self.downloader = downloader

    def run_forever(self):
        pass

    def stop(self):
        pass

    def close(self):
        pass
