# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from ..compat import compat_str
from ..utils import (
    ExtractorError,
    determine_ext,
    int_or_none,
    parse_iso8601,
    parse_duration,
    remove_start,
)


class NowTVIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?nowtv\.(?:de|at|ch)/(?:rtl|rtl2|rtlnitro|superrtl|ntv|vox)/(?P<id>.+?)/(?:player|preview)'

    _TESTS = [{
        # rtl
        'url': 'http://www.nowtv.de/rtl/bauer-sucht-frau/die-neuen-bauern-und-eine-hochzeit/player',
        'info_dict': {
            'id': '203519',
            'display_id': 'bauer-sucht-frau/die-neuen-bauern-und-eine-hochzeit',
            'ext': 'flv',
            'title': 'Die neuen Bauern und eine Hochzeit',
            'description': 'md5:e234e1ed6d63cf06be5c070442612e7e',
            'thumbnail': 're:^https?://.*\.jpg$',
            'timestamp': 1432580700,
            'upload_date': '20150525',
            'duration': 2786,
        },
        'params': {
            # rtmp download
            'skip_download': True,
        },
    }, {
        # rtl2
        'url': 'http://www.nowtv.de/rtl2/berlin-tag-nacht/berlin-tag-nacht-folge-934/player',
        'info_dict': {
            'id': '203481',
            'display_id': 'berlin-tag-nacht/berlin-tag-nacht-folge-934',
            'ext': 'flv',
            'title': 'Berlin - Tag & Nacht (Folge 934)',
            'description': 'md5:c85e88c2e36c552dfe63433bc9506dd0',
            'thumbnail': 're:^https?://.*\.jpg$',
            'timestamp': 1432666800,
            'upload_date': '20150526',
            'duration': 2641,
        },
        'params': {
            # rtmp download
            'skip_download': True,
        },
    }, {
        # rtlnitro
        'url': 'http://www.nowtv.de/rtlnitro/alarm-fuer-cobra-11-die-autobahnpolizei/hals-und-beinbruch-2014-08-23-21-10-00/player',
        'info_dict': {
            'id': '165780',
            'display_id': 'alarm-fuer-cobra-11-die-autobahnpolizei/hals-und-beinbruch-2014-08-23-21-10-00',
            'ext': 'flv',
            'title': 'Hals- und Beinbruch',
            'description': 'md5:b50d248efffe244e6f56737f0911ca57',
            'thumbnail': 're:^https?://.*\.jpg$',
            'timestamp': 1432415400,
            'upload_date': '20150523',
            'duration': 2742,
        },
        'params': {
            # rtmp download
            'skip_download': True,
        },
    }, {
        # superrtl
        'url': 'http://www.nowtv.de/superrtl/medicopter-117/angst/player',
        'info_dict': {
            'id': '99205',
            'display_id': 'medicopter-117/angst',
            'ext': 'flv',
            'title': 'Angst!',
            'description': 'md5:30cbc4c0b73ec98bcd73c9f2a8c17c4e',
            'thumbnail': 're:^https?://.*\.jpg$',
            'timestamp': 1222632900,
            'upload_date': '20080928',
            'duration': 3025,
        },
        'params': {
            # rtmp download
            'skip_download': True,
        },
    }, {
        # ntv
        'url': 'http://www.nowtv.de/ntv/ratgeber-geld/thema-ua-der-erste-blick-die-apple-watch/player',
        'info_dict': {
            'id': '203521',
            'display_id': 'ratgeber-geld/thema-ua-der-erste-blick-die-apple-watch',
            'ext': 'flv',
            'title': 'Thema u.a.: Der erste Blick: Die Apple Watch',
            'description': 'md5:4312b6c9d839ffe7d8caf03865a531af',
            'thumbnail': 're:^https?://.*\.jpg$',
            'timestamp': 1432751700,
            'upload_date': '20150527',
            'duration': 1083,
        },
        'params': {
            # rtmp download
            'skip_download': True,
        },
    }, {
        # vox
        'url': 'http://www.nowtv.de/vox/der-hundeprofi/buero-fall-chihuahua-joel/player',
        'info_dict': {
            'id': '128953',
            'display_id': 'der-hundeprofi/buero-fall-chihuahua-joel',
            'ext': 'flv',
            'title': "Büro-Fall / Chihuahua 'Joel'",
            'description': 'md5:e62cb6bf7c3cc669179d4f1eb279ad8d',
            'thumbnail': 're:^https?://.*\.jpg$',
            'timestamp': 1432408200,
            'upload_date': '20150523',
            'duration': 3092,
        },
        'params': {
            # rtmp download
            'skip_download': True,
        },
    }, {
        'url': 'http://www.nowtv.de/rtl/bauer-sucht-frau/die-neuen-bauern-und-eine-hochzeit/preview',
        'only_matching': True,
    }, {
        'url': 'http://www.nowtv.at/rtl/bauer-sucht-frau/die-neuen-bauern-und-eine-hochzeit/preview?return=/rtl/bauer-sucht-frau/die-neuen-bauern-und-eine-hochzeit',
        'only_matching': True,
    }, {
        'url': 'http://www.nowtv.de/rtl2/echtzeit/list/aktuell/schnelles-geld-am-ende-der-welt/player',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        display_id = self._match_id(url)
        display_id_split = display_id.split('/')
        if len(display_id) > 2:
            display_id = '/'.join((display_id_split[0], display_id_split[-1]))

        info = self._download_json(
            'https://api.nowtv.de/v3/movies/%s?fields=id,title,free,geoblocked,articleLong,articleShort,broadcastStartDate,seoUrl,duration,format,files' % display_id,
            display_id)

        video_id = compat_str(info['id'])

        files = info['files']
        if not files:
            if info.get('geoblocked', False):
                raise ExtractorError(
                    'Video %s is not available from your location due to geo restriction' % video_id,
                    expected=True)
            if not info.get('free', True):
                raise ExtractorError(
                    'Video %s is not available for free' % video_id, expected=True)

        formats = []
        for item in files['items']:
            if determine_ext(item['path']) != 'f4v':
                continue
            app, play_path = remove_start(item['path'], '/').split('/', 1)
            formats.append({
                'url': 'rtmpe://fms.rtl.de',
                'app': app,
                'play_path': 'mp4:%s' % play_path,
                'ext': 'flv',
                'page_url': 'http://rtlnow.rtl.de',
                'player_url': 'http://cdn.static-fra.de/now/vodplayer.swf',
                'tbr': int_or_none(item.get('bitrate')),
            })
        self._sort_formats(formats)

        title = info['title']
        description = info.get('articleLong') or info.get('articleShort')
        timestamp = parse_iso8601(info.get('broadcastStartDate'), ' ')
        duration = parse_duration(info.get('duration'))

        f = info.get('format', {})
        thumbnail = f.get('defaultImage169Format') or f.get('defaultImage169Logo')

        return {
            'id': video_id,
            'display_id': display_id,
            'title': title,
            'description': description,
            'thumbnail': thumbnail,
            'timestamp': timestamp,
            'duration': duration,
            'formats': formats,
        }
