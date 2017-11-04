from threading import Thread, Event


class StoppableThread(Thread):
    """ Utility class to create stoppable threads """

    def __init__(self, daemon=None):
        super().__init__(daemon=daemon)

        self._to_stop = Event()

    def stop(self):
        """ Signals the thread to stop """
        self._to_stop.set()

    def stopped(self) -> bool:
        """ Indicates whether the thread was stopped or not """
        return self._to_stop.is_set()

    def wait_on_stop(self, timeout):
        """
        Blocks until the stop() is called or the timeout is reached.

        :return True if the stop() was called or false it it timed out
        """
        return self._to_stop.wait(timeout)
