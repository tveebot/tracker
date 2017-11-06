import logging
from datetime import datetime
from queue import Queue, Empty

import libtorrent as lt

from tveebot_tracker.config import Config
from tveebot_tracker.episode import Episode, EpisodeFile, State
from tveebot_tracker.episode_db import EpisodeDB, connect
from tveebot_tracker.stoppable_thread import StoppableThread

logger = logging.getLogger('downloader')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class Downloader(StoppableThread):
    """
    The downloader is the component responsible for actually downloading
    the episode files. It is a simple torrent client.

    This is an abstract base class for downloader implementations. It
    implements the logic of having the downloader run in loop and queue
    episodes to be downloaded. The actual steps/protocol are left to the be
    implemented by the subclasses.
    """

    QUEUE_TIMEOUT = 5.0  # seconds

    state_str = ['queued', 'checking', 'downloading metadata',
                 'downloading', 'finished', 'seeding', 'allocating']

    def __init__(self, database: EpisodeDB, config: Config,
                 queue: Queue = Queue()):
        super().__init__()
        self._database = database
        self._config = config

        # This queue is shared with the tracker. The tracker 'produces'
        # episodes to download. The Downloader consumes those episodes and
        # downloads them.
        self._queue = queue

        # noinspection PyArgumentList
        self.session = lt.session()
        self.session.listen_on(6881, 6891)

        self._handles = []  # holds episode, file, and handle

    @property
    def download_dir(self):
        """ Download queue, including the episodes to be downloaded """
        return self._config.download_dir

    @property
    def queue(self):
        """ Download queue, including the episodes to be downloaded """
        return self._queue

    def run(self):
        # TODO restart downloads for episodes ser as DOWNLOADING

        while not self.stopped():
            logger.debug("looking for finished downloads")
            finished = []
            for episode, file, handle in self._handles:
                if handle.status().is_seeding:
                    finished.append((episode, file, handle))
                    logger.debug(f"found finished download: {episode}")

            # Remove handles corresponding to finished downloads
            for episode, file, handle in finished:
                logger.info(f"finished downloading {episode}")
                self._download_finished(episode, file)
                self.session.remove_torrent(handle)
                self._handles.remove((episode, file, handle))

            try:
                episode, file = self.queue.get(timeout=self.QUEUE_TIMEOUT)
                self.download(episode, file)
            except Empty:
                pass  # go check if the stop() method was called

    def download(self, episode: Episode, file: EpisodeFile):
        """
        Subclasses should use this method as the entry point to start
        downloading an episode file.

        !! When this method returns, it does not mean, necessarily, that the
        episode has finished downloading !!

        :param episode: episode to download
        :param file:    actual file to be downloaded
        """
        params = {
            'save_path': self.download_dir,
            'storage_mode': lt.storage_mode_t.storage_mode_sparse
        }
        handle = lt.add_magnet_uri(self.session, file.link, params)
        self._handles.append((episode, file, handle))

        logger.info(f"started downloading {episode}")

        # Set the episode's state as 'downloading'
        with connect(self._database) as connection:
            connection.set_episode_state(episode, State.DOWNLOADING)
        logger.debug("set episode's state as 'downloading'")

    def state_info(self):
        # TODO improve the information provided by this method
        state_info = []

        for episode, file, handle in self._handles:
            status = handle.status()
            state_info.append((episode, status))

        return state_info

    def _download_finished(self, episode: Episode, file: EpisodeFile):
        """
        Changes the *episode*'s state to 'downloaded' and updates its
        download information, such as, the episode quality and the time at
        which the episode was downloaded.

        :param episode: episode that finished downloading
        :param file:    actual file that has been downloaded
        """
        with connect(self._database) as connection:
            connection.set_episode_state(episode, State.DOWNLOADED)
            connection.set_episode_quality(episode, file.quality)
            connection.set_episode_download_timestamp(episode, datetime.now())
