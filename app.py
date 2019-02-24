from flask import Flask,render_template,session,jsonify,request
import time
import requests
import re
import json

app = Flask(__name__)
app.secret_key = 'asdsadsa'

# 解析字符串
from bs4 import BeautifulSoup

def xml_parse(text):
    result = {}
    soup = BeautifulSoup(text,'html.parser')
    tag_list = soup.find(name='error').find_all()
    for tag in tag_list:
        result[tag.name] = tag.text
    return result


@app.route('/login')
def login():
    # 1550217571.949244 要转换成下面格式
    # 1550217416454微信上的时间戳
    ctime = int(time.time()*1000)
    qcode_url = 'https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_={0}'.format(ctime)

    rep = requests.get(
        url=qcode_url
    )
    # print(rep.text)
    qcode = re.findall('uuid = "(.*)";',rep.text)[0]
    session['qcode'] = qcode
    return render_template('login.html',qcode=qcode)

@app.route('/check/login')
def check_login():
    # https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=4dQpYScYHA==&tip=0&r=261182834&_=1550221984438
    qcode = session['qcode']
    ctime = int(time.time() * 1000)
    check_login_url = 'https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid={0}&tip=0&r=261182834&_={1}'.format(qcode,ctime)
    rep = requests.get(url=check_login_url)
    result = {'code':408}

    if 'window.code=408' in rep.text:
        # 用户未扫码
        result['code'] = 408
    elif 'window.code=201' in rep.text:
        # 用户扫码 获取头像
        result['code'] = 201
        result['avatar'] = re.findall("userAvatar = '(.*)';",rep.text)[0]

    elif 'window.code=200' in rep.text:
        # 用户确认登录

        redirect_url = re.findall('window.redirect_uri="(.*)";',rep.text)[0]
        redirect_url = redirect_url + "&fun=new&version=v2"
        # https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?ticket=A7htva9hPz8Zg8UqD0SNv1DW@qrticket_0&uuid=gfZE-OaeKg==&lang=zh_CN&scan=1550225176&fun=new&version=v2 (火狐浏览器)
        print(redirect_url)

        ru = requests.get(url=redirect_url)
        print(ru.text)
        ticket_dict = xml_parse(ru.text)
        session['ticket_dict'] = ticket_dict
        session['ticket_cookies'] = ru.cookies.get_dict()
        result['code'] = 200
    # print(rep.text)
    return jsonify(result)


# 初始化
@app.route('/index')
def index():
    pass_ticket = session['ticket_dict']['pass_ticket']
    print(pass_ticket)
    init_url = 'https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=255090542&lang=zh_CN&pass_ticket={0}'.format(pass_ticket)

    rep = requests.post(
        url=init_url,
        json={
            'BaseRequest':{
                'DeviceID':'e807696598023008',
                'Sid':session['ticket_dict']['wxsid'],
                'Skey':session['ticket_dict']['skey'],
                'Uin':session['ticket_dict']['wxuin'],
            }
        }
    )
    rep.encoding = 'utf-8'
    init_user_dict = rep.json()
    print('*'*20,init_user_dict)
    return render_template('index.html',init_user_dict=init_user_dict)


@app.route('/contact/list')
def contact_list():
    """
    获取联系人列表
    :return:
    """
    ctime = int(time.time() * 1000)
    skey = session['ticket_dict']['skey']
    contact_url = 'https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?r={0}&seq=0&skey={1}'.format(ctime,skey)

    res = requests.get(
        url=contact_url,
        cookies=session['ticket_cookies']
    )
    res.encoding = 'utf-8'
    # print(res.json())
    user_list = res.json()
    return render_template('contact_list.html',user_list=user_list)

@app.route('/get_img')
def get_img():
    # print(request.args)
    prev = request.args.get('prev') # /cgi-bin/mmwebwx-bin/webwxgeticon?seq=670333939
    username = request.args.get('username') # @2beb520fa4bf57aebba8e9ea2893172ab541584a94d3930d5372198b5aa9462c
    skey = request.args.get('skey') # @crypt_f4c59f9_2ef29774d8ab199b70403b9cb3c5d618

    head_img_url = 'https://wx2.qq.com{0}&username={1}&skey={2}'.format(prev,username,skey)
    rep = requests.get(
        url=head_img_url,
        cookies = session['ticket_cookies']
    )
    return rep.content

@app.route('/send/msg',methods=['GET','POST'])
def send_msg():
    if request.method == "GET":
        return render_template('send_msg.html')
    from_user = request.form.get('fromUser')
    to_user = request.form.get('toUser')
    content = request.form.get('content')
    ctime = int(time.time() * 1000)
    data_dict = {
        'BaseRequest': {
            'DeviceID': 'e807696598023008',
            'Sid': session['ticket_dict']['wxsid'],
            'Skey': session['ticket_dict']['skey'],
            'Uin': session['ticket_dict']['wxuin'],
        },
        'Msg':{
            'ClientMsgId':ctime,
            'Content':content,
            'FromUserName':from_user,
            'LocalID':ctime,
            'ToUserName':to_user,
            'Type':1
        },
        'Scene':0
    }
    print('++++++',data_dict)
    #
    msg_url = 'https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg?lang=zh_CN&pass_ticket={0}'.format(session['ticket_dict']['pass_ticket'])
    rep = requests.post(
        url=msg_url,
        data=bytes(json.dumps(data_dict,ensure_ascii=False),encoding='utf-8')
    )
    print(rep)
    return '发送成功'

if __name__ == '__main__':
    app.run()