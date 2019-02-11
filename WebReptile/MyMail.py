# -*- coding: UTF-8 -*-
import smtplib
#def MyMail(mailto_list)

from email.mime.text import MIMEText  
  
def send_mail(to_list,sub,content):
    mail_host="smtp.139.com"  #设置服务器
    mail_user="13568827344"    #用户名
    mail_pass="ben139321"   #口令 
    mail_postfix="139.com"  #发件箱的后缀
    me="hello"+"<"+mail_user+"@"+mail_postfix+">"  
    msg = MIMEText(content,_subtype='plain',_charset='gb2312')  
    msg['Subject'] = sub  
    msg['From'] = me  
    msg['To'] = ";".join(to_list)  
    try:  
        server = smtplib.SMTP()  
        server.connect(mail_host)  
        server.login(mail_user,mail_pass)  
        server.sendmail(me, to_list, msg.as_string())  
        server.close()  
        return True  
    except Exception as e:  
        print(str(e))
        return False  
if __name__ == '__main__':
    mailto_list=['a5192179@126.com']
    if send_mail(mailto_list,"hello","hello world！"):  
        print ("发送成功")
    else:  
        print ("发送失败")
