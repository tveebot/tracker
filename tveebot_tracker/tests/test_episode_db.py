from unittest.mock import MagicMock

from pytest import fixture, raises

from tveebot_tracker.episode import TVShow, Quality
from tveebot_tracker.episode_db import connect, EpisodeDB, EntryExistsError


class TestEpisodeDB:
    @fixture
    def db(self, tmpdir):
        config = MagicMock()
        config.db_file = str(tmpdir.join("episodes.db"))
        # noinspection PyTypeChecker
        return EpisodeDB(config)

    def test_AfterInsertingANewTVShowInDB_TheDBContainsThatTVShow(self, db):
        with connect(db) as conn:
            conn.insert_tvshow(TVShow("#1", "My Show"), Quality.SD)
            conn.commit()

        with connect(db) as conn:
            assert (TVShow("#1", "My Show"), Quality.SD) in conn.tvshows()

    def test_AfterInsertingMultipleNewTVShows_TheDBContainsAllOfThem(self, db):
        tvshows = [
            (TVShow("#1", "My Show 1"), Quality.SD),
            (TVShow("#2", "My Show 2"), Quality.HD),
            (TVShow("#3", "My Show 3"), Quality.FHD),
        ]

        with connect(db) as conn:
            for tvshow, quality in tvshows:
                conn.insert_tvshow(tvshow, quality)
            conn.commit()

        with connect(db) as conn:
            for tvshow, quality in tvshows:
                assert tvshow, quality in conn.tvshows()

    def test_InsertingTVShowsWithSameIDs_RaisesEntryExistsError(self, db):
        with connect(db) as conn:
            conn.insert_tvshow(TVShow("#1", "My Show"), Quality.SD)
            conn.commit()

        with connect(db) as conn:
            with raises(EntryExistsError):
                conn.insert_tvshow(TVShow("#1", "Other Show"), Quality.HD)
