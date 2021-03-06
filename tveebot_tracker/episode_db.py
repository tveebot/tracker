import sqlite3
from datetime import datetime
from functools import wraps
from pathlib import Path

from pkg_resources import resource_filename

from tveebot_tracker.config import Config
from tveebot_tracker.episode import TVShow, Quality, Episode, State, EpisodeFile


# region Errors/Exceptions


class EntryNotFoundError(Exception):
    """ Raised when the DB does not contain an expected entry """


class EntryExistsError(Exception):
    """ Raised when the DB unexpectedly contains an entry """


# endregion

# region Helper Decorators


def EntryErrors(func):
    """
    Decorator for methods that should raise an Entry Error. It converts
    sqlite errors into entry errors and it ignores any other errors.
    """

    @wraps(func)
    def convert_errors(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.IntegrityError as error:
            error_message = str(error)
            if 'UNIQUE constraint failed' in error_message:
                raise EntryExistsError(f"DB already contains that entry")
            elif 'FOREIGN KEY constraint failed' in error_message:
                raise EntryNotFoundError(f"DB does not contain that entry")

            # Re-raise any ot expected error
            raise

    return convert_errors


# endregion


class EpisodeDB:
    """ Abstraction for the Episode DB """

    TABLES_SCRIPT = Path(resource_filename(__name__, 'tables.sql'))

    def __init__(self, config: Config):
        """
        Initializes the database. It creates the database file if it does
        not exist and creates the necessary tables. If the file already exists
        and the tables are created then nothing changes in the DB.

        :param config: the config instance used to obtain the DB file
        """
        self._config = config

        # Create the DB file and the tables if necessary
        with connect(self) as conn:
            conn.execute_script(self.TABLES_SCRIPT)

    @property
    def db_file(self):
        return self._config.db_file


class Connection:
    """ Abstraction for a connection for the Episode DB """

    # Datetime format used to store timestamps
    DATETIME_FORMAT = "%Y-%m-%d_%H:%M:%S"

    def __init__(self, database: EpisodeDB):
        """
        Initializes a new connection. This initializer should not be called
        from outside of this module.

        :param database: the database to which the connection is referred
        """
        self._conn = sqlite3.connect(database.db_file)

        with self._conn:
            # Enable foreign keys
            self._conn.execute('PRAGMA foreign_keys=ON')

            # Use a row factory to return the query results
            # This allows columns to be accessed by name
            self._conn.row_factory = sqlite3.Row

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def commit(self):
        """ Commits the current transaction """
        self._conn.commit()

    def rollback(self):
        """ Rolls back the current transaction """
        self._conn.rollback()

    def close(self):
        """
        Closes the connection.
        After calling this method the connection is no longer valid.
        """
        self._conn.close()

    # region TV Show Table Methods

    @EntryErrors
    def insert_tvshow(self, tvshow: TVShow, quality: Quality):
        """
        Inserts a new TV Show in the DB. It associates the TV Show with a
        video quality.

        :raise EntryExistsError: if DB already contains a TV show with the
                                 same ID as *tvshow*
        """
        self._conn.cursor().execute(
            'INSERT INTO tvshow VALUES (?, ?, ?)',
            (tvshow.id, tvshow.name, quality.tag))

    def delete_tvshow(self, tvshow_id: str):
        """
        Deletes the TV show with the specified ID from the DB.

        :param tvshow_id: the ID of the TV Show to delete
        :raise EntryNotFoundError: if the DB does not contain a TV Show with
                                   the specified ID
        """
        cursor = self._conn.cursor()
        cursor.execute('DELETE FROM tvshow WHERE id = ?', (tvshow_id,))

        if cursor.rowcount == 0:
            raise EntryNotFoundError(f"DB does not contain TV Show with the "
                                     f"ID {tvshow_id}")

    def tvshows(self):
        """ Yields each TV Show in the DB (including the video quality) """
        cursor = self._conn.cursor()
        cursor.execute('SELECT * FROM tvshow')

        for row in _iter_rows(cursor):
            yield _tvshow_from_row(row)

    def set_tvshow_quality(self, tvshow_id: str, quality: Quality):
        """
        Sets the video quality for the specified TV Show.

        :raise EntryNotFoundError: if the DB does not contain a TV Show with
                                   the specified ID
        """
        cursor = self._conn.cursor()
        cursor.execute('UPDATE tvshow SET quality = ? WHERE id = ?',
                       (quality.tag, tvshow_id))

        if cursor.rowcount == 0:
            raise EntryNotFoundError(f"DB does not contain TV Show with the "
                                     f"ID {tvshow_id}")

    # endregion

    # region Episode Table Methods

    @EntryErrors
    def insert_episode(self, episode: Episode):
        """
        Inserts a new TV Show in the DB. It associates the TV Show with a
        video quality.

        :raise EntryExistsError: if DB already contains *episode*
        :raise EntryNotFoundError: if the DB does not contain the TV Show
                                   this episode belongs to
        """
        self._conn.cursor().execute(
            'INSERT INTO episode VALUES (?, ?, ?, ?, ?)',
            (episode.tvshow.id, episode.season, episode.number,
             episode.title, None))

    def episodes(self, include_state: bool = False):
        """
        Yields each Episode in the DB. If *include_state* is set to true, then
        it yields, for each episode, a tuple including the episode and the
        respective state.
        """
        cursor = self._conn.cursor()
        cursor.execute(
            'SELECT id, name, season, number, title, state '
            'FROM episode JOIN tvshow ON tvshow_id == tvshow.id')

        for row in _iter_rows(cursor):
            if include_state:
                yield _episode_from_row(row), row['state']
            else:
                yield _episode_from_row(row)

    def episodes_from(self, tvshow_id: str):
        """
        Retrieves from the DB all episodes from TV show with ID matching
        *tvshow_id*.

        :param tvshow_id: ID of TV Show to get episodes from
        :return: list containing all episodes
        """
        cursor = self._conn.cursor()
        cursor.execute(
            'SELECT id, name, season, number, title '
            'FROM episode JOIN tvshow ON tvshow_id == tvshow.id '
            'WHERE id = ?', (tvshow_id,))

        return [_episode_from_row(row) for row in _iter_rows(cursor)]

    def set_episode_state(self, episode: Episode, state: State):
        """
        Sets the state of an episode.

        :raise EntryNotFoundError: if the DB does not contain *episode*
        """
        cursor = self._conn.cursor()
        cursor.execute(
            'UPDATE episode SET state = ? '
            'WHERE tvshow_id = ? AND season = ? AND number = ?',
            (state.tag,
             episode.tvshow.id, episode.season, episode.number))

        if cursor.rowcount == 0:
            raise EntryNotFoundError(f"DB does not contain {episode}")

    def episode_exists(self, episode: Episode) -> bool:
        """
        Checks whether the DB contains *episode* or not.

        :param episode: episode to check
        :return: True if DB contains *episode* or False if otherwise
        """
        cursor = self._conn.cursor()
        cursor.execute(
            'SELECT * FROM episode '
            'WHERE tvshow_id = ? AND season = ? AND number = ?',
            (episode.tvshow.id, episode.season, episode.number))

        return cursor.rowcount > 0

    # endregion

    # region File Table Methods

    @EntryErrors
    def insert_file(self, episode: Episode, file: EpisodeFile):
        """
        Inserts a new TV Show in the DB. It associates the TV Show with a
        video quality.

        :param episode: episode to which the *file* corresponds
        :param file:    file to insert
        :raise EntryExistsError: if *episode* is already associated with a file
        :raise EntryNotFoundError: if the DB does not contain *episode*
        """
        self._conn.cursor().execute(
            'INSERT INTO file VALUES (?, ?, ?, ?, ?, ?)',
            (episode.tvshow.id, episode.season, episode.number,
             file.link, file.quality.tag, None))

    def set_download_timestamp(self, episode: Episode, timestamp: datetime):
        """
        Sets the 'download timestamp' for the file associated with *episodes*.

        :param episode:   episode to set download timestamp for
        :param timestamp: timestamp to set
        :raise EntryNotFoundError: if the DB does not contain *episode* or if
                                   no file is specified for it
        """
        cursor = self._conn.cursor()
        cursor.execute(
            'UPDATE file SET download_timestamp = ? '
            'WHERE tvshow_id = ? AND season = ? AND number = ?',
            (episode.tvshow.id, episode.season, episode.number,
             timestamp.strftime(self.DATETIME_FORMAT)))

        if cursor.rowcount == 0:
            raise EntryNotFoundError(f"DB does not contain file for {episode}")

    # endregion

    def execute_script(self, script: Path):
        """ Executes an SQL script """
        with open(script) as file:
            self._conn.cursor().executescript(file.read())


# region Helper Functions


def _iter_rows(cursor):
    """ Yields each row fetchable from a cursor """
    row = cursor.fetchone()
    while row:
        yield row
        row = cursor.fetchone()


def _tvshow_from_row(row) -> (TVShow, Quality):
    return TVShow(row['id'], row['name']), Quality.from_tag(row['quality'])


def _episode_from_row(row) -> Episode:
    return Episode(
        tvshow=TVShow(row['id'], row['name']),
        title=row['title'],
        season=row['season'],
        number=row['number']
    )


# endregion


def connect(db: EpisodeDB) -> Connection:
    """ Returns a connection to the DB """
    return Connection(db)
