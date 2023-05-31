# coding=gb2312
import json
import socket
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from ..base import * #对接


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
        options.add_argument('--headless')  # 静默运行，不弹出浏览器窗口
        options.add_argument('--disable-extensions')  # 禁用扩展
        url=u'http://192.3.165.101:5860/?word={word}'.format(word=words)
        #
        #如果您使用的是Microsoft Edge浏览器，您可以在以下地址下载Microsoft Edge浏览器驱动：
        #https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
        #下载完后，请把驱动文件解压到任意位置，并在代码中使用以下代码指定驱动的路径：     
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
    #！获取单词音标
    ipa_span = soup.select_one('.ipa')
    #ok1
    result['yinbiao'] =str(ipa_span)

    #！获取单词排第一位词性
    pos_span = soup.select_one('.coca.pc .pos')
    result['mean']=str(pos_span)

    #！获取单词排第一位的意思
    # 查询第一个 span 标签的内容

    first_span = soup.find('div', class_='coca2').find('span')
    # 去除内容中的 font 标签
    #first_span = soup.find('div', class_='coca2').find('span').text
    #first_span = re.sub(r'\d+', '', first_span)
    #ok2
    result['mean']= result['mean']+'. '+str(first_span)
    
    
    #！获取单词变形
    # 找到class为hwrap的div标签
    hwrap_div = soup.find('div', {'class': 'hwrap'})


    #！获取单词是哪级词汇
    frequency_div = soup.find('div', {'class': 'word-frequency'})


    #！获取单词是词性词频
    coca_pc_div = soup.find('div', {'class': 'coca pc'})

    #！获取完整的释义频率
    coca2_div = soup.find("div", class_="coca2")

    #！获取完整的释义
    gdc_div = soup.find("div", class_="gdc")    

    #ok5
    result['tld']=str(hwrap_div)+str(frequency_div)+str(coca_pc_div)+str(coca2_div)+str(gdc_div)


    #获取单词考研词频result['cipin']
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
        temp=temp+' | 考研'+kaoyantxt.text+': '+kaoyancipin.text
    #ok3
    result['cipin']=temp
    '''

    #获取童哥说单词(简洁版)result['cigen']
    last_mdict = soup.find_all("div", class_="etmy")
    #links = last_mdict.find_all("link")
    #for link in links:
    #    link.decompose()
    #ok4
    result['cigen']=str(last_mdict[0])

    '''

    ##高伟东版的词根词缀
    # # 找到所有的script标签
    #gwdcg_tags = soup.find('gwdcg')
    ##定义正则表达式
    #if gwdcg_tags:
    #    data = json.loads(gwdcg_tags.text)
    #    #ok4
    #    result['cigen']=str(render_node_list(data,True))


    #获取AHD标签数据
    #童哥说单词和ahd词典都是mdict类，ahd是最后面的，所以因该是-1
    ahd_mdict = soup.find_all("div", class_="mdict")[-1]
    #获取图片解释
    capc = ahd_mdict.find("cap_c")
    
    #获取图片-第一种是藏在特殊标签下
    img_tags = None
    a5p_wr_list = soup.find_all('a5p_wr')  # 查找所有的<a5p_wr>标签
    for a5p_wr in a5p_wr_list:
        img_tags = a5p_wr.find_all('img', class_=False)  # 查找没有class名的<img>标签
        if img_tags:
            src = img_tags[0]['src']
            img_tags[0]['src']=u'http://198.74.107.8:5860/'+str(src)
            img_tags[0]['class']="lxjytp"

    #第二种是有固定类名的
    if img_tags:
        print("特殊标签下获得数据了")
    else:
        img_tags = soup.find_all('img', class_="yd_img")  # 查找没有class名的<img>标签
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


@register([u'YueDuZhuanYongPlus', u'YDZYPLUS-us'])#词库名称
class ydzyPlus_English(WebService):#接口名称
    def __init__(self):
        super(ydzyPlus_English, self).__init__()#接口名称保持一致
    def _get_from_api(self):
        result=ydzyPlusSearch_English(self.word)#获取dict
        return self.cache_this(result)

    @export('意思')#功能名称
    def mean_(self):#功能函数
        return self._get_field('mean')
    
    @export('词频')
    def cipinjs_(self):
        return self._get_field('cipin')

    @export('词根')
    def cigen_(self):
        return self._get_field('cigen')

    @export('Tld')
    def theld_(self):
        return self._get_field('tld')

    @export('yb')
    def ybjz_(self):
        return self._get_field('yinbiao')

    @export('联想')
    def yblx_(self):
        return self._get_field('lx')