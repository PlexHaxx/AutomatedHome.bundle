import re

####################################################################################################

PLUGIN_PREFIX = '/video/automatedhome'
NAME          = L('Title')
ART           = 'art-default.jpg'
ICON          = 'icon-default.png'

FEED          = 'http://gdata.youtube.com/feeds/base/users/automatedhomeuk/uploads'
NAMESPACES    = {'a': 'http://www.w3.org/2005/Atom', 'os': 'http://a9.com/-/spec/opensearchrss/1.0/'}

YOUTUBE_VIDEO_FORMATS = ['Standard', 'Medium', 'High', '720p', '1080p']
YOUTUBE_FMT           = [34, 18, 35, 22, 37]
USER_AGENT            = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12'

####################################################################################################

def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, NAME, ICON, ART)
  Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')

  MediaContainer.art = R(ART)
  MediaContainer.title1 = NAME
  MediaContainer.viewGroup = 'InfoList'
  MediaContainer.userAgent = USER_AGENT

  DirectoryItem.thumb = R(ICON)
  VideoItem.thumb = R(ICON)

  HTTP.CacheTime = CACHE_1HOUR
  HTTP.Headers['User-Agent'] = USER_AGENT

####################################################################################################

def MainMenu():
  dir = ParseYtFeed(feed=FEED)
  return dir

####################################################################################################

def ParseYtFeed(sender=None, feed=None):
  cookies = HTTP.GetCookiesForURL('http://www.youtube.com')
  dir = MediaContainer(title2=L('Episodes'), httpCookies=cookies)

  xml = XML.ElementFromURL(feed, errors='ignore')

  try:
    nextUrl = xml.xpath('//a:link[@rel="next"]', namespaces=NAMESPACES)[0].get('href')
  except:
    nextUrl = None

  try:
    prevUrl = xml.xpath('//a:link[@rel="previous"]', namespaces=NAMESPACES)[0].get('href')
  except:
    prevUrl = None

  if prevUrl:
    dir.Append(Function(DirectoryItem(ParseYtFeed, title=L('Previous Page')), feed=prevUrl))

  for e in xml.xpath('//a:entry', namespaces=NAMESPACES):
    try:
      date = re.sub('T.*', '', e.xpath('.//a:published/text()', namespaces=NAMESPACES)[0])
    except:
      date = ''

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

    dir.Append(Function(VideoItem(VidRedirect, title=title, subtitle=date, summary=summary, duration=duration, thumb=thumb), url=url))

  if nextUrl:
    dir.Append(Function(DirectoryItem(ParseYtFeed, title=L('Next Page')), feed=nextUrl))

  return dir

####################################################################################################

def VidRedirect(sender, url):
  yt_page = HTTP.Request(url, cacheTime=1).content

  fmt_url_map = re.findall('"fmt_url_map".+?"([^"]+)', yt_page)[0]
  fmt_url_map = fmt_url_map.replace('\/', '/').split(',')

  fmts = []
  fmts_info = {}

  for f in fmt_url_map:
    (fmt, url) = f.split('|')
    fmts.append(fmt)
    fmts_info[str(fmt)] = url

  index = YOUTUBE_VIDEO_FORMATS.index(Prefs['youtube_fmt'])
  if YOUTUBE_FMT[index] in fmts:
    fmt = YOUTUBE_FMT[index]
  else:
    for i in reversed( range(0, index+1) ):
      if str(YOUTUBE_FMT[i]) in fmts:
        fmt = YOUTUBE_FMT[i]
        break
      else:
        fmt = 5

  url = fmts_info[str(fmt)].decode('unicode_escape')
  return Redirect(url)
