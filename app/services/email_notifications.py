
from flask_mail import Mail, Message
from app import mail  # Importamos mail desde __init__.py

from flask import flash, redirect, render_template, request, url_for



from app.services.pdf_service import PDF_QR_Service





class EmailNotifications:
    @staticmethod
    def send_notification(receipt_number, html_body):

        PDF_QR_Service.generate_qr_image('REC-20260521-999')
        msg = Message(
            subject=f'Notificacion de nuevo Recibo # {receipt_number}',
            sender='kryptonlogicpty@gmail.com',
            recipients=['jorgeloy0276@gmail.com', 'kryptonlogicpty@gmail.com'],
            html =html_body
        )
        try:
            mail.send(msg)

        except Exception as e:
            print( f'Hubo un problema al enviar el correo.. Error: {e}')
            flash(f'Hubo un problema al enviar el correo.. Error: {e}', 'danger')
            return redirect(url_for('receipts.index'))


        flash(f'Recibo {receipt_number} enviado correctamente por email.', 'success')
        return redirect(url_for('receipts.index'))

