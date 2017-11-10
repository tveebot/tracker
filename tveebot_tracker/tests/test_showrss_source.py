import pytest

from tveebot_tracker.episode import EpisodeFile, Quality
from tveebot_tracker.exceptions import ParseError
from tveebot_tracker.showrss_source import parse_item, parse_feed


@pytest.mark.parametrize("feed, expected_files", [
    (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<rss version="2.0" xmlns:tv="https://showrss.info">'
            '<channel>'
            '</channel>'
            '</rss>',
            []
    ),
    (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<rss version="2.0" xmlns:tv="https://showrss.info">'
            '<channel>'
            '<description>showRSS show feed for Prison Break</description>'
            '<item>'
            '<title>Prison Break 5x09 720p</title>'
            '<link>magnet_link1</link>'
            '<pubDate>Wed, 31 May 2017 01:50:08 +0000</pubDate>'
            '</item>'
            '<item>'
            '<title>Prison Break 5x10</title>'
            '<link>magnet_link2</link>'
            '<pubDate>Wed, 31 May 2017 01:50:08 +0000</pubDate>'
            '</item>'
            '</channel>'
            '</rss>',
            [
                EpisodeFile("Prison Break 5x09", "magnet_link1", Quality.HD),
                EpisodeFile("Prison Break 5x10", "magnet_link2", Quality.SD),
            ]
    ),
])
def test_ParseFeed_ReturnsCorrespondingEpisodeFiles(feed, expected_files):
    assert parse_feed(feed) == expected_files


@pytest.mark.parametrize("feed", [
    '',

    '<?xml version="1.0" encoding="UTF-8"?>'
    '<rss version="2.0" xmlns:tv="https://showrss.info">'
    # Missing channel element
    '<item>'
    '<title>Prison Break 5x09 720p</title>'
    '<link>magnet_link1</link>'
    '<pubDate>Wed, 31 May 2017 01:50:08 +0000</pubDate>'
    '</item>'
    '<item>'
    '<title>Prison Break 5x10</title>'
    '<link>magnet_link2</link>'
    '<pubDate>Wed, 31 May 2017 01:50:08 +0000</pubDate>'
    '</item>'
    '</rss>',
])
def test_ParseFeed_RaisesParseError(feed):
    with pytest.raises(ParseError):
        parse_feed(feed)


@pytest.mark.parametrize("title, expected_title, expected_quality", [
    ("Prison Break 5x09", "Prison Break 5x09", Quality.SD),
    ("Prison Break 5x09 720", "Prison Break 5x09 720", Quality.SD),
    ("Prison Break 5x09 720p", "Prison Break 5x09", Quality.HD),
    ("Prison Break 5x09 1080", "Prison Break 5x09 1080", Quality.SD),
    ("Prison Break 5x09 1080p", "Prison Break 5x09", Quality.FHD),
    ("Prison Break 5x09 1080P", "Prison Break 5x09 1080P", Quality.SD),
    ("Prison Break 5x09 1080pA", "Prison Break 5x09 1080pA", Quality.SD),
    ("Prison Break 5x09 PROPER", "Prison Break 5x09 PROPER", Quality.SD),
    ("Prison Break 5x09 720p PROPER", "Prison Break 5x09 PROPER", Quality.HD),
    ("Prison Break 5x09 1080p PROPER", "Prison Break 5x09 PROPER", Quality.FHD),
    ("Prison Break 5x09 720p REPACK", "Prison Break 5x09 REPACK", Quality.HD),
    ("Prison Break 5x09 1080p REPACK", "Prison Break 5x09 REPACK", Quality.FHD),
    ("Prison Break 5x09 720p TBA", "Prison Break 5x09 TBA", Quality.HD),
    ("Prison Break 5x09 1080p TBA", "Prison Break 5x09 TBA", Quality.FHD),
    ("", "", Quality.SD),
])
def test_ParseItem_ReturnCorrespondingEpisodeFile(
        title, expected_title, expected_quality):
    item = {
        'title': title,
        'link': 'magnet://link'
    }

    assert parse_item(item) == EpisodeFile(expected_title, 'magnet://link',
                                           expected_quality)
