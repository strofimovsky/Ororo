# -*- coding: utf-8 -*-

'''
    Copyright (C) 2015 ororo.tv

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

import xbmc,xbmcplugin,xbmcgui,xbmcaddon,xbmcvfs,sys,os,base64,re

import six
from six.moves import urllib_parse

addonId = xbmcaddon.Addon().getAddonInfo("id")

class contextMenu:
    def __init__(self, indexClass):
        self.index = indexClass

    def item_play(self):
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        xbmc.executebuiltin('Action(Queue)')
        playlist.unshuffle()
        xbmc.Player().play(playlist)

    def item_queue(self):
        xbmc.executebuiltin('Action(Queue)')

    def item_play_from_here(self, id):
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        playlist.unshuffle()
        total = xbmc.getInfoLabel('Container.NumItems')
        for i in range(0, int(total)):
            i = str(i)
            label = xbmc.getInfoLabel('ListItemNoWrap(%s).label' % i)
            if label == '': break

            params = {}
            path = xbmc.getInfoLabel('ListItemNoWrap(%s).FileNameAndPath' % i)
            path = urllib_parse.quote_plus(path).replace('+%26+', '+&+')
            query = path.split('%3F', 1)[-1].split('%26')
            for i in query: params[urllib_parse.unquote_plus(i).split('=')[0]] = urllib_parse.unquote_plus(i).split('=')[1]

            u = '%s?action=play&id=%s&content_type=shows' % (sys.argv[0], params['id'])
            meta = {'title': xbmc.getInfoLabel('ListItemNoWrap(%s).title' % i), 'tvshowtitle': xbmc.getInfoLabel('ListItemNoWrap(%s).tvshowtitle' % i), 'season': xbmc.getInfoLabel('ListItemNoWrap(%s).season' % i), 'episode': xbmc.getInfoLabel('ListItemNoWrap(%s).episode' % i), 'imdb_id': xbmc.getInfoLabel('ListItemNoWrap(%s).imdb_id' % i), 'premiered': xbmc.getInfoLabel('ListItemNoWrap(%s).premiered' % i), 'genre': '', 'plot': xbmc.getInfoLabel('ListItemNoWrap(%s).plot' % i), 'cover_url': xbmc.getInfoLabel('ListItemNoWrap(%s).cover_url' % i), 'duration': xbmc.getInfoLabel('ListItemNoWrap(%s).duration' % i) }
            poster, fanart = xbmc.getInfoLabel('ListItemNoWrap(%s).icon' % i), xbmc.getInfoLabel('ListItemNoWrap(%s).Property(Fanart_Image)' % i)

            item = xbmcgui.ListItem(label, iconImage="DefaultVideo.png", thumbnailImage=poster)
            item.setInfo( type="Video", infoLabels= meta )
            item.setProperty("IsPlayable", "true")
            item.setProperty("Video", "true")
            item.setProperty("Fanart_Image", fanart)
            playlist.add(u, item)
        xbmc.Player().play(playlist)

    def playlist_open(self):
        xbmc.executebuiltin('ActivateWindow(VideoPlaylist)')

    def settings_open(self):
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % (addonId))

    def addon_home(self):
        xbmc.executebuiltin('Container.Update(plugin://%s/,replace)' % (addonId))

    def view(self, content):
        try:
            skin = xbmc.getSkinDir()
            skinPath = xbmcvfs.translatePath('special://skin/')
            xml = os.path.join(skinPath,'addon.xml')
            file = xbmcvfs.File(xml)
            read = file.read().replace('\n','')
            file.close()
            try: src = re.compile('defaultresolution="(.+?)"').findall(read)[0]
            except: src = re.compile('<res.+?folder="(.+?)"').findall(read)[0]
            src = os.path.join(skinPath, src)
            src = os.path.join(src, 'MyVideoNav.xml')
            file = xbmcvfs.File(src)
            read = file.read().replace('\n','')
            file.close()
            views = re.compile('<views>(.+?)</views>').findall(read)[0]
            views = [int(x) for x in views.split(',')]
            for view in views:
                label = xbmc.getInfoLabel('Control.GetLabel(%s)' % (view))
                if not (label == '' or label is None): break
            file = xbmcvfs.File(viewData)
            read = file.read()
            file.close()
            write = [i.strip('\n').strip('\r') for i in read.splitlines(True) if i.strip('\r\n')]
            write = [i for i in write if not '"%s"|"%s"|"' % (skin, content) in i]
            write.append('"%s"|"%s"|"%s"' % (skin, content, str(view)))
            write = '\r\n'.join(write)
            file = xbmcvfs.File(viewData, 'w')
            file.write(str(write))
            file.close()
            viewName = xbmc.getInfoLabel('Container.Viewmode')
            self.index().infoDialog('%s%s%s' % (xbmcaddon.Addon().getLocalizedString(30301).encode("utf-8"), viewName, xbmcaddon.Addon().getLocalizedString(30302).encode("utf-8")))
        except:
            return

    def favourite_add(self, favData, id, name):
        try:
            file = xbmcvfs.File(favData)
            read = file.read()
            file.close()

            if '"%s"' % id in read:
                self.index().infoDialog(xbmcaddon.Addon().getLocalizedString(30307).encode("utf-8"), name)
                return

            write = [i.strip('\n').strip('\r') for i in read.splitlines(True) if i.strip('\r\n')]
            write.append('"%s"' % (id))
            write = '\r\n'.join(write)
            file = xbmcvfs.File(favData, 'w')
            file.write(str(write))
            file.close()

            self.index().container_refresh()
            self.index().infoDialog(xbmcaddon.Addon().getLocalizedString(30303).encode("utf-8"), name)
        except:
            return

    def favourite_delete(self, favData, id, name):
        try:
            file = xbmcvfs.File(favData)
            read = file.read()
            file.close()
            write = [i.strip('\n').strip('\r') for i in read.splitlines(True) if i.strip('\r\n')]
            write = [i for i in write if not '"%s"' % name in i and not '"%s"' % id in i]
            write = '\r\n'.join(write)
            file = xbmcvfs.File(favData, 'w')
            file.write(str(write))
            file.close()

            self.index().container_refresh()
            self.index().infoDialog(xbmcaddon.Addon().getLocalizedString(30304).encode("utf-8"), name)
        except:
            return

    def library_add(self, subData, id, name):
        try:
            file = xbmcvfs.File(subData)
            read = file.read()
            file.close()

            if '"%s"' % id in read:
                self.index().infoDialog(xbmcaddon.Addon().getLocalizedString(30316).encode("utf-8"), name)
                return

            self.library(id, silent=True)

            write = [i.strip('\n').strip('\r') for i in read.splitlines(True) if i.strip('\r\n')]
            write.append('"%s"' % (id))
            write = '\r\n'.join(write)
            file = xbmcvfs.File(subData, 'w')
            file.write(str(write))
            file.close()

            self.index().infoDialog(xbmcaddon.Addon().getLocalizedString(30312).encode("utf-8"), name)
            xbmc.executebuiltin('UpdateLibrary(video)')
        except:
            return

    def library_delete(self, subData, id, name):
        try:
            file = xbmcvfs.File(subData)
            read = file.read()
            file.close()
            write = [i.strip('\n').strip('\r') for i in read.splitlines(True) if i.strip('\r\n')]
            write = [i for i in write if not '"%s"' % name in i and not '"%s"' % id in i]
            write = '\r\n'.join(write)
            file = xbmcvfs.File(subData, 'w')
            file.write(str(write))
            file.close()

            self.index().container_refresh()
            self.index().infoDialog(xbmcaddon.Addon().getLocalizedString(30313).encode("utf-8"), name)
        except:
            return

    def library_update(self, subData, silent=False):
        try:
            file = xbmcvfs.File(subData)
            read = file.read()
            file.close()

            match = [i.strip('\r\n').strip('"').split('"|"') for i in read.splitlines(True)]
            for i in match:
                if xbmc.Monitor().abortRequested() == True: sys.exit()
                self.library(i[0], silent=True)

            if xbmcaddon.Addon().getSetting("updatelibrary") == 'true':
                xbmc.executebuiltin('UpdateLibrary(video)')
            if silent == False:
                self.index().infoDialog(xbmcaddon.Addon().getLocalizedString(30314).encode("utf-8"))
        except:
            return

    def library(self, id, check=False, silent=False):
        library = xbmcvfs.translatePath(xbmcaddon.Addon().getSetting("tv_library"))
        dataPath = xbmcvfs.translatePath('special://profile/addon_data/%s' % (xbmcaddon.Addon().getAddonInfo("id")))
        xbmcvfs.mkdir(dataPath)
        xbmcvfs.mkdir(library)

        try:
            # Id can also be the name in old format
            index_show = next(obj for obj in self.index().get_shows() if id == str(obj['id']) or id == obj['name'])
            show = self.index().get_show(index_show['id'])
            episodeList = self.index().get_episodes(show)

            for episode in episodeList:
                season = 'Season %d' % episode['season']
                enc_show = re.sub(r'[\\/:*?"<>|]', '', show['name'])
                folder = os.path.join(library, enc_show)
                xbmcvfs.mkdir(folder)
                enc_season = re.sub(r'[\\/:*?"<>|]', '', season)
                seasonDir = os.path.join(folder, enc_season)
                xbmcvfs.mkdir(seasonDir)

                content = '%s?action=play&id=%s&content_type=shows' % (sys.argv[0], episode['id'])
                enc_name = re.sub(r'[\\/:*?"<>|]', '', episode['name'])

                stream = os.path.join(seasonDir, enc_name + '.strm')
                file = xbmcvfs.File(stream, 'w')
                file.write(str(content))
                file.close()
            if silent == False:
                self.index().infoDialog(xbmcaddon.Addon().getLocalizedString(30311).encode("utf-8"), show['name'])
        except:
            return
