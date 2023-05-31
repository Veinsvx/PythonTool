import requests
from bs4 import BeautifulSoup
from ..base import * #对接


def TLDSearch_English(words):
    result={
        'mean':u'',
        'cipin':u'',
    }
    try:
        url=u'http://192.168.10.103:5860/?word={word}'.format(word=words)
        get_requests=requests.get(url)
        soup=BeautifulSoup(get_requests.text,'html.parser')
    except:
        return result
    
    resulttemp=''
    #获取最常用的单词词性
    container = soup.find("div", class_="coca iweb")
    if container:
        cixing_span = container.find("span", class_="pos")
        if cixing_span:
            resulttemp=cixing_span.text
        else:
            resulttemp='?'
    else:
        resulttemp='?'

    #获取最常用单词释义
    mean_div = soup.find("div", class_="coca2")
    if mean_div:
        meantemp =  mean_div.text
        resulttemp=resulttemp+'.'+meantemp[:meantemp.find('(')]        
    else:
        resulttemp=resulttemp+'.'+'?'

    result['mean']=resulttemp

    #获取单词coca词频
    row=[]
    coca = soup.find_all(name='span',attrs={'class':'badge badge-pill badge-info'})
    for b in coca:
        row.append(b.text)
    temp=row[-1]
    result['cipin']=temp

    result.update()
    return result


@register([u'TLD', u'TLD-us'])#词库名称
class TLD_English(WebService):#接口名称
    def __init__(self):
        super(TLD_English, self).__init__()#接口名称保持一致
    def _get_from_api(self):
        result=TLDSearch_English(self.word)#获取dict
        return self.cache_this(result)

    @export('意思')#功能名称
    def mean_(self):#功能函数
        return self._get_field('mean')
    
    @export('词频')
    def cipinjs_(self):
        return self._get_field('cipin')