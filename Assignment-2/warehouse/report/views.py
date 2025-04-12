from django.shortcuts import render
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, XPreformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from inventory.models import Item
from purchase.models import PurchaseDetail
from sell.models import SellDetail
from datetime import datetime
import json, os

def generate_stock_report_pdf(data, output_path="report/report-pdf/stock_report_output.pdf"):
    result_data = data['result']
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading1']
    styleN9 = ParagraphStyle(
        name="Normal9",
        fontSize=9,
        leading=10,
        spaceBefore=1,
        spaceAfter=1,
        leftIndent=2,
        keepLeadingSpace=True
    )

    elements.append(Paragraph("<b>Stock Report</b>", styleH))
    elements.append(Paragraph(f"Items code : {result_data['item_code']}", styleN))
    elements.append(Paragraph(f"Name : {result_data['name']}", styleN))
    elements.append(Paragraph(f"Unit : {result_data['unit']}", styleN))
    elements.append(Spacer(1, 9))

    table_style = [
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("SPAN", (4, 0), (6, 0)),   # In
        ("SPAN", (7, 0), (9, 0)),   # Out
        ("SPAN", (10, 0), (12, 0)), # Stock
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, 1), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]

    table_data = [
        ["No", "Date", "Description", "Code",
         "In", "", "",
         "Out", "", "",
         "Stock", "", ""],
        ["", "", "", "",
         "qty", "price", "total",
         "qty", "price", "total",
         "qty", "price", "total"]
    ]
    row_heights = [20, 18]

    no = 1
    for idx, item in enumerate(result_data["items"]):
        stock_qty_str = "\n".join([str(q) for q in item['stock_qty']])
        stock_price_str = "\n".join([f"{p:,}" for p in item['stock_price']])
        stock_total_str = "\n".join([f"{t:,}" for t in item['stock_total']])

        row1 = [
            str(no),
            item["date"],
            item["description"],
            item["code"],
            item["in_qty"],
            f"{item['in_price']:,}" if item['in_price'] else 0,
            f"{item['in_total']:,}" if item['in_total'] else 0,
            item["out_qty"],
            f"{item['out_price']:,}" if item['out_price'] else 0,
            f"{item['out_total']:,}" if item['out_total'] else 0,
            XPreformatted(stock_qty_str, styleN9),
            XPreformatted(stock_price_str, styleN9),
            XPreformatted(stock_total_str, styleN9)
        ]

        row2 = [
            Paragraph("Balance", styleN9), "", "",
            "", "", "", "",
            "", "", "",
            item["balance_qty"],
            Paragraph(f"{item['balance']:,}", styleN9),
            ""
        ]

        row_index = 2 + idx * 2 + 1
        table_style.extend([
            ("SPAN", (0, row_index), (3, row_index)),
            ("SPAN", (4, row_index), (6, row_index)),
            ("SPAN", (7, row_index), (9, row_index)),
            ("SPAN", (11, row_index), (12, row_index)),
        ])

        table_data.append(row1)
        row_heights.append(25)

        table_data.append(row2)
        row_heights.append(20)

        no += 1

    summary = result_data["summary"]
    table_data.append([
        "Summary", "", "", "",
        summary["in_qty"], "", "",
        summary["out_qty"], "", "",
        summary["balance_qty"], Paragraph(f"{summary['balance']:,}", styleN9)
    ])

    table_style.extend([
        ("SPAN", (0, len(table_data)-1), (3, len(table_data)-1)),
        ("SPAN", (4, len(table_data)-1), (6, len(table_data)-1)),
        ("SPAN", (7, len(table_data)-1), (9, len(table_data)-1)),
        ("SPAN", (11, len(table_data)-1), (12, len(table_data)-1)),
    ])
    row_heights.append(22)

    col_widths = [25, 50, 100, 40, 25, 45, 50, 25, 45, 50, 25, 45, 50]
    t = Table(table_data, colWidths=col_widths, rowHeights=row_heights)
    t.setStyle(TableStyle(table_style))

    elements.append(t)
    doc.build(elements)
    print(f"✅ PDF berhasil dibuat: {output_path}")

