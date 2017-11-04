from abc import ABC, abstractmethod
from queue import Queue, Empty

from tveebot_tracker.episode import Episode, EpisodeFile, State
from tveebot_tracker.episode_db import EpisodeDB
from tveebot_tracker.stoppable_thread import StoppableThread


class Downloader(ABC, StoppableThread):
    """
    The downloader is the component responsible for actually downloading
    the episode files.

    This is an abstract base class for downloader implementations. It
    implements the logic of having the downloader run in loop and queue
    episodes to be downloaded. The actual steps/protocol are left to the be
    implemented by the subclasses.
    """

    def __init__(self, database: EpisodeDB, queue: Queue=Queue()):
        super().__init__()
        self._database = database

        # This queue is shared with the tracker. The tracker 'produces'
        # episodes to download. The Downloader consumes those episodes and
        # downloads them.
        self._queue = queue

    @property
    def queue(self):
        """ Download queue, including the episodes to be downloaded """
        return self._queue

    def run(self):
        pass

    @abstractmethod
    def download(self, episode: Episode, file: EpisodeFile):
        """
        Subclasses should use this method as the entry point to start
        downloading an episode file.

        !! When this method returns, it does not mean, necessarily, that the
        episode has finished downloading !!

        Subclasses should always call _download_finished() method when a
        download has finished.

        :param episode: episode to download
        :param file:    actual file to be downloaded
        """

    def _download_finished(self, episode: Episode, file: EpisodeFile):
        """
        Changes the *episode*'s state to 'downloaded' and updates its
        download information, such as, the episode quality and the time at
        which the episode was downloaded.

        Must be called by subclasses after they determine that an episode
        file has finished downloading.

        :param episode: episode that finished downloading
        :param file:    actual file that has been downloaded
        """

