from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from xml.etree import ElementTree

from tveebot_tracker.episode import Quality, EpisodeFile
from tveebot_tracker.exceptions import ParseError
from tveebot_tracker.source import TVShowNotFoundError


class ShowRSSSource:
    """ Source based on the ShowRSS website """

    SHOW_RSS_URL = "https://showrss.info/show"

    def fetch(self, tvshow_reference: str) -> list:
        """
        Fetches all the episode files available at the source for the specified
        TV show.

        ShowRSS assigns a unique ID to each TV Show. The *tvshow_reference* must
        correspond to that ID. This ID is absolutely necessary to be able to
        fetch the episode file from this source.

        :param tvshow_reference: the TV Show id
        :return: list containing the episode files fetched
        :raise TVShowNotFound: if the specified reference does not match to any
                               TV show available
        :raises ConnectionRefusedError: if it can not connect to ShowRSS
        """
        tvshow_url = "%s/%s.rss" % (self.SHOW_RSS_URL, tvshow_reference)

        try:
            with urlopen(tvshow_url) as response:
                feed = response.read()

        except HTTPError:
            raise TVShowNotFoundError(f"ShowRSS source did not find TV Show "
                                      f"with reference '{tvshow_reference}'")
        except URLError:
            raise ConnectionRefusedError("connection with ShowRSS failed")

        return parse_feed(feed)


def parse_feed(feed: str) -> list:
    """
    Parses a TV Show *feed*, returning the episode files included in that feed.

    :param feed: the feed to parse
    :return: list of episode files included in *feed*
    """
    try:
        root = ElementTree.fromstring(feed)
    except ElementTree.ParseError as error:
        raise ParseError(str(error))

    channel = root.find('channel')

    if channel is None:
        raise ParseError("feed's format is invalid: missing 'channel' element")

    # This function is used multiple times in the loop below
    def attr(item, attribute):
        """ Fetches the text of *attribute* from *item* element """
        attribute = item.find(attribute)

        if attribute is None:
            raise ParseError(f"item is missing required attribute {attribute}")

        return attribute.text

    files = []
    for item in channel.findall('item'):
        item = {
            "title": attr(item, 'title'),
            "link": attr(item, 'link')
        }

        files.append(parse_item(item))

    return files


quality_tags = {
    '720p': Quality.HD,
    '1080p': Quality.FHD,
}


def parse_item(item: dict) -> EpisodeFile:
    """
    Parses an item in some feed, returning the corresponding episode file.

    The *item* argument is a dictionary that must include 2 keys:
      - title, the title of the episode file (including all quality tags)
      - link, the link to download the episode file

    :param item: a dict with the keys specified in the description
    :return: episode file parsed from *item*
    """
    file_quality = Quality.SD  # may change

    words: list = item['title'].split(" ")
    for tag, quality in quality_tags.items():
        try:
            words.remove(tag)
            file_quality = quality
            break
        except ValueError:
            # Tag is not in words
            continue

    # The file title does not include the quality tags
    # Those are removed from 'words' at this point
    file_title = " ".join(words)

    return EpisodeFile(file_title, item['link'], file_quality)

