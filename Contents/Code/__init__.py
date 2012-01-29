import re

####################################################################################################

PLUGIN_PREFIX = '/video/automatedhome'
NAME          = L('Title')
ART           = 'art-default.jpg'
ICON          = 'icon-default.png'

FEED          = 'http://gdata.youtube.com/feeds/base/users/automatedhomeuk/uploads'
NAMESPACES    = {'a': 'http://www.w3.org/2005/Atom', 'os': 'http://a9.com/-/spec/opensearchrss/1.0/'}

####################################################################################################

def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, NAME, ICON, ART)
  Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')

  ObjectContainer.title1 = NAME
  ObjectContainer.view_group = 'InfoList'
  ObjectContainer.art = R(ART)

  DirectoryObject.thumb = R(ICON)
  DirectoryObject.art = R(ART)
  VideoClipObject.thumb = R(ICON)
  VideoClipObject.art = R(ART)

  HTTP.CacheTime = CACHE_1HOUR

####################################################################################################

def MainMenu():
  oc = ParseYtFeed(feed = FEED)
  return oc

####################################################################################################

def ParseYtFeed(feed=None):
  oc = ObjectContainer(title2=L('Episodes'))

  xml = XML.ElementFromURL(feed, errors='ignore')

  try:
    nextUrl = xml.xpath('//a:link[@rel="next"]', namespaces=NAMESPACES)[0].get('href')
  except:
    nextUrl = None

  for e in xml.xpath('//a:entry', namespaces=NAMESPACES):
    try:
      date = re.sub('T.*', '', e.xpath('.//a:published/text()', namespaces=NAMESPACES)[0])
      date = Datetime.ParseDate(date)
    except:
      date = None

    url = e.xpath('.//a:link[@rel="alternate"]', namespaces=NAMESPACES)[0].get('href')
    title = e.xpath('.//a:title/text()', namespaces=NAMESPACES)[0]

    summary_html = e.xpath('.//a:content/text()', namespaces=NAMESPACES)[0]
    summary_xml = HTML.ElementFromString(summary_html)

    try:
      thumb = summary_xml.xpath('//img')[0].get('src')
      thumb = re.sub(r'/default.jpg','/hqdefault.jpg',thumb)
    except:
      thumb = R(ICON)

    try:
      summary = summary_xml.xpath('//span')[0].text
    except:
      summary = ''

    try:
      dur_parts = summary_xml.xpath('//span')[-2].text.split(':')
      dur_parts.reverse()
      i = 0
      for p in dur_parts:
        duration = duration + int(p)*(60**i)
        i = i + 1
        duration = duration * 1000
    except:
      duration = None

    oc.add(VideoClipObject(
      url = url,
      title = title,
      summary = summary,
      thumb = thumb,
      duration = duration))

  if nextUrl:
    oc.add(DirectoryObject(key = Callback(ParseYtFeed, feed = nextUrl), title = L('Next Page')))

  return oc
