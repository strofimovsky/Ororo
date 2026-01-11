# -*- coding: utf-8 -*-

'''
    Ororo TV Addon
    Copyright (C) 2014 ororo.tv

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

import re,os,threading,datetime,time,base64,itertools,calendar,re

import six
from six.moves import urllib_parse

from kodi_six import xbmc, xbmcaddon, xbmcgui, xbmcplugin, xbmcvfs

from operator import itemgetter
try:    import json
except: import simplejson as json
try:    import CommonFunctions
except: import commonfunctionsdummy as CommonFunctions

import cache

from ororoAPI import OroroAPI
from contextMenu import contextMenu

def getKodiVersion():
    return int(xbmc.getInfoLabel("System.BuildVersion").split(".")[0])

action              = None
common              = CommonFunctions
transPath           = xbmc.translatePath if getKodiVersion() < 19 else xbmcvfs.translatePath
language            = xbmcaddon.Addon().getLocalizedString
setSetting          = xbmcaddon.Addon().setSetting
getSetting          = xbmcaddon.Addon().getSetting
addonName           = xbmcaddon.Addon().getAddonInfo("name")
addonVersion        = xbmcaddon.Addon().getAddonInfo("version")
addonId             = xbmcaddon.Addon().getAddonInfo("id")
addonPath           = xbmcaddon.Addon().getAddonInfo("path")
addonFullId         = addonName + addonVersion
addonDesc           = language(30450).encode("utf-8")

addonIcon           = os.path.join(addonPath,'icon.png')
addonFanart         = os.path.join(addonPath,'fanart.jpg')
addonArt            = os.path.join(addonPath,'resources/art')
addonGenres         = os.path.join(addonPath,'resources/art/Genres.png')
addonNext           = os.path.join(addonPath,'resources/art/Next.png')
dataPath            = transPath('special://profile/addon_data/%s' % (addonId))
viewData            = os.path.join(dataPath,'views.cfg')
offData             = os.path.join(dataPath,'offset.cfg')
subData             = os.path.join(dataPath,'subscriptions2.cfg')
favData             = os.path.join(dataPath,'favourites2.cfg')

user                = getSetting("user")
password            = getSetting("password")

API                 = OroroAPI(user, password)

class main:
    def __init__(self):
        global action, content_type
        index().container_data()
        params = dict(urllib_parse.parse_qsl(sys.argv[2].replace('?',''))) if len(sys.argv) > 1 else dict()

        action = params.get('action')
        id = params.get('id')
        name = params.get('name')
        content_type = params.get('content_type')
        query = params.get('query')
        genre = params.get('genre')
        season = params.get('season')
        lang = params.get('lang')

        if action == None:                          root().get()
        elif action == 'root_movies':               root().get('movies')
        elif action == 'root_shows':                root().get('shows')
        elif action == 'root_search':               root().search()
        elif action == 'item_play':                 contextMenu(index).item_play()
        elif action == 'item_queue':                contextMenu(index).item_queue()
        elif action == 'item_play_from_here':       contextMenu(index).item_play_from_here(id)
        elif action == 'favourite_add':             contextMenu(index).favourite_add(favData, id, name)
        elif action == 'favourite_delete':          contextMenu(index).favourite_delete(favData, id, name)
        elif action == 'playlist_open':             contextMenu(index).playlist_open()
        elif action == 'settings_open':             contextMenu(index).settings_open()
        elif action == 'addon_home':                contextMenu(index).addon_home()
        elif action == 'library_add':               contextMenu(index).library_add(subData, id, name)
        elif action == 'library_delete':            contextMenu(index).library_delete(subData, id, name)
        elif action == 'library_update':            contextMenu(index).library_update(subData)
        elif action == 'library_service':           contextMenu(index).library_update(subData, silent=True)

        elif action == 'shows_favourites':          favourites().shows()
        elif action == 'shows_subscriptions':       subscriptions().shows()

        elif action == 'shows':                     index().shows()
        elif action == 'movies':                    index().movies()

        elif action == 'movies_title':              index().movies()
        elif action == 'movies_added':              index().movies('added')
        elif action == 'movies_release':            index().movies('release')
        elif action == 'movies_rating':             index().movies('rating')
        elif action == 'movies_genre':              index().movies('genre', genre)
        elif action == 'movies_search':             index().movies('search', query)
        elif action == 'genres_movies':             index().pageList(index().get_genres(index().get_movies()), 'movies')

        elif action == 'shows_title':               index().shows('title')
        elif action == 'shows_release':             index().shows('release')
        elif action == 'shows_rating':              index().shows('rating')
        elif action == 'shows_search':              index().shows('search', query)
        elif action == 'shows_genre':               index().shows('genre', genre)
        elif action == 'genres_shows':              index().pageList(index().get_genres(index().get_shows()), 'shows')

        elif action == 'seasons':                   index().seasons(id)
        elif action == 'episodes':                  index().episodes(id, season)

        elif action == 'play':                      index().resolve(id)
        elif action == 'download':                  index().download(id)
        elif action == 'clear_cache':               index().clearCache()

        elif action == 'search':                    subtitles().search(index)
        elif action == 'download_subtitle':         subtitles().download(url, lang)

        if action is None:
            pass
        elif action.startswith('shows'):
            xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
            index().container_view('tvshows', {'skin.confluence' : 500})
        elif action.startswith('seasons'):
            xbmcplugin.setContent(int(sys.argv[1]), 'seasons')
            index().container_view('seasons', {'skin.confluence' : 500})
        elif action.startswith('episodes'):
            xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
            index().container_view('episodes', {'skin.confluence' : 504})
        elif action.startswith('movies'):
            xbmcplugin.setContent(int(sys.argv[1]), 'movies')
            index().container_view('movies', {'skin.confluence' : 500})
        xbmcplugin.setPluginFanart(int(sys.argv[1]), addonFanart)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        return

class player(xbmc.Player):
    def __init__ (self):
        self.folderPath = xbmc.getInfoLabel('Container.FolderPath')
        self.loadingStarting = time.time()
        xbmc.Player.__init__(self)

    def run(self, info):
        self.__dict__.update(info)

        item = xbmcgui.ListItem(path=self.url)
        meta = {'label': self.name, 'title': self.name} # Fix for playlist name change
        item.setInfo(type="Video", infoLabels=meta)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        for i in range(0, 250):
            try: self.totalTime = self.getTotalTime()
            except: self.totalTime = 0
            if not self.totalTime == 0: continue
            xbmc.sleep(1000)
        if self.totalTime == 0: return

        while True:
            try: self.currentTime = self.getTime()
            except: break
            xbmc.sleep(1000)

    def onPlayBackStarted(self):
        try: self.setSubtitles(self.subtitle)
        except: pass


class index:
    def resolve(self, id):
        try:
            info = self.media_info(id, content_type)

            if getSetting('subtitles') == 'true':
                preferred_lang = xbmc.convertLanguage(getSetting('sublang1'), xbmc.ISO_639_1)
                for subtitle in info['subtitles']:
                    if subtitle['lang'] == preferred_lang:
                        info['subtitle'] = subtitle['url']

            player().run(info)
        except:
            pass

    def media_info(self, id, type):
        return cache.get(self.get_media_info, 2, id, type)

    def get_media_info(self, id, type):
        info = {}

        try:
            if type == 'movies':
                info = json.loads(API.movie(id))
                info['content'] = 'movie'
                info['title']   = info['name']
            else:
                info = json.loads(API.episode(id))
                info['content'] = 'episode'
                info['title']   = info['show_name'] + ' S' + '%02d' % int(info['season']) + 'E' + '%02d' % int(info['number'])
        except:
            pass

        return info

    def clearCache(self):
        try:
            cache.cache_clear_all()
            self.okDialog("The cache has been cleared.")
        except:
            self.okDialog("The cache could not be cleared. Please try again.")

    def infoDialog(self, str, header=addonName):
        try: xbmcgui.Dialog().notification(header, str, addonIcon, 3000, sound=False)
        except: xbmc.executebuiltin("Notification(%s,%s, 3000, %s)" % (header, str, addonIcon))

    def okDialog(self, str, header=addonName):
        xbmcgui.Dialog().ok(header, str)

    def selectDialog(self, list, header=addonName):
        select = xbmcgui.Dialog().select(header, list)
        return select

    def yesnoDialog(self, str, header=addonName):
        answer = xbmcgui.Dialog().yesno(header, str)
        return answer

    def getProperty(self, str):
        property = xbmcgui.Window(10000).getProperty(str)
        return property

    def setProperty(self, str1, str2):
        xbmcgui.Window(10000).setProperty(str1, str2)

    def clearProperty(self, str):
        xbmcgui.Window(10000).clearProperty(str)

    def addon_status(self, id):
        check = xbmcaddon.Addon(id=id).getAddonInfo("name")
        if not check == addonName: return True

    def container_refresh(self):
        xbmc.executebuiltin("Container.Refresh")

    def container_data(self):
        if not xbmcvfs.exists(dataPath):
            xbmcvfs.mkdir(dataPath)
        if not xbmcvfs.exists(favData):
            file = xbmcvfs.File(favData, 'w')
            file.write('')
            file.close()
        if not xbmcvfs.exists(subData):
            file = xbmcvfs.File(subData, 'w')
            file.write('')
            file.close()
        if not xbmcvfs.exists(viewData):
            file = xbmcvfs.File(viewData, 'w')
            file.write('')
            file.close()
        if not xbmcvfs.exists(offData):
            file = xbmcvfs.File(offData, 'w')
            file.write('')
            file.close()

    def container_view(self, content, viewDict):
        try:
            skin = xbmc.getSkinDir()
            file = xbmcvfs.File(viewData)
            read = file.read().replace('\n','')
            file.close()
            view = re.compile('"%s"[|]"%s"[|]"(.+?)"' % (skin, content)).findall(read)[0]
            xbmc.executebuiltin('Container.SetViewMode(%s)' % str(view))
        except:
            try:
                id = str(viewDict[skin])
                xbmc.executebuiltin('Container.SetViewMode(%s)' % id)
            except:
                pass

    def rootList(self, rootList):
        total = len(rootList)
        for i in rootList:
            name = language(i['name']).encode("utf-8")
            image = '%s/%s' % (addonArt, i['image'])
            action = i['action']
            u = '%s?action=%s' % (sys.argv[0], action)

            cm = []
            cm.append((language(30409).encode("utf-8"), 'RunPlugin(%s?action=settings_open)' % (sys.argv[0])))
            cm.append((language(30411).encode("utf-8"), 'RunPlugin(%s?action=addon_home)' % (sys.argv[0])))

            item = xbmcgui.ListItem(name)
            item.setArt({ "icon": image, "thumb": image, "fanart": addonFanart })
            item.setInfo('video', { 'title': name, 'plot': addonDesc })
            item.addContextMenuItems(cm, replaceItems=True)
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=total,isFolder=action!="clear_cache")

    def get_genres(self, list):
        workaround = [] #used to track already existing genres in genres array

        genres = []
        for content in list:
            for genre in content['genres']:
                if genre not in workaround:
                    genres.append({'name': genre, 'image': addonGenres.encode('utf-8')})
                    workaround.append(genre)

        return genres

    def pageList(self, pageList, content_type):
        if pageList == None: return

        total = len(pageList)
        for i in pageList:
            try:
                name, image = i['name'], i['image']
                u = '%s?action=%s_genre&genre=%s' % (sys.argv[0], content_type, urllib_parse.quote_plus(name))

                item = xbmcgui.ListItem(name)
                item.setArt({ "thumb": image, "fanart": addonFanart })
                item.setInfo( type="Video", infoLabels={ "Label": name, "Title": name, "Plot": addonDesc } )
                item.addContextMenuItems([], replaceItems=True)
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=total,isFolder=True)
            except:
                pass

    def get_movies(self):
        return cache.get(API.movies_list, 24)

    def movies(self, sort_by='title', search_query=None):
        movie_list = self.get_movies()

        if sort_by =='release':
            movie_list = sorted(movie_list, key=itemgetter('year'), reverse=True)
        if sort_by == 'added':
            movie_list = sorted(movie_list, key=itemgetter('updated_at'), reverse=True)
        if sort_by == 'rating':
            movie_list = sorted(movie_list, key=itemgetter('imdb_rating'), reverse=True)
        if sort_by == 'genre':
            movie_list = [i for i in movie_list if search_query in i['genres']]
        if sort_by == 'search':
            if search_query is None:
                search_query = common.getUserInput(language(30362).encode("utf-8"), '')
            if not (search_query is None or search_query == ''):
                search_query = search_query.split(' ')
                movie_list = [i for i in movie_list if all(x.lower() in i['name'].lower() for x in search_query)]

        self.movieList(movie_list)

    def movieList(self, movieList):
        if movieList == None: return

        for movie in movieList:
            try:
                id = movie['id']
                title = movie['title']

                u = '%s?action=play&id=%s&content_type=movies' % (sys.argv[0], id)
                meta = {'mediatype': 'movie', 'title': title, 'year': movie['year'], 'imdbnumber': 'tt' + movie['imdb_id'], 'genre' : movie['genre'], 'plot': movie['desc']}

                try: fanart = movie['backdrop_url']
                except: fanart = addonFanart

                cm = []
                cm.append((language(30401).encode("utf-8"), 'RunPlugin(%s?action=item_play)' % (sys.argv[0])))
                cm.append((language(30436).encode("utf-8"), 'Action(ToggleWatched)'))
                cm.append((language(30406).encode("utf-8"), 'RunPlugin(%s?action=download&content_type=movies&id=%s)' % (sys.argv[0], id)))
                cm.append((language(30434).encode("utf-8"), 'Action(Info)'))
                cm.append((language(30410).encode("utf-8"), 'RunPlugin(%s?action=playlist_open)' % (sys.argv[0])))
                cm.append((language(30409).encode("utf-8"), 'RunPlugin(%s?action=settings_open)' % (sys.argv[0])))
                cm.append((language(30411).encode("utf-8"), 'RunPlugin(%s?action=addon_home)' % (sys.argv[0])))
                item = xbmcgui.ListItem(title)
                item.setArt({ "thumb": movie['poster'], "icon": "DefaultVideo.png", "fanart": fanart })
                item.setInfo(type="Video", infoLabels=meta)
                item.setProperty("IsPlayable", "true")
                item.setProperty("Video", "true")
                item.addContextMenuItems(cm, replaceItems=True)
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=len(movieList),isFolder=False)
            except:
                pass

    def get_shows(self):
        return cache.get(API.shows_list, 24)

    def sort_shows(self, shows, sort_by='title', search_query=None):
        show_list = shows

        if sort_by =='release':
            show_list = sorted(show_list, key=itemgetter('newest_video'), reverse=True)
        if sort_by == 'title':
            show_list = sorted(show_list, key=itemgetter('name'))
        if sort_by == 'rating':
            show_list = sorted(show_list, key=itemgetter('imdb_rating'), reverse=True)
        if sort_by == 'genre':
            show_list = [i for i in show_list if search_query in i['genres']]
        if sort_by == 'search':
            if search_query is None:
                search_query = common.getUserInput(language(30362).encode("utf-8"), '')
            if not (search_query is None or search_query == ''):
                search_query = search_query.split(' ')
                show_list = [i for i in show_list if all(x.lower() in i['name'].lower() for x in search_query)]

        return show_list

    def shows(self, sort_by='title', search_query=None):
        show_list = self.get_shows()
        print(show_list)
        show_list = self.sort_shows(show_list, sort_by, search_query)
        self.showList(show_list)

    def getWatchedEpisodes(self, show_name):
        """Query Kodi's database for watched episodes of a show"""
        try:
            request = {
                "jsonrpc": "2.0",
                "method": "VideoLibrary.GetEpisodes",
                "params": {
                    "filter": {"field": "tvshow", "operator": "is", "value": show_name},
                    "properties": ["playcount"]
                },
                "id": 1
            }
            response = json.loads(xbmc.executeJSONRPC(json.dumps(request)))
            if 'result' in response and 'episodes' in response['result']:
                return sum(1 for ep in response['result']['episodes'] if ep.get('playcount', 0) > 0)
        except:
            pass
        return 0

    def showList(self, showList, show_episode_counts=False):
        if showList == None: return

        file = xbmcvfs.File(favData)
        favRead = file.read()
        file.close()
        file = xbmcvfs.File(subData)
        subRead = file.read()
        file.close()

        # For favourites/subscriptions, fetch episode counts
        is_favourites_or_subs = action in ['shows_favourites', 'shows_subscriptions']

        for show in showList:
            try:
                id = show['id']
                sysname = urllib_parse.quote_plus(show['name'])
                display_name = show['name']

                # For favourites/subscriptions, show total episode count
                if is_favourites_or_subs:
                    try:
                        show_details = self.get_show(id)
                        total_episodes = len(show_details.get('episodes', []))
                        if total_episodes > 0:
                            display_name = '%s (%d episodes)' % (show['name'], total_episodes)
                    except:
                        pass

                u = '%s?action=seasons&id=%s' % (sys.argv[0], id)
                meta = {'mediatype': 'tvshow', 'title': show['name'], 'tvshowtitle': show['name'], 'year' : show['year'], 'imdbnumber': 'tt' + show['imdb'], 'genre' : show['genre'], 'plot': show['plot']}

                try: fanart = show['backdrop_url']
                except: fanart = addonFanart

                cm = []
                cm.append((language(30401).encode("utf-8"), 'RunPlugin(%s?action=item_play)' % (sys.argv[0])))
                cm.append((language(30413).encode("utf-8"), 'Action(Info)'))

                if action == 'shows_subscriptions':
                    cm.append((language(30425).encode("utf-8"), 'RunPlugin(%s?action=library_update)' % (sys.argv[0])))
                    cm.append((language(30424).encode("utf-8"), 'RunPlugin(%s?action=library_delete&id=%s&name=%s)' % (sys.argv[0], id, sysname)))
                else:
                    if not '"%s"' % show['id'] in subRead: cm.append((language(30423).encode("utf-8"), 'RunPlugin(%s?action=library_add&id=%s&name=%s)' % (sys.argv[0], id, sysname)))
                    else: cm.append((language(30424).encode("utf-8"), 'RunPlugin(%s?action=library_delete&id=%s&name=%s)' % (sys.argv[0], id, sysname)))

                if action == 'shows_favourites':
                    cm.append((language(30418).encode("utf-8"), 'RunPlugin(%s?action=favourite_delete&id=%s&name=%s)' % (sys.argv[0], id, sysname)))
                else:
                    if not '"%s"' % show['id'] in favRead: cm.append((language(30417).encode("utf-8"), 'RunPlugin(%s?action=favourite_add&id=%s&name=%s)' % (sys.argv[0], id, sysname)))
                    else: cm.append((language(30418).encode("utf-8"), 'RunPlugin(%s?action=favourite_delete&id=%s&name=%s)' % (sys.argv[0], id, sysname)))

                cm.append((language(30410).encode("utf-8"), 'RunPlugin(%s?action=playlist_open)' % (sys.argv[0])))
                cm.append((language(30409).encode("utf-8"), 'RunPlugin(%s?action=settings_open)' % (sys.argv[0])))
                cm.append((language(30411).encode("utf-8"), 'RunPlugin(%s?action=addon_home)' % (sys.argv[0])))

                item = xbmcgui.ListItem(display_name)
                item.setArt({ "thumb": show['image'], "icon": "DefaultVideo.png", "fanart": fanart })
                item.setInfo(type="Video", infoLabels=meta)
                item.setProperty("IsPlayable", "true")
                item.setProperty("Video", "true")
                item.addContextMenuItems(cm, replaceItems=True)
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=len(showList),isFolder=True)
            except:
                pass

    def get_show(self, show_id):
        return cache.get(API.show, 2, show_id)

    def get_seasons(self, show):
        list = []

        try:
            for i in range(show['seasons']):
                season = i + 1
                list.append({
                    'season': season,
                    'name': 'Season %d' % season
                })
        except:
            pass

        return sorted(list, key=itemgetter('season'))

    def seasons(self, show_id):
        show = self.get_show(show_id)
        self.seasonList(self.get_seasons(show), show)

    def seasonList(self, seasonList, show):
        if seasonList == None: return

        try: fanart = show['backdrop_url']
        except: fanart = addonFanart

        # Get all episodes for counting
        all_episodes = self.get_episodes(show)

        for season in seasonList:
            try:
                season_num = season['season']
                display_name = season['name']

                # Count total episodes in this season
                season_episodes = [ep for ep in all_episodes if ep['season'] == season_num]
                total_in_season = len(season_episodes)

                # Show episode count as "(X episodes)" - Kodi handles watched status natively
                if total_in_season > 0:
                    display_name = '%s (%d episodes)' % (season['name'], total_in_season)

                u = '%s?action=episodes&id=%s&season=%i' % (sys.argv[0], show['id'], season_num)

                cm = []
                cm.append((language(30401).encode("utf-8"), 'RunPlugin(%s?action=item_play)' % (sys.argv[0])))
                cm.append((language(30404).encode("utf-8"), 'RunPlugin(%s?action=item_queue)' % (sys.argv[0])))
                cm.append((language(30410).encode("utf-8"), 'RunPlugin(%s?action=playlist_open)' % (sys.argv[0])))
                cm.append((language(30409).encode("utf-8"), 'RunPlugin(%s?action=settings_open)' % (sys.argv[0])))
                cm.append((language(30411).encode("utf-8"), 'RunPlugin(%s?action=addon_home)' % (sys.argv[0])))

                item = xbmcgui.ListItem(display_name)
                item.setArt({ "thumb": show['image'], "icon": "DefaultVideo.png", "fanart": fanart })
                item.setProperty("IsPlayable", "true")
                item.setProperty("Video", "true")
                item.addContextMenuItems(cm, replaceItems=True)
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=len(seasonList),isFolder=True)
            except:
                pass

    def get_episodes(self, show, season = None):
        list = []

        for episode in show['episodes']:
            if season == None or episode['season'] == int(season):
                list.append(
                    {
                        'id': episode['id'],
                        'name': show['name'] + ' S' + '%02d' % int(episode['season']) + 'E' + '%02d' % int(episode['number']),
                        'title': episode['name'] or 'Episode',
                        'date': episode['airdate'],
                        'plot': episode['plot'],
                        'season': episode['season'],
                        'number': episode['number'],
                        'resolution': episode['resolution'],
                        'sort': '%10d' % int(episode['number'])
                    }
                )

        list = sorted(list, key=itemgetter('sort'))

        return list

    def episodes(self, show_id, season):
        show = self.get_show(show_id)
        episodes = self.get_episodes(show, season)
        self.episodeList(episodes, show)

    def episodeList(self, episodeList, show):
        if episodeList == None: return

        try: fanart = show['backdrop_url']
        except: fanart = addonFanart

        for episode in episodeList:
            try:
                id = episode['id']
                title = episode['title']
                number = episode['number']
                season = episode['season']

                try: duration = int(show['duration']) * 60
                except: duration = 0

                u = '%s?action=play&id=%s&content_type=shows' % (sys.argv[0], id)
                meta = {'title': title, 'tvshowtitle': show['name'], 'season': season, 'episode': number, 'premiered': episode['date'], 'plot': episode['plot'], 'duration': duration }
                
                label = str(season) + 'x' + '%02d' % int(number) + '. ' + title

                cm = []
                cm.append((language(30405).encode("utf-8"), 'RunPlugin(%s?action=item_queue)' % (sys.argv[0])))
                cm.append((language(30436).encode("utf-8"), 'Action(ToggleWatched)'))
                cm.append((language(30403).encode("utf-8"), 'RunPlugin(%s?action=item_play_from_here&id=%s)' % (sys.argv[0], id)))
                cm.append((language(30406).encode("utf-8"), 'RunPlugin(%s?action=download&content_type=shows&id=%s)' % (sys.argv[0], id)))
                cm.append((language(30414).encode("utf-8"), 'Action(Info)'))
                cm.append((language(30410).encode("utf-8"), 'RunPlugin(%s?action=playlist_open)' % (sys.argv[0])))
                cm.append((language(30409).encode("utf-8"), 'RunPlugin(%s?action=settings_open)' % (sys.argv[0])))
                cm.append((language(30411).encode("utf-8"), 'RunPlugin(%s?action=addon_home)' % (sys.argv[0])))

                item = xbmcgui.ListItem(label)
                item.setArt({ "thumb": fanart, "icon": "DefaultVideo.png", "fanart": fanart })
                item.setInfo(type="Video", infoLabels=meta)
                item.setProperty("IsPlayable", "true")
                item.setProperty("Video", "true")
                item.addContextMenuItems(cm, replaceItems=True)
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=len(episodeList),isFolder=False)
            except:
                pass

    def download(self, id):
        try:
            info = self.media_info(id, content_type)
            name = info['title']
        except:
            return

        try:
            url = info['download_url']
        except:
            # Subscription required
            str = xbmcaddon.Addon().getLocalizedString(30319).encode('utf-8')
            addonIcon = os.path.join(xbmcaddon.Addon().getAddonInfo("path"),'icon.png')
            xbmcgui.Dialog().notification('Ororo TV', str, addonIcon, 3000)
            return

        try:
            property = (xbmcaddon.Addon().getAddonInfo("name")+name)+'download'
            download = transPath(xbmcaddon.Addon().getSetting("downloads"))
            dataPath = transPath('special://profile/addon_data/%s' % (xbmcaddon.Addon().getAddonInfo("id")))
            enc_name = re.sub(r'[\\/:*?"<>|]', '', name)
            xbmcvfs.mkdir(dataPath)
            xbmcvfs.mkdir(download)

            file = [i for i in xbmcvfs.listdir(download)[1] if i.startswith(enc_name + '.')]
            if not file == []: file = os.path.join(download, file[0])
            else: file = None
            if download == '':
              yes = self.yesnoDialog(xbmcaddon.Addon().getLocalizedString(30341).encode("utf-8") + '[CR]' + xbmcaddon.Addon().getLocalizedString(30342).encode("utf-8"))
              if yes: contextMenu(index).settings_open()
              return

            if file is None:
              pass
            elif not file.endswith('.tmp'):
              yes = self.yesnoDialog(xbmcaddon.Addon().getLocalizedString(30343).encode("utf-8") + '[CR]' + xbmcaddon.Addon().getLocalizedString(30344).encode("utf-8"), name)
              if yes:
                  xbmcvfs.delete(file)
              else:
                  return
            elif file.endswith('.tmp'):
              if self.getProperty(property) == 'open':
                  yes = self.yesnoDialog(xbmcaddon.Addon().getLocalizedString(30345).encode("utf-8") + '[CR]' + xbmcaddon.Addon().getLocalizedString(30346).encode("utf-8"), name)
                  if yes: self.setProperty(property, 'cancel')
                  return
              else:
                  xbmcvfs.delete(file)

            if info['url'] is None: return
            stream = os.path.join(download, enc_name + '.mp4')
            temp = stream + '.tmp'

            count = 0
            CHUNK = 16 * 1024

            response = API.make_request(url)
            size = response.info()["Content-Length"]

            file = xbmcvfs.File(temp, 'w')
            self.setProperty(property, 'open')
            self.infoDialog(xbmcaddon.Addon().getLocalizedString(30308).encode("utf-8"), name)
            while True:
              chunk = response.read(CHUNK)
              if not chunk: break
              if self.getProperty(property) == 'cancel': raise Exception()
              if xbmc.Monitor().abortRequested() == True: raise Exception()
              part = xbmcvfs.File(temp)
              quota = int(100 * float(part.size())/float(size))
              part.close()
              if not count == quota and count in [0,10,20,30,40,50,60,70,80,90]:
                self.infoDialog(xbmcaddon.Addon().getLocalizedString(30309).encode("utf-8") + str(count) + '%', name)
              file.write(chunk)
              count = quota
            response.close()
            file.close()

            self.clearProperty(property)
            xbmcvfs.rename(temp, stream)
            self.infoDialog(xbmcaddon.Addon().getLocalizedString(30310).encode("utf-8"), name)
        except:
            file.close()
            self.clearProperty(property)
            xbmcvfs.delete(temp)
            sys.exit()
            return


class subscriptions:
    def __init__(self):
        self.list = []

    def shows(self):
        file = xbmcvfs.File(subData)
        read = file.read()
        file.close()

        shows = index().get_shows()
        match = [i.strip('\r\n').strip('"').split('"|"') for i in read.splitlines(True)]
        for i in match:
            # Support old format and fix None id by searching for imdb_id
            try:
              show = next(obj for obj in shows if i[0] == str(obj['id']) or i[0] == obj['name'] or (len(i) >= 4 and i[3] == obj['imdb']))
            except:
              continue

            if show not in self.list: self.list.append(show)

        self.list = sorted(self.list, key=itemgetter('name'))
        index().showList(self.list)

class favourites:
    def __init__(self):
        self.list = []

    def shows(self):
        file = xbmcvfs.File(favData)
        read = file.read()
        file.close()

        shows = index().get_shows()
        match = [i.strip('\r\n').strip('"').split('"|"') for i in read.splitlines(True)]
        for i in match:
            # Support old format and fix None id by searching for imdb_id
            try:
              show = next(obj for obj in shows if i[0] == str(obj['id']) or i[0] == obj['name'] or (len(i) >= 4 and i[3] == obj['imdb']))
            except:
              continue

            if show not in self.list: self.list.append(show)

        if getSetting("fav_sort") == '0':
            self.list = sorted(self.list, key=itemgetter('name'))
        elif getSetting("fav_sort") == '1':
            filter = []
            self.list = sorted(self.list, key=itemgetter('name'))
            filter += [i for i in self.list if not i['ended']]
            filter += [i for i in self.list if i['ended']]
            self.list = filter

        index().showList(self.list)


class subtitles:
    def search(self, index):
        try:
            id = re.search('\/(\d+)', xbmc.Player().getPlayingFile().decode('utf-8')).group(1)
            show = xbmc.getInfoLabel("VideoPlayer.TVshowtitle")
            if show == '': type = 'movies'
            else: type = 'shows'

            info = index().media_info(id, type)
            for subtitle in info['subtitles']:
                url = 'plugin://%s/?action=download_subtitle&url=%s&lang=%s' % (addonId, subtitle['url'], subtitle['lang'])
                listitem = xbmcgui.ListItem(label=subtitle['lang'], label2=info['name'])
                listitem.setArt({ "thumb": subtitle['lang'] })
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
        except:
            pass

    def download(self, url, lang):
        content = API.get(url)

        subtitle = transPath('special://temp/')
        subtitle = os.path.join(subtitle, 'TemporarySubs.%s.srt' % lang)
        file = open(subtitle, 'wb')
        file.write(content)
        file.close()

        listitem = xbmcgui.ListItem(label=subtitle)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

        return subtitle


class root:
    def __init__(self):
        if user == '' or password == '': self.openSettings(addonId)
    def get(self, content_type=None):
        rootList = []
        if content_type == "movies":
            rootList.append({'name': 30501, 'image': 'Title.png', 'action': 'movies_title'})
            rootList.append({'name': 30500, 'image': 'Added.png', 'action': 'movies_added'})
            rootList.append({'name': 30502, 'image': 'Release.png', 'action': 'movies_release'})
            rootList.append({'name': 30503, 'image': 'Rating.png', 'action': 'movies_rating'})
            rootList.append({'name': 30504, 'image': 'Genres.png', 'action': 'genres_movies'})
            rootList.append({'name': 30507, 'image': 'Search.png', 'action': 'movies_search'})
        elif content_type == "shows":
            rootList.append({'name': 30501, 'image': 'Title.png', 'action': 'shows_title'})
            rootList.append({'name': 30502, 'image': 'Release.png', 'action': 'shows_release'})
            rootList.append({'name': 30503, 'image': 'Rating.png', 'action': 'shows_rating'})
            rootList.append({'name': 30504, 'image': 'Genres.png', 'action': 'genres_shows'})
            rootList.append({'name': 30505, 'image': 'Favourites.png', 'action': 'shows_favourites'})
            rootList.append({'name': 30506, 'image': 'Subscriptions.png', 'action': 'shows_subscriptions'})
            rootList.append({'name': 30507, 'image': 'Search.png', 'action': 'shows_search'})
        else:
            cache.cache_version_check()
            rootList.append({'name': 30508, 'image': 'Movies.png', 'action': 'root_movies'})
            rootList.append({'name': 30509, 'image': 'Shows.png', 'action': 'root_shows'})
            rootList.append({'name': 30515, 'image': 'Subscriptions.png', 'action': 'clear_cache'})

        index().rootList(rootList)

    def openSettings(self, id=addonId):
        try:
            xbmc.executebuiltin('Dialog.Close(busydialog)')
            xbmc.executebuiltin('Addon.OpenSettings(%s)' % id)
            xbmc.executebuiltin("XBMC.Container.Update(addons://sources/video/,replace)")
        except:
            return

main()
