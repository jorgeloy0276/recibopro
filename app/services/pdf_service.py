# app/services/pdf_service.py
import os
import io
from fileinput import filename
from os import abort

import app
from flask import render_template, redirect, url_for, flash
from flask import current_app
from random import randint

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                Paragraph, Spacer, HRFlowable, Image)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

from app.models.receipt_model import Receipt
from flask import current_app
import qrcode


class PDF_QR_Service:
    @staticmethod
    def generate_qr_image(receipt_number: str) -> str:
        # Generate an unique validation number for the QR
        strCode = ""
        for i in range(20):
            strCode = strCode + str(randint(0,9))

        # Write to a file-like object:
        # Generate the QR code
        img = qrcode.make(f'RECIBO: <<{receipt_number}>> | UUID:  {strCode}')


        # Construir la ruta absoluta dentro de static/qr
        export_dir = os.path.join(current_app.root_path, "static", "qr")
        os.makedirs(export_dir, exist_ok=True)  # crea la carpeta si no existe

        filename = f'{receipt_number}.png'
        # Nombre del archivo
        file_path = os.path.join(export_dir, filename)

        # Guardar el archivo en esa ruta
        img.save(file_path)

        return file_path


    @staticmethod
    def generate_pdf(id):
        """
        Genera el PDF del recibo y lo guarda en export_dir.
        Retorna la ruta relativa para servir con url_for (static/export/REC-1000.pdf).
        """
        receipt, items = Receipt.get_by_id(id)

        filename = f"{receipt['receipt_number']}.pdf"
        export_dir = os.path.join(current_app.root_path, 'static', 'export')
        full_path = os.path.join(export_dir, filename)

        doc = SimpleDocTemplate(
            full_path,
            pagesize=A4,
            rightMargin=1.5 * cm, leftMargin=1.5 * cm,
            topMargin=1.5 * cm, bottomMargin=1.5 * cm,
        )
        # print(type(receipt))
        styles = getSampleStyleSheet()
        story = []

        # ── Paleta de colores ────────────────────────────────────────
        DARK = colors.HexColor('#0f172a')
        ACCENT = colors.HexColor('#3135F0')
        LIGHT = colors.HexColor('#f8fafc')
        GRAY = colors.HexColor('#94a3b8')
        WHITE = colors.white

        # ── Estilos de texto ─────────────────────────────────────────

        title_style1 = ParagraphStyle('Title', fontSize=19, textColor=DARK,
                                      alignment=TA_CENTER, spaceAfter=15,
                                      fontName='Helvetica-Bold')
        title_style2 = ParagraphStyle('Title', fontSize=15, textColor=ACCENT,
                                      alignment=TA_CENTER, spaceAfter=15,
                                      fontName='Helvetica-Bold')
        sub_style = ParagraphStyle('Sub', fontSize=9, textColor=GRAY,
                                   alignment=TA_CENTER, spaceAfter=6)
        label_style = ParagraphStyle('Label', fontSize=10, textColor=GRAY,
                                     fontName='Helvetica')
        value_style = ParagraphStyle('Value', fontSize=10, textColor=DARK,
                                     fontName='Helvetica-Bold')
        total_style = ParagraphStyle('Total', fontSize=14, textColor=WHITE,
                                     fontName='Helvetica-Bold', alignment=TA_RIGHT)
        footer_style = ParagraphStyle('Footer', fontSize=10, textColor=GRAY,
                                      alignment=TA_CENTER, spaceBefore=20)

        # ── Encabezado ───────────────────────────────────────────────
        story.append(Paragraph("KRYPTON LOGIC", title_style1))
        story.append(Paragraph("RECIBO DE SERVICIOS", title_style2))
        story.append(Paragraph("Sistema de Facturación Electrónica", sub_style))
        story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))

        # ── Info del recibo (tabla 2 col) ────────────────────────────
        date_str = receipt['receipt_date'].strftime('%d/%m/%Y %H:%M') \
            if hasattr(receipt['receipt_date'], 'strftime') \
            else str(receipt['receipt_date'])

        info_data = [
            [Paragraph("N° de Recibo", label_style),
             Paragraph(receipt['receipt_number'], value_style),
             Paragraph("Fecha", label_style),
             Paragraph(date_str, value_style)],
            [Paragraph("Cliente", label_style),
             Paragraph(receipt['client_name'], value_style),
             Paragraph("Teléfono", label_style),
             Paragraph(receipt['client_phone'], value_style)],
            [Paragraph("Forma de Pago", label_style),
             Paragraph(receipt['payment_method'], value_style), '', ''],
        ]

        info_table = Table(info_data, colWidths=[3 * cm, 7 * cm, 3 * cm, 5 * cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LIGHT),
            ('ROWBACKGROUND', (0, 0), (-1, -1), [LIGHT, WHITE, LIGHT]),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#e2e8f0')),
            ('ROUNDEDCORNERS', [4, 4, 4, 4]),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.4 * cm))


        # ── Tabla de items ───────────────────────────────────────────
        header = ['Descripción', 'Cant.', 'P. Unit.', 'Desc. %', 'Monto']
        table_data = [header]

        for item in items:
            table_data.append(
                [item['description'], f"{item['quantity']:,.2f}", f"${item['unit_price']:,.2f}",
                 f"{item['discount']:.1f}%", f"${item['amount']:,.2f}", ])

        col_widths = [8 * cm, 2 * cm, 2.8 * cm, 2.2 * cm, 3 * cm]
        items_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        items_table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), ACCENT),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            # Filas alternadas
            ('ROWBACKGROUND', (0, 1), (-1, -1), [WHITE, colors.HexColor('#f1f5f9')]),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#e2e8f0')),
        ]))

        # ── Agrega items a story  ──────────────────────────────────────────────────
        story.append(items_table)
        story.append(Spacer(1, 0.3 * cm))

        # ── Totales ──────────────────────────────────────────────────
        totals_data = [
            ['', 'Subtotal:', f"${receipt['subtotal']:,.2f}"],
            ['', 'TOTAL:', f"${receipt['total']:,.2f}"],
        ]

        totals_table = Table(totals_data, colWidths=[11 * cm, 3.5 * cm, 3.5 * cm])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, 1), 12),
            ('TEXTCOLOR', (0, 0), (-1, 0), DARK),
            ('BACKGROUND', (1, 1), (-1, 1), ACCENT),
            ('TEXTCOLOR', (1, 1), (-1, 1), WHITE),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('ROUNDEDCORNERS', [4, 4, 4, 4]),
        ]))
        story.append(totals_table)
        story.append(Spacer(1, 0.5 * cm))

        # ── Fin Tabla Items ─────────────────────────────────────────────

        # ── Código de barras ─────────────────────────────────────────
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0'), spaceAfter=20))
        story.append(Paragraph("Código de Verificación", sub_style))

        try:
            bc_png = PDF_QR_Service.generate_qr_image(receipt['receipt_number'])
            bc_img = Image(bc_png, width=5 * cm, height=5 * cm)
            bc_img.hAlign = 'CENTER'
            story.append(bc_img)
        except Exception as e:
            story.append(Paragraph(f"[Código de barras: {receipt['receipt_number']}]", sub_style))

        # print(f'contenido de story HEADER + INFO TABLA + ITEMS TABLA + TOTAL TABLE -->       {story}')

        # ── Pie de página ─────────────────────────────────────────────

        story.append(Spacer(1, 0.3 * cm))
        # VERIFICAR DESPUES COMO ARREGLAR ESTA LINEA PARA QUE QUEDE ARRIBA DEL TEXTO
        # story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY, spaceBefore=5))
        story.append(Paragraph(
            "Gracias por su preferencia · Este recibo es válido como comprobante de pago",
            footer_style
        ))

        doc.build(story)
        # return filename  # solo el nombre, la ruta estática la maneja Flask
        story = []

        # for item in items:
        #     print(item['description'])
        # def generate_pdf(receipt, export_dir: str) -> str:

        return filename
