from unittest.mock import MagicMock

from pytest import fixture, raises

from tveebot_tracker.episode import TVShow, Quality, Episode
from tveebot_tracker.episode_db import connect, EpisodeDB, EntryExistsError, \
    EntryNotFoundError


class TestEpisodeDB:
    @fixture
    def db(self, tmpdir):
        config = MagicMock()
        config.db_file = str(tmpdir.join("episodes.db"))
        # noinspection PyTypeChecker
        return EpisodeDB(config)

    @fixture
    def conn(self, db):
        with connect(db) as conn:
            yield conn

    def test_AfterInsertingANewTVShowInDB_TheDBContainsThatTVShow(self, conn):
        conn.insert_tvshow(TVShow("#1", "My Show"), Quality.SD)

        assert (TVShow("#1", "My Show"), Quality.SD) in conn.tvshows()

    def test_AfterInsertingMultipleNewTVShows_TheDBContainsAllOfThem(
            self, conn):
        tvshows = [
            (TVShow("#1", "My Show 1"), Quality.SD),
            (TVShow("#2", "My Show 2"), Quality.HD),
            (TVShow("#3", "My Show 3"), Quality.FHD),
        ]

        for tvshow, quality in tvshows:
            conn.insert_tvshow(tvshow, quality)

        for tvshow, quality in tvshows:
            assert tvshow, quality in conn.tvshows()

    def test_InsertingTVShowsWithSameIDs_RaisesEntryExistsError(self, conn):
        conn.insert_tvshow(TVShow("#1", "My Show"), Quality.SD)

        with raises(EntryExistsError):
            conn.insert_tvshow(TVShow("#1", "Other Show"), Quality.HD)

    def test_AfterDeletingAnExistingTVShow_TheDBDoesNotContainThatTVShow(
            self, conn):
        tvshow = TVShow("#1", "My Show"), Quality.SD
        conn.insert_tvshow(*tvshow)

        conn.delete_tvshow("#1")

        assert tvshow not in conn.tvshows()

    def test_AfterDeletingAllButOneTVShow_TheDBContainsOnlyThatTVShow(
            self, conn):
        tvshows = [
            (TVShow("#1", "My Show 1"), Quality.SD),
            (TVShow("#2", "My Show 2"), Quality.HD),
            (TVShow("#3", "My Show 3"), Quality.FHD),
            (TVShow("#4", "My Show 4"), Quality.FHD),
        ]
        for tvshow, quality in tvshows:
            conn.insert_tvshow(tvshow, quality)

        # Delete all except the last tv show
        for tvshow, _ in tvshows[:-1]:
            conn.delete_tvshow(tvshow.id)

        assert [tvshows[-1]] == list(conn.tvshows())

    def test_DeletingTVShowNotInDB_RaisesEntryNotFoundError(self, conn):
        conn.insert_tvshow(TVShow("#1", "My Show"), Quality.SD)
        conn.insert_tvshow(TVShow("#2", "My Show"), Quality.SD)

        with raises(EntryNotFoundError):
            conn.delete_tvshow(tvshow_id="#3")

    def test_SettingTVShowQualityFromSDToHD_ThatTVShowsQualityIsHD(self, conn):
        conn.insert_tvshow(TVShow("#1", "My Show 1"), Quality.SD)
        conn.insert_tvshow(TVShow("#2", "My Show 2"), Quality.SD)

        conn.set_tvshow_quality("#1", Quality.HD)

        assert TVShow("#1", "My Show 1"), Quality.HD in conn.tvshows()
        assert TVShow("#2", "My Show 2"), Quality.SD in conn.tvshows()

    def test_SettingQualityForNonExistingTVShow_RaisesEntryNotFoundError(
            self, conn):
        conn.insert_tvshow(TVShow("#1", "My Show 1"), Quality.SD)
        conn.insert_tvshow(TVShow("#2", "My Show 2"), Quality.SD)

        with raises(EntryNotFoundError):
            conn.set_tvshow_quality("#3", Quality.HD)

    def test_AfterInsertingAnEpisode_TheDBContainsThatEpisode(self, conn):
        conn.insert_tvshow(TVShow("#1", "My Show"), Quality.SD)
        episode = Episode(
            tvshow=TVShow('#1', 'My Show'),
            title="My Title",
            season=1,
            number=2
        )

        conn.insert_episode(episode)

        assert episode in conn.episodes()

    def test_InsertingAnEpisodeAlreadyInTheDB_RaisesEntryExistsError(
            self, conn):
        conn.insert_tvshow(TVShow("#1", "My Show"), Quality.SD)
        episode = Episode(
            tvshow=TVShow('#1', 'My Show'),
            title="My Title",
            season=1,
            number=2
        )
        conn.insert_episode(episode)

        with raises(EntryExistsError):
            conn.insert_episode(episode)

    def test_InsertingAnEpisodeWithoutAMatchingTVShow_RaisesEntryExistsError(
            self, conn):
        episode = Episode(
            tvshow=TVShow('#1', 'My Show'),
            title="My Title",
            season=1,
            number=2
        )

        with raises(EntryNotFoundError):
            conn.insert_episode(episode)
