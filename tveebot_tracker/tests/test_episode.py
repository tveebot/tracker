import pytest

from tveebot_tracker.episode import Episode, TVShow
from tveebot_tracker.exceptions import ParseError


@pytest.mark.parametrize(
    "title, expected_tvshow_name, expected_season, expected_number, "
    "expected_title", [
        ("Prison Break 5x09 Behind Eyes", "Prison Break", 5, 9, "Behind Eyes"),
        ("Prison Break 5x09", "Prison Break", 5, 9, ""),
        ("Prison Break 5x9", "Prison Break", 5, 9, ""),
        ("Prison Break 5x9", "Prison Break", 5, 9, ""),
        ("Prison Break 05x09", "Prison Break", 5, 9, ""),
        ("Another Name 05x09", "Another Name", 5, 9, ""),
        ("Prison Break 1x01A 5x09", "Prison Break 1x01A", 5, 9, ""),
        ("Prison Break A1x01 5x09", "Prison Break A1x01", 5, 9, ""),
        ("Prison Break 5x09 A1x01", "Prison Break", 5, 9, "A1x01"),
        ("5x09 Behind The Eyes", "", 5, 9, "Behind The Eyes"),
        ("5x09", "", 5, 9, ""),
        ("Prison Break 5x09 5x10 Behind", "Prison Break", 5, 9, "5x10 Behind"),
        # TODO add support for multiple episodes
    ])
def test_ParseEpisodeTitle_ReturnCorrespondingEpisode(
        title, expected_tvshow_name, expected_season, expected_number,
        expected_title):

    expected_episode = Episode(
        TVShow("#1", expected_tvshow_name),
        expected_title,
        expected_season,
        expected_number
    )

    assert Episode.from_title(title, tvshow_id="#1") == expected_episode


@pytest.mark.parametrize("title", [
    "",
    "Prison Break",
    "Prison Break 720p",
    "Prison Break AxAA",
    "Prison Break 5xA",
    "Prison Break Ax09",
    "Prison Break A5x09",
    "Prison Break 5x09A",
    "Prison Break 5x09x10",
])
def test_ParseEpisodeTitle_RaisesParseError(title):

    with pytest.raises(ParseError):
        Episode.from_title(title, tvshow_id="#1")
