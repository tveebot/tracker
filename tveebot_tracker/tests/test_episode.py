import pytest

from tveebot_tracker.episode import Episode, EpisodeFile, Quality, TVShow
from tveebot_tracker.exceptions import ParseError


@pytest.mark.parametrize(
    "title, expected_season, expected_number, expected_title", [
        ("Prison Break 5x09 Behind The Eyes", 5, 9, "Behind The Eyes"),
        ("Prison Break 5x09", 5, 9, ""),
        ("Prison Break 5x9", 5, 9, ""),
        ("Prison Break 5x9", 5, 9, ""),
        ("Prison Break 05x09", 5, 9, ""),
        ("Wrong Show Name 05x09 Behind The Eyes", 5, 9, "Behind The Eyes"),
        ("Prison Break 1x01A 5x09", 5, 9, ""),
        ("Prison Break A1x01 5x09", 5, 9, ""),
        ("Prison Break 5x09 A1x01", 5, 9, "A1x01"),
        ("5x09 Behind The Eyes", 5, 9, "Behind The Eyes"),
        ("5x09", 5, 9, ""),
        ("Prison Break 5x09 5x10 Behind", 5, 9, "5x10 Behind"),
        # TODO add support for multiple episodes
    ])
def test_ParseEpisodeTitle_ReturnCorrespondingEpisode(
        title, expected_season, expected_number, expected_title):
    file = EpisodeFile(
        TVShow("#1", "Prison Break"),
        title,
        link="magnet://link",
        quality=Quality.SD
    )

    expected_episode = Episode(
        TVShow("#1", "Prison Break"),
        expected_title,
        expected_season,
        expected_number
    )

    assert Episode.from_file(file) == expected_episode


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
    file = EpisodeFile(
        TVShow("#1", "Prison Break"),
        title,
        link="magnet://link",
        quality=Quality.SD
    )

    with pytest.raises(ParseError):
        Episode.from_file(file)
