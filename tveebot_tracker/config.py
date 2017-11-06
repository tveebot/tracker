from configparser import ConfigParser
from os import PathLike

from pathlib import Path
from pkg_resources import resource_filename


class Config:
    """
    Abstraction to access the configurations in the configuration file.

    The components, such as the tracker or the downloader, should access the
    configuration parameters through a Config instance.

    Configurations can be loaded from one or multiple files.

    Configurations can be changed while the daemon is already running. To do
    this, just ask config to reload and it will update every parameter for
    all components immediately.
    """
    # TODO improve documentation for this class

    DEFAULT_CONF = resource_filename(__name__, 'config.ini')

    def __init__(self):
        self._config = ConfigParser()

    def load_defaults(self):
        """ Loads the default configurations """
        self.load(self.DEFAULT_CONF)

    def load(self, file: PathLike):
        """
        Loads configurations from an INI file. The parameters specified in
        the file will be updated. Parameters missing from the file will be
        kept with their current value.

        :param file: INI file to load configurations from
        """
        with open(file) as f:
            self._config.read_file(f)

    @property
    def track_period(self):
        return float(self._config['tracker']['TrackPeriod'])

    @property
    def db_file(self):
        return Path(self._config['tracker']['Database'])

    @property
    def download_dir(self):
        return Path(self._config['downloader']['DownloadDirectory'])


