from contextlib import contextmanager
from datetime import datetime

from tveebot_tracker.episode import TVShow, Quality, Episode, State


class Connection:
    """ Abstraction for a connection for the Episode DB """

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass

    #
    # TV Show Table methods
    #

    def insert_tvshow(self, tvshow: TVShow, quality: Quality):
        pass

    def delete_tvshow(self, tvshow_id: str):
        pass

    def tvshows(self):
        pass

    def set_tvshow_quality(self, tvshow_id: str, quality: Quality):
        pass

    #
    # Episode Table Methods
    #

    def insert_episode(self, episode: Episode):
        pass

    def episodes(self):
        pass

    def episodes_from(self, tvshow: TVShow):
        pass

    def set_episode_state(self, episode: Episode, state: State):
        pass

    def set_episode_quality(self, episode: Episode, quality: Quality):
        pass

    def set_episode_download_timestamp(self, episode: Episode, download_timestamp: datetime):
        pass


class EpisodeDB:
    """ Abstraction for the Episode DB """

    @contextmanager
    def connect(self):
        pass
