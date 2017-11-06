import logging
from queue import Queue

from tveebot_tracker.config import Config
from tveebot_tracker.episode import TVShow, Quality, State, Episode
from tveebot_tracker.episode_db import EpisodeDB, connect
from tveebot_tracker.source import EpisodeSource
from tveebot_tracker.stoppable_thread import StoppableThread

logger = logging.getLogger('tracker')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class Tracker(StoppableThread):
    """
    The Tracker is the main component of the application. It connects
    everything together.

    Its job is to check episodes available to download, keep track of episodes
    that have already been downloaded, and download only new episodes. It does
    this for multiple TV Shows.
    """

    def __init__(self, source: EpisodeSource, episode_db: EpisodeDB,
                 download_queue: Queue, config: Config):
        """
        Initialize the tracker with the necessary components.

        :param source:         source to obtain episode files from
        :param episode_db:     DB used to track episodes
        :param download_queue: queue shared with downloader to place new
                               episodes to be downloaded
        :param config:         configuration used for the whole application
        """
        super().__init__()
        self.source = source
        self.database = episode_db
        self._queue = download_queue
        self._config = config

    @property
    def check_period(self):
        return self._config.track_period

    def run(self):
        # TODO put all episodes in QUEUED state back in the download queue

        while not self.stopped():
            self.track()

            logger.debug(f"will check again in {self.check_period} seconds")
            self.wait_on_stop(timeout=self.check_period)
            logger.debug(f"checking for new episodes")

    def track(self):
        """
        Checks for new episodes that may have become available at the source
        since the last time track() was called. If new episodes are available
        they are put into the download queue.
        """
        with connect(self.database) as connection:
            for tvshow in connection.tvshows():
                logger.info(f"looking for episodes from ")
                files = self.source.fetch(tvshow.id)
                logger.debug(f"fetched {len(files)} episode files")

                # TODO handle possible errors when fetching episodes
                #   - tv show ID may be incorrect - TV Show is not found
                #   - internet connection may be failing

                for file in files:
                    episode = Episode.from_file(file)
                    if not connection.episode_exists(episode):
                        logger.info("found new episode %dx%02d" %
                                    (episode.season, episode.number))

                        connection.set_episode_state(episode, State.QUEUED)
                        logger.debug("set episode's state to QUEUED")

                        self._queue.put((episode, file))
                        logger.debug("episode was queued to be downloaded")

    def add_tvshow(self, tvshow: TVShow, quality: Quality = Quality.SD):
        """
        Adds a new TV Show to be tracked.

        :param tvshow:  TV show to be tracked
        :param quality: episodes from this TV show will be downloaded with
                        the quality specified here
        """
        with connect(self.database) as connection:
            connection.insert_tvshow(tvshow, quality)

    def remove_tvshow(self, tvshow_id: str):
        """
        Signals the tracker to stop tracking the TV Show with the specified ID.

        :param tvshow_id: ID corresponding to TV Show to stop tracking
        """
        with connect(self.database) as connection:
            connection.delete_tvshow(tvshow_id)
