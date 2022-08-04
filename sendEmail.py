import smtplib
import ssl

from models import Voter, Admin


class sendEmails():
    gmail_user = 'uics5800@gmail.com'
    gmail_password = 'Gohawks21!'

    sent_from = gmail_user
    subject = 'Reset Passcode'
    body = 'Code: 5800'

    def __init__(self):
        '''email_text = """\
        From: %s
        To: %s
        Subject: %s
        
        %s
        """ % (sent_from, ", ".join(to), subject, body)'''

    def send_mail(self, email, code):
        # token = User.get_token()
        port = 587  # For starttls
        smtp_server = "smtp.gmail.com"
        sender_email = "uiowacs5800@gmail.com"
        receiver_email = email
        password = 'Gohawks21!'
        message = f'''
        From: {sender_email}
        To: {receiver_email}
        Subject: {"Reset Password"}
               Here is the code to reset your password:

               {code}

               If you did not send a passcode request, please ignore this message.

               '''

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)

        '''msg = """\
                From: %s
                To: %s
                Subject: %s
    
                %s
                """ % (sendEmails.sent_from, ", ".join(email), sendEmails.subject, body)
        # context = ssl.create_default_context()
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        try:
            smtp_server.ehlo()
            # smtp_server.starttls(context=context)
            smtp_server.login(sendEmails.gmail_user, sendEmails.gmail_password)
            smtp_server.sendmail(sendEmails.sent_from, [email], body)
            smtp_server.close()
            print ("Email sent successfully!")
        except Exception as ex:
            print ("Something went wrong….",ex)
        finally:
            smtp_server.quit()'''


# send = sendEmails()
# send.send_mail("wdbobcats54@gmail.com")

class SendApprovalEmails:
    gmail_user = 'uics5800@gmail.com'
    gmail_password = 'Gohawks21!'

    sent_from = gmail_user
    subject = 'Profile Approval'

    def __init__(self):
        '''email_text = """\
        From: %s
        To: %s
        Subject: %s

        %s
        """ % (sent_from, ", ".join(to), subject, body)'''

    def send_approval_mail(self, email):
        # token = User.get_token()
        port = 587  # For starttls
        smtp_server = "smtp.gmail.com"
        sender_email = "uiowacs5800@gmail.com"
        receiver_email = email
        password = 'Gohawks21!'
        message = f'''
        From: {sender_email}
        To: {receiver_email}
        Subject: Congratulations! Your profile creation request has been approved. You can login to vote now.
               '''
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)

    def send_denial_mail(self, email):
        # token = User.get_token()
        port = 587  # For starttls
        smtp_server = "smtp.gmail.com"
        sender_email = "uiowacs5800@gmail.com"
        receiver_email = email
        password = 'Gohawks21!'
        message = f'''
          From: {sender_email}
          To: {receiver_email}
          Subject: Sorry! your profile creation request has been denied.
                 '''
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)

    def send_authorization_mail(self, email):
        # token = User.get_token()
        port = 587  # For starttls
        smtp_server = "smtp.gmail.com"
        sender_email = "uiowacs5800@gmail.com"
        receiver_email = email
        password = 'Gohawks21!'
        message = f'''
             From: {sender_email}
             To: {receiver_email}
             Subject: You have been authorized to access your assigned poll station.
                    '''
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
