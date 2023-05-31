# coding=gb2312
import json
import socket
from bs4 import BeautifulSoup
from ..base import * #�Խ�



def tag_verbs_or_adverbs(text):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 12345)
    client_socket.connect(server_address)
    client_socket.sendall(text.encode('utf-8'))
    data = client_socket.recv(10240).decode('utf-8')
    #print(f"�յ��������Ļ�Ӧ: {data}")
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

@register([u'CiXingFenXi', u'CiXingFenXi-us'])#�ʿ�����
class CiXingFenXi_English(WebService):#�ӿ�����
    def __init__(self):
        super(CiXingFenXi_English, self).__init__()#�ӿ����Ʊ���һ��
    def _get_from_api(self):
        result=tag_verbs_or_adverbs(self.word)#��ȡstring
        return self.cache_this(result)

    @export('����')#��������
    def CiXing_(self):#���ܺ���
        return self._get_field('CX')

    @export('����')#��������
    def FanYi_(self):#���ܺ���
        return self._get_field('FY')
    
