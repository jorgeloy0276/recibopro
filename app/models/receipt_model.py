import datetime

#Antigua
# from app import mysql
import datetime
from os import abort

#Nueva
from app.database import get_connection



class Receipt:
    """Representa un recibo electrónico completo."""

    def __init__(self, client_name, client_phone, payment_method,
                 items=None, receipt_id=None, receipt_number=None,
                 receipt_date=None, subtotal=0, total=0, pdf_path=None):
        self.id = receipt_id
        self.receipt_number = receipt_number  # e.g. REC-1000
        self.receipt_date = receipt_date
        self.client_name = client_name
        self.client_phone = client_phone
        self.payment_method = payment_method
        # self.items = items or []  # lista de ReceiptItem
        self.subtotal = float(subtotal)
        self.total = float(total)
        self.pdf_path = pdf_path

    # ─────────────────────────────────────────────────────────────
    # Buscar todos
    # ─────────────────────────────────────────────────────────────
    @classmethod
    def get_all(cls):
        try:
            # cur = mysql.connection.cursor()

            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                           SELECT *
                           FROM receipts
                           ORDER BY id DESC
                           """)
            receipts = cursor.fetchall()
            cursor.close()
            return receipts
        except Exception as e:
            print(e)


        # receipts = ""

        # for r in rows:
        #     rec = cls(
        #         client_name    = r['client_name'],
        #         client_phone   = r['client_phone'],
        #         payment_method = r['payment_method'],
        #         receipt_id     = r['id'],
        #         receipt_number = r['receipt_number'],
        #         receipt_date   = r['receipt_date'],
        #         subtotal       = r['subtotal'],
        #         total          = r['total'],
        #         pdf_path       = r['pdf_path'],
        #     )
        #     receipts.append(rec)


    # ─────────────────────────────────────────────────────────────
    # Buscar por ID (con items)
    # ─────────────────────────────────────────────────────────────
    @classmethod
    def get_by_id(cls, receipt_id):
        # cur = mysql.connection.cursor()
        connection = get_connection()
        cur = connection.cursor(dictionary=True)
        cur.execute("SELECT * FROM receipts WHERE id=%s", (receipt_id,))
        receipt = cur.fetchone()

        # --- ITEMS ---
        cur.execute("SELECT * FROM receipt_items WHERE receipt_id=%s", (receipt_id,))
        item_rows = cur.fetchall()
        cur.close()
        return receipt, item_rows

    # ─────────────────────────────────────────────────────────────
    # Generar próximo número de recibo
    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def _next_receipt_number():
        fec_full = datetime.date.today()
        num_rec_fec = fec_full.strftime("%Y%m%d")
        # cur = mysql.connection.cursor()
        connection = get_connection()
        cur = connection.cursor(dictionary=False)
        cur.execute("SELECT receipt_number FROM receipts ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()

        cur.close()

        if row:
            txtlast_num = row[0]
            txtlast_num = txtlast_num[13:16]
            print(txtlast_num)
            # abort()
            last_num = int(txtlast_num)

            return f"REC-{num_rec_fec}-{last_num + 1:03d}"
        # abort()
        return f'REC-{fec_full.strftime("%Y%m%d")}-001'

    def save_receipt(self):
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        # cursor = mysql.connection.cursor()
        query = ("""
                 INSERT INTO receipts (receipt_number, receipt_date, client_name, client_phone, payment_method,
                                       subtotal, total)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)
                 """)
        cursor.execute(query, (self.receipt_number, self.receipt_date, self.client_name, self.client_phone,
                               self.payment_method, self.subtotal, self.total))

        connection.commit()

        cursor.close()
        connection.close()
        # mysql.connection.commit()
        receipt_id = cursor.lastrowid

        return receipt_id


# ─────────────────────────────────────────────────────────────
# Generar próximo número de recibo
# ─────────────────────────────────────────────────────────────


class ReceiptItem:
    """Representa una línea de detalle en el recibo."""

    def __init__(self, description, quantity, unit_price, discount=0.0,
                 item_id=None, receipt_id=None):
        self.id = item_id
        self.receipt_id = receipt_id
        self.description = description
        self.quantity = float(quantity)
        self.unit_price = float(unit_price)
        self.discount = float(discount)  # porcentaje  0-100

    @property
    def to_dict(self):
        return {
            'id': self.id,
            'receipt_id': self.receipt_id,
            'description': self.description,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'discount': self.discount,
            'amount': self.amount,
        }

    def save(self):
        # cursor = mysql.connection.cursor()

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        amount =round (self.quantity * self.unit_price * (1 - self.discount / 100), 2)
        cursor.execute("""
                       INSERT INTO receipt_items (receipt_id, description, quantity, unit_price, discount, amount)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       """, (self.receipt_id, self.description, self.quantity,
                             self.unit_price, self.discount, amount))
        connection.commit()

        # mysql.connection.commit()
        cursor.close()
        connection.close()
        # cursor.execute("UPDATE receipts SET subtotal=%s, total=%s WHERE id=%s",(subtotal, subtotal, receipt_id))

        # ─────────────────────────────────────────────────────────────
        # Actualizar pdf_path luego de generar el PDF
        # ─────────────────────────────────────────────────────────────
class UpdatePDF:
    @staticmethod
    def update_pdf_path( id, pdf_path):

        pdf_path = pdf_path
        # cursor = mysql.connection.cursor()
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("UPDATE receipts SET pdf_path=%s WHERE id=%s",
                    (pdf_path, id))
        connection.commit()
        # mysql.connection.commit()
        cursor.close()
        connection.close()
