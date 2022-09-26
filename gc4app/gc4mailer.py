from flask_mail import Mail, Message
from flask import current_app 
from .factory import mail
import os

# sendMSG(sender,recipient,subject,msg)

def sendMSG(email,gc4uid,jobName,app,mail=mail,status=True):
    with app.app_context():
        #mail = Mail(app)
        recipients = [email]
        print("recipients",recipients)
        if status == False:
            body = """
                <p>
                Your job <a href="{0}/job={1}" target="_blank">{0}/job={1}{2}</a> could not be finished.
                We have been notified and will try to solve this as soon as possible.
                Sorry the inconveniences.
                </p>
            """
            msg = Message('GeneCodis4 Results',sender=os.getenv("MAIL_USERNAME"),
                recipients=recipients,bcc=[os.getenv("MAIL2_NAME")])
        else:
            body = """
                <p>
                Your job <a href="{0}/job={1}" target="_blank">{0}/job={1}{2}</a> is finished.
                </p>
                <p>Please, if you use GeneCodis, remember to cite:</p>
                <p><a href="https://doi.org/10.3390/biomedicines10030590" target="_blank">
                Garcia-Moreno, A.; López-Domínguez, R.; Villatoro-García, J.A.; Ramirez-Mena, A.; Aparicio-Puerta, E.; Hackenberg, M.; Pascual-Montano, A.; Carmona-Saez, P. Functional Enrichment Analysis of Regulatory Elements. Biomedicines 2022, 10, 590.
                </a></p>
                """
            msg = Message('GeneCodis4 Results',sender=os.getenv("MAIL_USERNAME"),recipients=recipients)
        jobName = '' if jobName == 'input1' else ' - '+jobName
        msg.html = body.format(os.getenv("API_URL"),gc4uid,jobName)
        
        print("msg",msg)
        mail.send(msg)
