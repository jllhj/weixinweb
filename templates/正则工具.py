import re
"""
data = 'window.QRLogin.code = 200; window.QRLogin.uuid = "gbBNimb1cw==";'

ret = re.findall('uuid = "(.*)";',data)[0]
print(ret)
"""

def xml_parse(text):
    result = {}
    soup = BeautifulSoup(text,'html.parser')
    tag_list = soup.find(name='error').find_all()
    for tag in tag_list:
        result[tag.name] = tag.text
    return result

# 解析字符串
from bs4 import BeautifulSoup
v = "<error><ret>0</ret><message></message><skey>@crypt_f4c59f9_514a1b6c9f6a1f7c8cda577a2413c105</skey><wxsid>Ny8Uqbrv42z81MMY</wxsid><wxuin>736280903</wxuin><pass_ticket>slxsXaH2vXOGhmX2kyheYKdDc28P4k3P7jywT1DsBUVhvUcMZuLxDwi52OlWmH2I</pass_ticket><isgrayscale>1</isgrayscale></error>"
result = xml_parse(v)
print(result)