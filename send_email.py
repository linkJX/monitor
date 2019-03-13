import smtplib
from email.mime.text import MIMEText
from email.header import Header


def send(content, subject):
    from_addr = 'link690@126.com'
    password = 'qwertyui0p'
    smtp_server = 'smtp.126.com'
    to_addr = 'pacinolin@126.com'

    msg = MIMEText(content, 'html', 'utf-8')
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = Header(subject, 'utf-8').encode()

    server = smtplib.SMTP_SSL(smtp_server, 465)
    # server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()

