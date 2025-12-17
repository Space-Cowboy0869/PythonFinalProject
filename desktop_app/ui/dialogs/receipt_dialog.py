from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox, QPushButton, QFileDialog, QMessageBox
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtCore import Qt
from decimal import Decimal
import html
from ...database import db_session
from ...models import Transaction
from ...utils.helpers import format_currency, compute_ph_vat_breakdown, PH_VAT_RATE


class ReceiptDialog(QDialog):
    def __init__(self, transaction_id: int, parent=None):
        super().__init__(parent)
        self.transaction_id = transaction_id
        self.setWindowTitle(f"Receipt #{transaction_id}")
        self.setMinimumSize(420, 600)
        self._build_ui()
        self._load_receipt()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setAcceptRichText(True)
        self.text.setStyleSheet("QTextEdit { background: #ffffff; color: #000000; }")
        layout.addWidget(self.text)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn_print = QPushButton("Print")
        btn_pdf = QPushButton("Save PDF")

        btn_print.clicked.connect(self.print_receipt)
        btn_pdf.clicked.connect(self.save_pdf)

        buttons.addButton(btn_print, QDialogButtonBox.ButtonRole.ActionRole)
        buttons.addButton(btn_pdf, QDialogButtonBox.ButtonRole.ActionRole)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)

        layout.addWidget(buttons)

    def _load_receipt(self):
        tx = db_session.get(Transaction, self.transaction_id)
        if not tx:
            self.text.setPlainText("Transaction not found")
            return

        items = list(tx.items or [])
        date_str = tx.created_at.strftime('%Y-%m-%d %H:%M:%S')

        meta_rows = []
        if tx.employee:
            meta_rows.append(
                "<tr><td class='label'>Employee</td><td class='value'>"
                f"{html.escape(str(tx.employee.username))}"
                "</td></tr>"
            )
        if tx.customer_name:
            meta_rows.append(
                "<tr><td class='label'>Customer</td><td class='value'>"
                f"{html.escape(str(tx.customer_name))}"
                "</td></tr>"
            )
        if tx.customer_phone:
            meta_rows.append(
                "<tr><td class='label'>Phone</td><td class='value'>"
                f"{html.escape(str(tx.customer_phone))}"
                "</td></tr>"
            )
        meta_rows.append(
            "<tr><td class='label'>Payment</td><td class='value'>"
            f"{html.escape(str(tx.payment_method))}"
            "</td></tr>"
        )
        # Show cash/gcash details if present
        if getattr(tx, 'cash_received', None) is not None:
            meta_rows.append(
                "<tr><td class='label'>Cash Received</td><td class='value'>"
                f"{format_currency(tx.cash_received)}"
                "</td></tr>"
            )
        if getattr(tx, 'change_amount', None) is not None:
            meta_rows.append(
                "<tr><td class='label'>Change</td><td class='value'>"
                f"{format_currency(tx.change_amount)}"
                "</td></tr>"
            )
        if getattr(tx, 'gcash_ref', None):
            meta_rows.append(
                "<tr><td class='label'>GCash Ref</td><td class='value'>"
                f"{html.escape(str(tx.gcash_ref))}"
                "</td></tr>"
            )

        item_rows = []
        for it in items:
            name = it.product.name if it.product else f"Product #{it.product_id}"
            qty = it.qty
            price = Decimal(str(it.price))
            line_total = price * int(qty)
            item_rows.append(
                "<tr>"
                f"<td class='item'>{html.escape(str(name))}</td>"
                f"<td class='qty'>{qty}</td>"
                f"<td class='num'>{format_currency(price)}</td>"
                f"<td class='num'>{format_currency(line_total)}</td>"
                "</tr>"
            )

        if not item_rows:
            item_rows.append("<tr><td class='empty' colspan='4'>No items</td></tr>")

        vatable_sales, vat_amount, total = compute_ph_vat_breakdown(Decimal(str(tx.total)), prices_include_vat=True)

        lines = []
        lines.append("<html><head><style>")
        lines.append(
            """
            body { margin: 0; padding: 0; background: #ffffff; }
            .receipt { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; color: #000000; padding: 18px; }
            .title { text-align: center; font-size: 18px; font-weight: 700; margin: 0; }
            .subtitle { text-align: center; font-size: 11px; margin-top: 3px; }
            .divider { border-top: 2px solid #00b050; margin: 12px 0; }

            table { width: 100%; }
            .meta { border-collapse: collapse; font-size: 11px; }
            .meta td { padding: 2px 0; }
            .meta .label { color: #000000; }
            .meta .value { text-align: right; color: #000000; }

            .items { border-collapse: collapse; font-size: 11px; }
            .items thead th { background: #000000; color: #ffffff; padding: 6px 6px; border: 1px solid #00b050; }
            .items tbody td { padding: 6px 6px; border-bottom: 1px solid #00b050; vertical-align: top; }
            .items td.item { width: 55%; }
            .items td.qty { width: 10%; text-align: right; }
            .items td.num { text-align: right; white-space: nowrap; }
            .items td.empty { text-align: center; padding: 14px 6px; }

            .totals { border-collapse: collapse; font-size: 11px; }
            .totals td { padding: 3px 0; }
            .totals .label { color: #000000; }
            .totals .value { text-align: right; color: #000000; white-space: nowrap; }
            .totals .grand td { font-size: 14px; font-weight: 700; padding-top: 10px; }

            .footer { text-align: center; font-size: 11px; margin-top: 12px; color: #000000; }
            .footer .line { border-top: 1px dashed #00b050; margin-top: 12px; padding-top: 10px; }
            """
        )
        lines.append("</style></head><body>")

        lines.append("<div class='receipt'>")
        lines.append("<div class='title'>POS Receipt</div>")
        lines.append(f"<div class='subtitle'>Receipt #<b>{tx.id}</b></div>")
        lines.append(f"<div class='subtitle'>{html.escape(date_str)}</div>")
        lines.append("<div class='divider'></div>")

        lines.append("<table class='meta'>")
        lines.append("".join(meta_rows))
        lines.append("</table>")
        lines.append("<div class='divider'></div>")

        lines.append("<table class='items'>")
        lines.append(
            "<thead><tr>"
            "<th align='left'>Item</th>"
            "<th align='right'>Qty</th>"
            "<th align='right'>Price</th>"
            "<th align='right'>Total</th>"
            "</tr></thead>"
        )
        lines.append("<tbody>")
        lines.append("".join(item_rows))
        lines.append("</tbody></table>")

        lines.append("<div class='divider'></div>")

        lines.append("<table class='totals'>")
        lines.append(
            "<tr><td class='label'>VATable Sales</td>"
            f"<td class='value'>{format_currency(vatable_sales)}</td></tr>"
        )
        lines.append(
            "<tr><td class='label'>VAT ("
            f"{int(PH_VAT_RATE * 100)}%"
            ")</td>"
            f"<td class='value'>{format_currency(vat_amount)}</td></tr>"
        )
        lines.append(
            "<tr class='grand'><td class='label'>Total</td>"
            f"<td class='value'>{format_currency(total)}</td></tr>"
        )
        lines.append("</table>")

        lines.append("<div class='footer'><div class='line'>Thank you for your purchase!</div></div>")
        lines.append("</div></body></html>")

        self.text.setHtml("\n".join(lines))

    def print_receipt(self):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dlg = QPrintDialog(printer, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.text.document().print(printer)

    def save_pdf(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Receipt", f"receipt_{self.transaction_id}.pdf", "PDF Files (*.pdf)")
        if not filename:
            return

        try:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(filename)
            self.text.document().print(printer)
            QMessageBox.information(self, "Saved", "Receipt saved.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
