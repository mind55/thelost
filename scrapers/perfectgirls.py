import xbmc,xbmcplugin,os,urlparse,re
import client
import kodi
import dom_parser2
import log_utils
from resources.lib.modules import utils
from resources.lib.modules import helper
buildDirectory = utils.buildDir

filename     = os.path.basename(__file__).split('.')[0]
base_domain  = 'http://www.perfectgirls.net'
base_name    = base_domain.replace('www.',''); base_name = re.findall('(?:\/\/|\.)([^.]+)\.',base_name)[0].title()
type         = 'video'
menu_mode    = 216
content_mode = 217
player_mode  = 801

search_tag   = 0
search_base  = urlparse.urljoin(base_domain,'search/?q=%s')

@utils.url_dispatcher.register('%s' % menu_mode)
def menu():
    
    url = base_domain
    r = client.request(url)
    r = dom_parser2.parse_dom(r, 'li', {'class': 'header-submenu__item'})
    r = dom_parser2.parse_dom(r, 'a', req='href')
    r = [(i.attrs['href'], \
        i.content)for i in r if i]
    r = [(urlparse.urljoin(base_domain,i[0]),i[1]) for i in r if i]
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

    url = client.request(url, output='geturl')
    r = client.request(url)
    r = dom_parser2.parse_dom(r, 'div', {'class': 'list__item'})
    r = [(dom_parser2.parse_dom(i, 'a', req=['href','title']), \
        dom_parser2.parse_dom(i, 'time'), \
        dom_parser2.parse_dom(i, 'img', req='data-original')) for i in r if i]
    r = [(urlparse.urljoin(base_domain,i[0][0].attrs['href']), \
        i[0][0].attrs['title'], \
        i[1][0].content, \
        i[2][0].attrs['data-original']) for i in r if i]

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
        
        try:
            pattern = r'''((?:http|https)(?:\:\/\/)(?:www)(?:\/\/|\.)(perfectgirls.net)\/(category\/)([0-9+]\/)(.+?\/))([0-9]+)'''
            r = re.search(pattern,url)
            base = r.group(1)
            search_pattern = '''<a\s*class=['"]btn_wrapper__btn['"]\s*href=['"]([^'"]+)['"]>Next'''
            parse = base            
            helper.scraper().get_next_page(content_mode,url,search_pattern,filename,parse)
        except Exception as e: 
            log_utils.log('Error getting next page for %s :: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)