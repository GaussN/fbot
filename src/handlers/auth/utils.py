import smtplib
from email.message import EmailMessage
from string import ascii_letters, digits
from random import choices

from config import GOOGLE_LOGIN, GOOGLE_PASSWORD
from config import BOT_NAME


def _send_mail(from_: str, to: str, msg: str):
    with smtplib.SMTP('smtp.gmail.com', 587) as client:
        client.starttls()
        client.login(GOOGLE_LOGIN, GOOGLE_PASSWORD)
        return client.sendmail(from_, to, msg)


def gen_verify_code(length: int = 5) -> str:
    return ''.join(choices(ascii_letters + digits, k=length))


def send_verify_code(recipient: str, code: str):
    body = f"""<p>Твой код для регистрации в {BOT_NAME}:</p>
    <h1>{code}</h1>
    </br>
    <small>Не отвечайте на это письмо</small>
    """
    msg = EmailMessage()
    msg['From'] = GOOGLE_LOGIN
    msg['To'] = recipient
    msg['Subject'] = 'Код верификации'
    msg.set_content(body, subtype='html')
    return _send_mail(GOOGLE_LOGIN, recipient, msg.as_string())
