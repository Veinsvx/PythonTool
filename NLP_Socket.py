# coding=gb2312
import json
import socket
from bs4 import BeautifulSoup
from ..base import * #对接



def tag_verbs_or_adverbs(text):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 12345)
    client_socket.connect(server_address)
    client_socket.sendall(text.encode('utf-8'))
    data = client_socket.recv(10240).decode('utf-8')
    #print(f"收到服务器的回应: {data}")
    client_socket.close()
    data_dict = json.loads(data)
    result={
        'CX':u'''''',
        'FY':u'''''',
    }
    result["CX"] = data_dict["CX"]
    result["FY"]=data_dict["FY"]
    result.update()
    return result

@register([u'CiXingFenXi', u'CiXingFenXi-us'])#词库名称
class CiXingFenXi_English(WebService):#接口名称
    def __init__(self):
        super(CiXingFenXi_English, self).__init__()#接口名称保持一致
    def _get_from_api(self):
        result=tag_verbs_or_adverbs(self.word)#获取string
        return self.cache_this(result)

    @export('词性')#功能名称
    def CiXing_(self):#功能函数
        return self._get_field('CX')

    @export('翻译')#功能名称
    def FanYi_(self):#功能函数
        return self._get_field('FY')
    
