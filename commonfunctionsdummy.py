'''
   Parsedom for XBMC plugins
   Copyright (C) 2010-2011 Tobias Ussing And Henrik Mosgaard Jensen

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

import sys

import six
from six.moves import urllib_parse, urllib_request

import re
import io
import inspect
import time
import json

version = "2.5.1"
plugin = "CommonFunctions-" + version
print(plugin)

USERAGENT = "Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1"

if hasattr(sys.modules["__main__"], "xbmc"):
    xbmc = sys.modules["__main__"].xbmc
else:
    import xbmc

if hasattr(sys.modules["__main__"], "xbmcgui"):
    xbmcgui = sys.modules["__main__"].xbmcgui
else:
    import xbmcgui

if hasattr(sys.modules["__main__"], "dbg"):
    dbg = sys.modules["__main__"].dbg
else:
    dbg = False

if hasattr(sys.modules["__main__"], "dbglevel"):
    dbglevel = sys.modules["__main__"].dbglevel
else:
    dbglevel = 3

if hasattr(sys.modules["__main__"], "opener"):
    urllib_request.install_opener(sys.modules["__main__"].opener)


# This function raises a keyboard for user input
def getUserInput(title="Input", default="", hidden=False):
    log("", 5)
    result = None

    # Fix for when this functions is called with default=None
    if not default:
        default = ""

    keyboard = xbmc.Keyboard(default, title)
    keyboard.setHiddenInput(hidden)
    keyboard.doModal()

    if keyboard.isConfirmed():
        result = keyboard.getText()

    log(repr(result), 5)
    return result


# This function raises a keyboard numpad for user input
def getUserInputNumbers(title="Input", default=""):
    log("", 5)
    result = None

    # Fix for when this functions is called with default=None
    if not default:
        default = ""

    keyboard = xbmcgui.Dialog()
    result = keyboard.numeric(0, title, default)

    log(repr(result), 5)
    return str(result)


def getXBMCVersion():
    log("", 3)
    version = xbmc.getInfoLabel( "System.BuildVersion" )
    log(version, 3)
    for key in ["-", " "]:
        if version.find(key) -1:
            version = version[:version.find(key)]
    version = float(version)
    log(repr(version))
    return version

# Converts the request url passed on by xbmc to the plugin into a dict of key-value pairs
def getParameters(parameterString):
    log("", 5)
    commands = {}
    if getXBMCVersion() >= 12.0:
        parameterString = urllib_parse.unquote_plus(parameterString)
    splitCommands = parameterString[parameterString.find('?') + 1:].split('&')

    for command in splitCommands:
        if (len(command) > 0):
            splitCommand = command.split('=')
            key = splitCommand[0]
            try:
                value = splitCommand[1].encode("utf-8")
            except:
                log("Error utf-8 encoding argument value: " + repr(splitCommand[1]))
                value = splitCommand[1]

            commands[key] = value

    log(repr(commands), 5)
    return commands


# This function implements a horrible hack related to python 2.4's terrible unicode handling.
def makeAscii(data):
    log(repr(data), 5)
    #if sys.hexversion >= 0x02050000:
    #        return data

    try:
        return data.encode('ascii', "ignore")
    except:
        log("Hit except on : " + repr(data))
        s = ""
        for i in data:
            try:
                i.encode("ascii", "ignore")
            except:
                log("Can't convert character", 4)
                continue
            else:
                s += i

        log(repr(s), 5)
        return s


# This function handles stupid utf handling in python.
def makeUTF8(data):
    log(repr(data), 5)
    return data
    try:
        return data.decode('utf8', 'xmlcharrefreplace') # was 'ignore'
    except:
        log("Hit except on : " + repr(data))
        s = ""
        for i in data:
            try:
                i.decode("utf8", "xmlcharrefreplace")
            except:
                log("Can't convert character", 4)
                continue
            else:
                s += i
        log(repr(s), 5)
        return s


def openFile(filepath, options="r"):
    log(repr(filepath) + " - " + repr(options))
    if options.find("b") == -1:  # Toggle binary mode on failure
        alternate = options + "b"
    else:
        alternate = options.replace("b", "")

    try:
        log("Trying normal: %s" % options)
        return io.open(filepath, options)
    except:
        log("Fallback to binary: %s" % alternate)
        return io.open(filepath, alternate)


def log(description, level=0):
    if dbg and dbglevel > level:
        try:
            xbmc.log(("[%s] %s : '%s'" % (plugin, inspect.stack()[1][3], description)).decode("utf-8"), xbmc.LOGNOTICE)
        except:
            xbmc.log("FALLBACK [%s] %s : '%s'" % (plugin, inspect.stack()[1][3], repr(description)), xbmc.LOGNOTICE)
