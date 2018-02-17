import xbmc,xbmcplugin,os,urlparse,re
import client
import kodi
import dom_parser2
import log_utils
from resources.lib.modules import utils
from resources.lib.modules import helper
buildDirectory = utils.buildDir

filename     = os.path.basename(__file__).split('.')[0]
base_domain  = 'http://www.motherless.com'
base_name    = base_domain.replace('www.',''); base_name = re.findall('(?:\/\/|\.)([^.]+)\.',base_name)[0].title()
type         = 'video'
menu_mode    = 210
content_mode = 211
player_mode  = 801

search_tag   = 1
search_base  = urlparse.urljoin(base_domain,'term/%s')

@utils.url_dispatcher.register('%s' % menu_mode)
def menu():
    
    url = urlparse.urljoin(base_domain,'videos')
    r = client.request(url)
    r = dom_parser2.parse_dom(r, 'h1')
    r = [(dom_parser2.parse_dom(i, 'a', req='href')) for i in r if i]
    r = [(urlparse.urljoin(base_domain,i[0].attrs['href']),i[0].content) for i in r if i]
    dirlst = []
    
    for i in r:
        try:
            name = kodi.sortX(i[1].encode('utf-8')).title()
            icon = xbmc.translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/icon.png' % filename))
            fanarts = xbmc.translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': name, 'url': i[0], 'mode': content_mode, 'icon': icon, 'fanart': fanarts, 'folder': True})
        except Exception as e:
            log_utils.log('Error adding menu item %s in %s:: Error: %s' % (i[1].title(),base_name.title(),str(e)), log_utils.LOGERROR)
    
    if dirlst: buildDirectory(dirlst)    
    else:
        kodi.notify(msg='No Menu Items Found')
        quit()
        
@utils.url_dispatcher.register('%s' % content_mode,['url'],['searched'])
def content(url,searched=False):

    r = client.request(url)
    r = dom_parser2.parse_dom(r, 'div', {'class': re.compile('thumb\svideo\smedium')})
    r = [(dom_parser2.parse_dom(i, 'a', req='href'), \
         dom_parser2.parse_dom(i, 'h2', {'class': re.compile('caption\stitle')}), \
         dom_parser2.parse_dom(i, 'div', {'class': re.compile('caption\sleft')}), \
         dom_parser2.parse_dom(i, 'img', req='src')) for i in r if i]
    r = [(i[0][0].attrs['href'],i[1][0].content,i[2][0].content,i[3][0].attrs['src']) for i in r if i]
    dirlst = []
    
    for i in r:
        try:
            name = '%s - [ %s ]' % (kodi.sortX(i[1].encode('utf-8')).title(),kodi.sortX(i[2].encode('utf-8')))
            if searched: description = 'Result provided by %s' % base_name.title()
            else: description = name
            content_url = i[0] + '|SPLIT|%s' % base_name
            fanarts = xbmc.translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': name, 'url': content_url, 'mode': player_mode, 'icon': i[3], 'fanart': fanarts, 'description': description, 'folder': False})
        except Exception as e:
            log_utils.log('Error adding menu item %s in %s:: Error: %s' % (i[1].title(),base_name.title(),str(e)), log_utils.LOGERROR)
    
    if dirlst: buildDirectory(dirlst, stopend=True, isVideo = True, isDownloadable = True)
    else:
        if (not searched):
            kodi.notify(msg='No Content Found')
            quit()
        
    if searched: return str(len(r))
    
    if not searched:
        search_pattern = '''a\s*href=['"]([^'"]+)['"]\s*class=['"]pop['"]\s*rel=['"]\d+['"]>NEXT'''
        parse = base_domain
        
        helper.scraper().get_next_page(content_mode,url,search_pattern,filename,parse)