from contextlib import contextmanager

from tveebot_tracker.episodes import TVShow, Quality, Episode


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


class EpisodeDB:
    """ Abstraction for the Episode DB """

    @contextmanager
    def connect(self):
        pass
