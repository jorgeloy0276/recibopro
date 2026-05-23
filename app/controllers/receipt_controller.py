import os
from flask import (render_template, request,
                   redirect, url_for, flash, current_app, abort)

from app.services.pdf_service import PDF_QR_Service
from app.models.receipt_model import Receipt, ReceiptItem, UpdatePDF
# from app.models.receipt_model import Receipt
from app.services.email_notifications import EmailNotifications
# from app.services.pdf_service import generate_pdf
from config import Config
import datetime


class ReceiptController:

    @staticmethod
    def index():
        receipts = Receipt.get_all()
        #
        # print(receipts)
        # print(len(receipts))
        # abort(404)
        return render_template('receipts/index.html', receipts=receipts)

    @staticmethod
    def ver_recibo(id):
        receipts, items_rows = Receipt.get_by_id(int(id))

        if not receipts:
            abort(404)
        # print(receipts['pdf_path'])
        # abort(404)
        # Construir URL pública del PDF
        pdf_url = url_for('static', filename=f'export/{receipts['pdf_path']}', _external=True) \
            if receipts['pdf_path'] else None

        # print(f'celular sucio: {receipts['client_phone']}')
        # Link de WhatsApp
        phone_clean = ''.join(filter(str.isdigit, receipts['client_phone']))

        wa_text = (
            f"Hola {receipts['client_name']},"
            f"te adjunto tu recibo de servicios "
            f"{receipts['receipt_number']}. \n"
            f"\n"
            f"\n"
            f"Puedes verlo aquí: \n"
            f"{pdf_url}"
        )

        import urllib.parse
        wa_link = f"https://wa.me/{phone_clean}?text={urllib.parse.quote(wa_text)}" \
            if phone_clean else None
        # print(f'mensaje ws: {wa_link}')

        return render_template('receipts/receipt-details.html', receipts=receipts, pdf_url=pdf_url, wa_link=wa_link,
                               items_rows=items_rows)

    @staticmethod
    def nuevo_recibo():
        nuevo_num_recibo = Receipt._next_receipt_number()

        return render_template('receipts/new_receipt.html', nuevo_num_recibo=nuevo_num_recibo)

    @staticmethod
    def create_receipt():
        # Otra manera de hacer request a traces del form, declarando el request por otra variable.

        form = request.form
        if request.method == 'POST':
            # Genera nuevo numero de recibo
            nuevo_num_recibo = Receipt._next_receipt_number()

            # Datos principales
            client_name = form.get('client_name', '').strip()
            client_phone = form.get('client_phone', '').strip()
            client_phone = '507' + client_phone
            payment_method = form.get('payment_method', '').strip()
            receipt_number = nuevo_num_recibo
            receipt_date = datetime.date.today()

            # Recolectar items dinámicos (campo name = "description[]", etc.)
            descriptions = form.getlist('description[]')
            quantities = form.getlist('quantity[]')
            unit_prices = form.getlist('unit_price[]')
            discounts = form.getlist('discount[]')

            # Insertar cabecera
            subtotal = sum(
                float(p) * int(q) * (1 - (int(d) / 100)) for p, q, d in zip(unit_prices, quantities, discounts))
            # print(f'Subtotal = {subtotal}')
            total = subtotal  # aquí podrías sumar impuestos u otros cargos

            receipt = Receipt(
                receipt_number=receipt_number,
                receipt_date=receipt_date,
                client_name=client_name,
                client_phone=client_phone,
                payment_method=payment_method,
                subtotal=subtotal,
                total=total,

            )
            actual_rec_id = receipt.save_receipt()

            for desc, qty, price in zip(descriptions, quantities, unit_prices):
                receipt_items = ReceiptItem(description=desc, quantity=qty, unit_price=price, receipt_id=actual_rec_id)
                receipt_items.save()

            # Generar PDF
            # export_dir = os.path.join(current_app.root_path, 'static', 'export')
            pdf_filename = PDF_QR_Service.generate_pdf(actual_rec_id)
            # print(pdf_filename)
            UpdatePDF.update_pdf_path(actual_rec_id, pdf_filename)

            html_body = f'''

            <h2><strong> Creacion de nuevo recibo  </strong></h2>
            <p>Se ha generado el siguiente recibo No. {receipt.receipt_number}  para el cliente {receipt.client_name} </p>
             <p> por un monto de {total} </p>

             <p> Gracias por preferirnos </p>
            '''

            try:
                EmailNotifications.send_notification(receipt.receipt_number, html_body)
            except Exception as e:
                flash(f'Hubo un problema al enviar el correo..', 'danger')

            flash(f'Recibo {receipt.receipt_number} creado exitosamente.', 'success')
        return redirect(url_for('receipts.ver_recibo', id=actual_rec_id))

    # ─────────────────────────────────────────────────────────────────────────────
    # RE-GENERAR PDF — por si se necesita otro
    # ─────────────────────────────────────────────────────────────────────────────
    @staticmethod
    def regenerate_pdf(id):

        # receipt = Receipt.get_by_id(id)
        export_dir = os.path.join(current_app.root_path, 'static', 'export')
        pdf_filename = PDF_QR_Service.generate_pdf(id)
        # Construir URL pública del PDF
        # pdf_url = url_for('static', filename=f'export/{pdf_filename}', _external=False) \

        # UpdatePDF.update_pdf_path(id, [pdf_filename])
        UpdatePDF.update_pdf_path(id, pdf_filename)

        flash(f'PDF regenerado satisfactoriamente!.', 'success')
        # return redirect(url_for('receipts.ver_recibo', id=receipt.id))
        return redirect(url_for('receipts.ver_recibo', id=id))
