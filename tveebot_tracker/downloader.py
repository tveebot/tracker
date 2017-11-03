import asyncio
from abc import ABC, abstractmethod

from tveebot_tracker.episode import Episode


class Downloader(ABC):
    """
    The downloader is the component responsible for actually downloading
    the episode files.

    This is an abstract base class for downloader implementations. It
    implements the logic of having the downloader run in loop and queue
    episodes to be downloaded. The actual steps/protocol are left to the be
    implemented by the subclasses.
    """

    def __init__(self):
        self._queue = asyncio.Queue()
        self._loop = asyncio.get_event_loop()

    def run_forever(self):
        self._loop.run_forever()

    def stop(self):
        self._loop.stop()

    def close(self):
        self._loop.close()

    # Called by the tracker when it wants to download a new episode
    def download(self, file: EpisodeFile):
        self._loop.create_task(self._download(file))

    @abstractmethod
    async def _download(self, file: EpisodeFile):
        pass
