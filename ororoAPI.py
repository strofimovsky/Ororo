# -*- coding: utf-8 -*-

'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import base64, os, xbmcaddon, xbmc

import six
from six.moves import urllib_parse, urllib_request, urllib_error

try:    import json
except: import simplejson as json

# TODO: maybe it must be singleton?

class OroroAPI:
    def __init__(self, login=None, password=None):
        self.protocol = 'https://'
        self.url = 'front.ororo-mirror.tv'
        self.api_prefix = '/api/v2'

        if login and password:
            self.set_credentials(login, password)

    def addon_version(self): #TODO: move me to plugin top level
        return xbmcaddon.Addon().getAddonInfo("version")

    def api_url(self):
        return self.url + self.api_prefix

    def base_url_with_credentials(self):
        return self.protocol + '%s:%s@' % (urllib_parse.quote_plus(self.login), urllib_parse.quote_plus(self.password)) + self.url

    def api_with_credentials_url(self):
        return self.protocol + '%s:%s@' % (urllib_parse.quote_plus(self.login), urllib_parse.quote_plus(self.password)) + self.api_url()

    def have_credentials(self):
        return self.login and self.password

    def new_request(self, uri, method, data=None):
        if self.protocol not in uri:
            uri = self.protocol + self.url + self.api_prefix + uri

        request = urllib_request.Request(uri, data)
        request.add_header('Accept', 'application/json')
        request.add_header('Content-Type', 'application/json')
        request.add_header('User-Agent', 'Kodi (%s)' % self.addon_version())

        if self.have_credentials():
            request.add_header("Authorization", "Basic %s" % self.generate_auth_header())

        return request

    def set_credentials(self, login, password):
        self.login = login
        self.password = password

    def generate_auth_header(self):
        text = '%s:%s' % (self.login, self.password)
        if six.PY3:
            text = text.encode('utf-8')

        return base64.b64encode(text).decode('utf-8')

    def make_request(self, uri, method='GET', params=None):
        try:
            return urllib_request.urlopen(self.new_request(uri, method, params))
        except urllib_error.HTTPError as e:
            if e.getcode() == 401:
                code = 30516 # Failed to log in
            elif e.getcode() == 402:
                code = 30318 # Free limit reached
            else:
                code = 30320 # General "Load failed" error

            str = xbmcaddon.Addon().getLocalizedString(code)
            addonIcon = os.path.join(xbmcaddon.Addon().getAddonInfo("path"),'icon.png')
            try: xbmcgui.Dialog().notification(xbmcaddon.Addon().getAddonInfo("name"), str, addonIcon, 3000, sound=False)
            except: xbmc.executebuiltin("Notification(%s,%s, 3000, %s)" % ('Ororo TV', str, addonIcon))

    def get(self, uri, params=None):
        return self.make_request(uri, params=params).read()

    def movies_list(self):
        list = []
        movies = json.loads(self.get('/movies'))
        for movie in movies['movies']: list.append(self.movie_info(movie))

        return list

    def movie(self, movie_id):
        return self.get('/movies/' + str(movie_id))

    def movie_info(self, movie):
        info = {
            'id': movie['id'],
            'title': movie['name'],
            'name': '%s (%s)' % (movie['name'], movie['year']),
            'poster': movie['poster_thumb'],
            'imdb_id': movie['imdb_id'],
            'imdb_rating': movie['imdb_rating'],
            'backdrop_url': movie['backdrop_url'],
            'updated_at': movie['updated_at'],
            'genre': ', '.join(movie['array_genres']),
            'genres': movie['array_genres'],
            'year': movie['year'],
            'desc': movie['desc']
        }

        return info

    def shows_list(self):
        list = []
        shows = json.loads(self.get('/shows'))
        for show in shows['shows']: list.append(self.show_info(show))

        return list

    def show(self, show_id):
        show = json.loads(self.get('/shows/' + str(show_id)))
        return self.show_info(show)

    def show_info(self, show):
        info = {
            'id': show['id'],
            'name': show['name'],
            'title': show['name'],
            'image': show['poster_thumb'],
            'year': show['year'],
            'tmdb': show['tmdb_id'],
            'imdb': show['imdb_id'],
            'imdb_rating': show['imdb_rating'],
            'backdrop_url': show['backdrop_url'],
            'genre': ', '.join(show['array_genres']),
            'genres': show['array_genres'],
            'countries': show['array_countries'],
            'plot': show['desc'],
            'ended': show['ended'],
            'duration': show['length'],
            'newest_video': show['newest_video'],
            'user_popularity': show['user_popularity']
        }

        info['seasons']  = show.get('seasons')
        info['episodes'] = show.get('episodes')

        return info

    def episode(self, episode_id):
        return self.get('/episodes/' + str(episode_id))
