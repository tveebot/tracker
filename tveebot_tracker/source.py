from abc import ABC, abstractmethod


class TVShowNotFound(Exception):
    """ Raised when a reference does not match any TV Show available """


class EpisodeSource(ABC):
    """
    Abstract base class to define the interface for and episode source.

    An episode source is used by the tracker to obtain episode files. A
    source is usually based on a feed that provides links to TV Show's
    episodes.

    Every source has its own protocol to obtain the information and it uses
    its own format to present that information. Implementations of this
    interface are responsible for implementing the details of how to obtain
    the episode files' information and present them to the tracker.
    """

    # Called by the tracker when it wants to get the episodes available for
    # a specific TVShow
    @abstractmethod
    def fetch(self, tvshow_reference: str) -> list:
        """
        Fetches all available episode files, corresponding to the specified
        TV show. Multiple files for the same episode may be retrieved.

        The TV show to obtain the episodes from is identified by some reference
        that uniquely identifies it within the episode source in question.

        :param tvshow_reference: reference that uniquely identifies the TV show
                                 to get the episodes for
        :return: a list containing all episode files available for the specified
                 TV Show. An empty list if none is found.
        :raise TVShowNotFound: if the specified reference does not match to any
                               TV show available
        """
