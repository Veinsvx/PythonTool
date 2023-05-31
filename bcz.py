#-*- coding:utf-8 -*-
import os
import re
import random
from ..base import *

DICT_PATH = u"C:\\cd\\bcz.mdx" 

@register([u'A_baicizhan', u'A_Baicizhan'])
class bcz(MdxService):

    def __init__(self):
        dict_path = DICT_PATH
        if not dict_path:
            from ...service import service_manager, service_pool
            for clazz in service_manager.mdx_services:
                service = service_pool.get(clazz.__unique__)
                title = service.builder._title if service and service.support else u''
                service_pool.put(service)
                if title.startswith(u'bcz'):
                    dict_path = service.dict_path
                    break
        super(bcz, self).__init__(dict_path)

    @property
    def title(self):
        return getattr(self, '__register_label__', self.unique)

    def get_html_all(self):
        html = self.get_html()
        if not html:
            self.word = self.word.lower()
            html = self.get_html()
            if not html:
                self.word = self.word.capitalize()
                html = self.get_html()
                if not html:
                    self.word = self.word.upper()
                    html = self.get_html()
        return html

    @export('音标')
    def eco_freq(self):
        html = self.get_html_all()
        if html:
            freq = re.search(r'<span class="pron">(.*?)</span>', html)
            if freq:
                return freq[1].strip()
        return ''

    @export('中文释义')
    def chinese_def(self):
        m = re.findall(r'<div class="\s*.*<\/div>', self.get_html_all())
        if m:
            soup = parse_html(m[0])

            el_list = soup.findAll('div', {'class':'mean_cn'})
            def_distribution = ''
            if el_list:
                def_distribution = str(el_list[0])
                return def_distribution
        return ''

    @export('例句')
    def exg(self):
        m = re.findall(r'<div class="\s*.*<\/div>', self.get_html_all())
        if m:
            soup = parse_html(m[0])

            exg_list = soup.findAll('div', {'class':'exg'})
            eg_exg = ''
            if exg_list:
                eg_exg = str(exg_list[0])
                return eg_exg
        return ''

    def _fld_image(self, img):
        val = '/' + img
        file_extension = os.path.splitext(img)[1][1:].strip().lower()
        name = get_hex_name('mdx-'+self.unique.lower(), val, file_extension)
        name = self.save_file(val, name)
        if name:
            return self.get_anki_label(name, 'img')
        return ''

    @export('图片')
    def fld_image(self):
        html = self.get_html()
        m = re.search(r'<div class="pic"><img class="illu" src="(.*?)".*?><div class="exg">', html)
        if m:
            return self._fld_image(m.groups()[0])
        return ''

    def _fld_df(self, img):
        val = '/' + img
        # file extension isn't always jpg
        file_extension = os.path.splitext(img)[1][1:].strip().lower()
        name = get_hex_name('mdx-'+self.unique.lower(), val, file_extension)
        name = self.save_file(val, name)
        if name:
            return self.get_anki_label(name, 'img')
        return ''


    @export('象形')
    def fld_df(self):
        html = self.get_html()
        m = re.search(r'<img class="df" src="(.*?)".*?/></div>', html)
        if m:
            return self._fld_image(m.groups()[0])
        return ''