from flask import Blueprint
from app.controllers.receipt_controller import ReceiptController
from app.services.pdf_service import PDF_QR_Service
from  app.services.email_notifications import EmailNotifications

receipt_bp = Blueprint('receipts', __name__)

pdf_bp = Blueprint('pdfs', __name__)

email_bp = Blueprint('emails', __name__)
# ─────────────────────────────────────────────────────────────────────────────
# RUTA: INDEX — lista todos los recibos
# ─────────────────────────────────────────────────────────────────────────────

receipt_bp.route('/')(ReceiptController.index)

receipt_bp.route('/create_receipt', methods=['GET', 'POST'])(ReceiptController.create_receipt)

# ─────────────────────────────────────────────────────────────────────────────
# RUTA: NUEVO RECIBO — formulario
# ─────────────────────────────────────────────────────────────────────────────
receipt_bp.route('/recibo/nuevo', methods=['GET'])(ReceiptController.nuevo_recibo)


# ─────────────────────────────────────────────────────────────────────────────
# CREAR RECIBO — procesar POST
# ─────────────────────────────────────────────────────────────────────────────
receipt_bp.route('/receipt/create', methods=['POST'])(ReceiptController.create_receipt)


# ─────────────────────────────────────────────────────────────────────────────
# RUTA: VER RECIBO
# ─────────────────────────────────────────────────────────────────────────────
receipt_bp.route('/ver_recibo/<int:id>', methods=['GET', 'POST'])(ReceiptController.ver_recibo)

# ─────────────────────────────────────────────────────────────────────────────
# RUTA: GENERAR PDF
# ─────────────────────────────────────────────────────────────────────────────
pdf_bp.route('/generar_pdf/<int:id>', methods=['GET','POST'])(PDF_QR_Service.generate_pdf)

# ─────────────────────────────────────────────────────────────────────────────
# RUTA: EGENERAR PDF
# ─────────────────────────────────────────────────────────────────────────────
receipt_bp.route('/regenerar_pdf/<int:id>', methods=['GET','POST'])(ReceiptController.regenerate_pdf)
#

# ─────────────────────────────────────────────────────────────────────────────
# RUTA: ENVIAR NOTIFICACION POR CORREO
# ─────────────────────────────────────────────────────────────────────────────
email_bp.route('/enviar_correo/<receipt_number>/<html_body>',methods=['GET','POST'] )(EmailNotifications.send_notification)
