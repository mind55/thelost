import xbmc,xbmcplugin,os,urlparse,re
import client
import kodi
import dom_parser2
import log_utils
from resources.lib.modules import utils
from resources.lib.modules import helper
buildDirectory = utils.buildDir

filename     = os.path.basename(__file__).split('.')[0]
base_domain  = 'http://chaturbate.com'
base_name    = base_domain.replace('www.',''); base_name = re.findall('(?:\/\/|\.)([^.]+)\.',base_name)[0].title()
type         = 'video'
menu_mode    = 300
content_mode = 301
player_mode  = 801

search_tag   = 0

@utils.url_dispatcher.register('%s' % menu_mode)
def menu():
    
    url = base_domain
    r = client.request(url)
    r = dom_parser2.parse_dom(r, 'dd')
    r = dom_parser2.parse_dom(r, 'a', req='href')
    r = [i for i in r if 'private-cams' not in i.attrs['href']]
    r = [(urlparse.urljoin(base_domain,i.attrs['href']),i.content) for i in r if i]
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
    r = dom_parser2.parse_dom(r, 'li')
    r = [(dom_parser2.parse_dom(i, 'div', {'class': 'title'}), \
        dom_parser2.parse_dom(i, 'img', req='src'), \
        dom_parser2.parse_dom(i, 'div', {'class': re.compile('thumbnail_label.+?')}), \
        dom_parser2.parse_dom(i, 'li', {'title': re.compile('.+?')}), \
        dom_parser2.parse_dom(i, 'li', {'class': 'location'}), \
        dom_parser2.parse_dom(i, 'li', {'class': 'cams'}) \
        ) for i in r if '<div class="title">' in i.content]

    r = [(dom_parser2.parse_dom(i[0], 'a'), \
        dom_parser2.parse_dom(i[0], 'span'), \
        i[2][0].content, \
        i[1][0].attrs['src'], \
        i[3][0].content, \
        i[4][0].content, \
        i[5][0].content, \
        ) for i in r]
    r = [(urlparse.urljoin(base_domain,i[0][0].attrs['href']), i[0][0].content, i[1][0].content,i[2],i[3],i[6],i[5],i[4]) for i in r]
    dirlst = []
    
    for i in r:
        try:
            name = '%s - [ %s ]' % (kodi.sortX(i[1].encode('utf-8')).title(),kodi.sortX(i[3].encode('utf-8')))
            description = 'Name: %s \nAge: %s \nLocation: %s \nStats: %s \n\nDescription: %s' % \
            (kodi.sortX(i[1].encode('utf-8')),i[2],kodi.sortX(i[6].encode('utf-8')),kodi.sortX(i[5].encode('utf-8')),kodi.sortX(i[7].encode('utf-8')))
            content_url = i[0] + '|SPLIT|%snotify|%s' % (base_name, kodi.sortX(i[7].encode('utf-8')))
            fanarts = xbmc.translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': name, 'url': content_url, 'mode': player_mode, 'icon': i[4], 'fanart': fanarts, 'description': description, 'folder': False})
        except Exception as e:
            log_utils.log('Error adding menu item %s in %s:: Error: %s' % (i[1].title(),base_name.title(),str(e)), log_utils.LOGERROR)
    
    if dirlst: buildDirectory(dirlst, stopend=True, isVideo = False, isDownloadable = False)
    else:
        kodi.notify(msg='No Content Found')
        quit()
        
    search_pattern = '''<li><a\s*href=['"]([^'"]+)['"]\s*class=['"]next endless_page_link['"]>next<\/a><\/li>'''
    parse = base_domain
    helper.scraper().get_next_page(content_mode,url,search_pattern,filename,parse)