class StockReportJSON(APIView):
    def get(self, request, item_code):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response(
                {"code": status.HTTP_400_BAD_REQUEST, "message": "start_date and end_date are required"},
                status=status.HTTP_200_OK
            )

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"code": status.HTTP_400_BAD_REQUEST, "message": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_200_OK
            )

        try:
            item = Item.objects.get(code=item_code, is_deleted=False)
        except Item.DoesNotExist:
            return Response(
                {"code": status.HTTP_404_NOT_FOUND, "message": "Item not found."},
                status=status.HTTP_200_OK
            )

        transactions = []

        purchases = PurchaseDetail.objects.filter(
            item__code=item_code,
            item__is_deleted=False,
            header__is_deleted=False,
            header__date__range=(start_date, end_date)
        ).select_related('header')

        for p in purchases:
            transactions.append({
                "date": p.header.date.strftime('%d-%m-%Y'),
                "description": p.header.description,
                "code": p.header.code,
                "in_qty": p.quantity,
                "in_price": p.unit_price,
                "in_total": p.quantity * p.unit_price,
                "out_qty": 0,
                "out_price": 0,
                "out_total": 0,
                "type": "purchase"
            })

        sells = SellDetail.objects.filter(
            item__code=item_code,
            item__is_deleted=False,
            header__is_deleted=False,
            header__date__range=(start_date, end_date)
        ).select_related('header')

        for s in sells:
            transactions.append({
                "date": s.header.date.strftime('%d-%m-%Y'),
                "description": s.header.description,
                "code": s.header.code,
                "in_qty": 0,
                "in_price": 0,
                "in_total": 0,
                "out_qty": s.quantity,
                "out_price": 0,
                "out_total": 0,
                "type": "sell"
            })

        transactions.sort(key=lambda x: datetime.strptime(x["date"], '%d-%m-%Y'))

        stock_batches = []
        for tx in transactions:
            if tx['type'] == 'purchase':
                stock_batches.append([tx['in_qty'], tx['in_price']])
            elif tx['type'] == 'sell':
                qty_needed = tx['out_qty']
                used_batches = []
                i = 0
                while qty_needed > 0 and i < len(stock_batches):
                    batch_qty, batch_price = stock_batches[i]
                    if batch_qty == 0:
                        i += 1
                        continue
                    used_qty = min(qty_needed, batch_qty)
                    used_batches.append((used_qty, batch_price))
                    
                    # Kurangi langsung stok batch
                    stock_batches[i][0] -= used_qty
                    qty_needed -= used_qty

                    if stock_batches[i][0] == 0:
                        i += 1

                if used_batches:
                    tx['out_price'] = used_batches[0][1] if len(used_batches) == 1 else 0  
                    tx['out_total'] = sum(q * p for q, p in used_batches)


            active_batches = [(qty, price) for qty, price in stock_batches if qty > 0]
            stock_qty_list = [q for q, _ in active_batches]
            stock_price_list = [p for _, p in active_batches]
            stock_total_list = [q * p for q, p in active_batches]

            tx['stock_qty'] = stock_qty_list
            tx['stock_price'] = stock_price_list
            tx['stock_total'] = stock_total_list
            tx['balance_qty'] = sum(stock_qty_list)
            tx['balance'] = sum(stock_total_list)


        in_qty = sum(tx['in_qty'] for tx in transactions)
        out_qty = sum(tx['out_qty'] for tx in transactions)
        in_total = sum(tx['in_total'] for tx in transactions)
        out_total = sum(tx['out_total'] for tx in transactions)

        summary = {
            "in_qty": in_qty,
            "out_qty": out_qty,
            "balance_qty": in_qty - out_qty,
            "balance": in_total - out_total
        }

        final_output = {
            "result": {
                "item_code": item.code,
                "name": item.name,
                "unit": item.unit,
                "items": transactions,
                "summary": summary
            }
        }

        today = datetime.now().strftime("%Y-%m-%d")
        os.makedirs('documentation/report-json/', exist_ok=True)
        os.makedirs('documentation/report-pdf/', exist_ok=True)

        length_file_json = len(os.listdir('documentation/report-json/')) + 1
        length_file_pdf = len(os.listdir('documentation/report-pdf/')) + 1

        generate_stock_report_pdf(final_output, f'documentation/report-pdf/werehouse-report-{today}-{length_file_pdf}.pdf')

        with open(f"documentation/report-json/werehouse-report-{today}-{length_file_json}.json", "w") as f:
            json.dump(final_output, f, indent=4)

        return Response(final_output)