# coding=gb2312
import json
import socket
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from ..base import * #�Խ�


def ydzyPlusSearch_English(words):
    result={
        'yinbiao':u'',
        'mean':u'',
        'cipin':u'',
        'cigen':u'',
        'tld':u'',
        'lx':u'',
    }
    try:
        service = EdgeService(r'C:\edgedriver_win64\msedgedriver.exe')
        options = webdriver.EdgeOptions()
        options.add_argument('--headless')  # ��Ĭ���У����������������
        options.add_argument('--disable-extensions')  # ������չ
        url=u'http://192.3.165.101:5860/?word={word}'.format(word=words)
        #
        #�����ʹ�õ���Microsoft Edge������������������µ�ַ����Microsoft Edge�����������
        #https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
        #���������������ļ���ѹ������λ�ã����ڴ�����ʹ�����´���ָ��������·����     
        driver = webdriver.Edge(service=service, options=options)
        driver.get(url)
        html = driver.page_source
        print(html)
        driver.quit()
        soup = BeautifulSoup(html, 'html.parser')
    except:
        print("xxxx")
        return result

    '''
    #����ȡ��������
    ipa_span = soup.select_one('.ipa')
    #ok1
    result['yinbiao'] =str(ipa_span)

    #����ȡ�����ŵ�һλ����
    pos_span = soup.select_one('.coca.pc .pos')
    result['mean']=str(pos_span)

    #����ȡ�����ŵ�һλ����˼
    # ��ѯ��һ�� span ��ǩ������

    first_span = soup.find('div', class_='coca2').find('span')
    # ȥ�������е� font ��ǩ
    #first_span = soup.find('div', class_='coca2').find('span').text
    #first_span = re.sub(r'\d+', '', first_span)
    #ok2
    result['mean']= result['mean']+'. '+str(first_span)
    
    
    #����ȡ���ʱ���
    # �ҵ�classΪhwrap��div��ǩ
    hwrap_div = soup.find('div', {'class': 'hwrap'})


    #����ȡ�������ļ��ʻ�
    frequency_div = soup.find('div', {'class': 'word-frequency'})


    #����ȡ�����Ǵ��Դ�Ƶ
    coca_pc_div = soup.find('div', {'class': 'coca pc'})

    #����ȡ����������Ƶ��
    coca2_div = soup.find("div", class_="coca2")

    #����ȡ����������
    gdc_div = soup.find("div", class_="gdc")    

    #ok5
    result['tld']=str(hwrap_div)+str(frequency_div)+str(coca_pc_div)+str(coca2_div)+str(gdc_div)


    #��ȡ���ʿ��д�Ƶresult['cipin']
    row=[]
    temp=''
    coca = soup.find_all(name='span',attrs={'class':'badge badge-pill badge-info'})
    if coca:
        for b in coca:
            row.append(b.text)
            temp=row[-1]

    kaoyantxt= soup.find(name='span',attrs={'class':'freq1'})
    kaoyancipin= soup.find(name='span',attrs={'class':'freq2'})
    if kaoyantxt and kaoyancipin:
        temp=temp+' | ����'+kaoyantxt.text+': '+kaoyancipin.text
    #ok3
    result['cipin']=temp
    '''

    #��ȡͯ��˵����(����)result['cigen']
    last_mdict = soup.find_all("div", class_="etmy")
    #links = last_mdict.find_all("link")
    #for link in links:
    #    link.decompose()
    #ok4
    result['cigen']=str(last_mdict[0])

    '''

    ##��ΰ����Ĵʸ���׺
    # # �ҵ����е�script��ǩ
    #gwdcg_tags = soup.find('gwdcg')
    ##����������ʽ
    #if gwdcg_tags:
    #    data = json.loads(gwdcg_tags.text)
    #    #ok4
    #    result['cigen']=str(render_node_list(data,True))


    #��ȡAHD��ǩ����
    #ͯ��˵���ʺ�ahd�ʵ䶼��mdict�࣬ahd�������ģ����������-1
    ahd_mdict = soup.find_all("div", class_="mdict")[-1]
    #��ȡͼƬ����
    capc = ahd_mdict.find("cap_c")
    
    #��ȡͼƬ-��һ���ǲ��������ǩ��
    img_tags = None
    a5p_wr_list = soup.find_all('a5p_wr')  # �������е�<a5p_wr>��ǩ
    for a5p_wr in a5p_wr_list:
        img_tags = a5p_wr.find_all('img', class_=False)  # ����û��class����<img>��ǩ
        if img_tags:
            src = img_tags[0]['src']
            img_tags[0]['src']=u'http://198.74.107.8:5860/'+str(src)
            img_tags[0]['class']="lxjytp"

    #�ڶ������й̶�������
    if img_tags:
        print("�����ǩ�»��������")
    else:
        img_tags = soup.find_all('img', class_="yd_img")  # ����û��class����<img>��ǩ
        if img_tags:
            src = img_tags[0]['src']
            img_tags[0]['src']=u'http://198.74.107.8:5860/'+str(src)
            img_tags[0]['class']="lxjytp"
    #ok5
    if  capc and img_tags[0]:
        result['lx']=str(img_tags[0])+"<p class=\"lxjywb\">"+capc.text+"</p>"
    else:
        result['lx']=u""

    '''

    result.update()
    return result


def render_node_list(nodes,isonce,parentid=None, level=0):
    html = "<ul>\n"
    for node in nodes['data']:
        if (node.get('parentid') == parentid and node.get('direction') == 'left') or (node.get('isroot', False) and isonce):
            html += '<li describe="{0}">{1}</li>\n'.format(node.get('describe', ''), node['topic'])
            html += render_node_list(nodes,False, parentid=node['id'], level=level+1)
    html += "</ul>\n"
    return html


@register([u'YueDuZhuanYongPlus', u'YDZYPLUS-us'])#�ʿ�����
class ydzyPlus_English(WebService):#�ӿ�����
    def __init__(self):
        super(ydzyPlus_English, self).__init__()#�ӿ����Ʊ���һ��
    def _get_from_api(self):
        result=ydzyPlusSearch_English(self.word)#��ȡdict
        return self.cache_this(result)

    @export('��˼')#��������
    def mean_(self):#���ܺ���
        return self._get_field('mean')
    
    @export('��Ƶ')
    def cipinjs_(self):
        return self._get_field('cipin')

    @export('�ʸ�')
    def cigen_(self):
        return self._get_field('cigen')

    @export('Tld')
    def theld_(self):
        return self._get_field('tld')

    @export('yb')
    def ybjz_(self):
        return self._get_field('yinbiao')

    @export('����')
    def yblx_(self):
        return self._get_field('lx')