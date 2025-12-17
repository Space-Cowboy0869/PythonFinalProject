import os
import shutil
import uuid
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_icon_path(icon_name: str) -> str:
    if not icon_name:
        return ""

    root = project_root()
    candidates = [
        root / "static" / "icons" / icon_name,
        root / "static" / icon_name,
        root / "desktop_app" / "static" / "icons" / icon_name,
        root / "desktop_app" / "static" / icon_name,
    ]

    for p in candidates:
        if p.exists():
            return str(p)

    return ""


def load_icon(icon_name: str):
    try:
        from PyQt6.QtGui import QIcon
        from PyQt6.QtWidgets import QApplication, QStyle
    except Exception:
        return None

    if not icon_name:
        return QIcon()

    path = get_icon_path(icon_name)
    if path:
        icon = QIcon(path)
        if not icon.isNull():
            return icon

    app = QApplication.instance()
    style = app.style() if app is not None else None
    if style is None:
        return QIcon()

    fallback_names = {
        "app_icon.png": "SP_ComputerIcon",
        "logo.png": "SP_ComputerIcon",
        "menu.png": "SP_TitleBarMenuButton",
        "dashboard.png": "SP_ComputerIcon",
        "products.png": "SP_DirIcon",
        "service.png": "SP_FileIcon",
        "sales.png": "SP_DialogOkButton",
        "customers.png": "SP_DirHomeIcon",
        "reports.png": "SP_FileDialogInfoView",
        "settings.png": "SP_FileDialogDetailedView",
        "logout.png": "SP_DialogCloseButton",
        "new_sale.png": "SP_DialogOkButton",
        "add_product.png": "SP_FileDialogNewFolder",
        "add.png": "SP_FileDialogNewFolder",
        "categories.png": "SP_DirIcon",
        "edit.png": "SP_FileDialogContentsView",
        "delete.png": "SP_TrashIcon",
        "inventory.png": "SP_DirOpenIcon",
        "orders.png": "SP_FileDialogListView",
        "refresh.png": "SP_BrowserReload",
        "receipt.png": "SP_FileIcon",
        "payment.png": "SP_DialogApplyButton",
        "report.png": "SP_FileDialogInfoView",
        "export.png": "SP_DialogSaveButton",
    }

    sp_name = fallback_names.get(icon_name, "SP_FileIcon")
    sp = getattr(QStyle.StandardPixmap, sp_name, QStyle.StandardPixmap.SP_FileIcon)
    return style.standardIcon(sp)


def uploads_dir() -> Path:
    p = project_root() / "static" / "uploads"
    p.mkdir(parents=True, exist_ok=True)
    return p


def uploads_path(filename: str) -> str:
    if not filename:
        return ""
    return str(uploads_dir() / filename)


def copy_image_to_uploads(source_path: str) -> str:
    if not source_path:
        return ""

    source = Path(source_path)
    if not source.exists():
        return ""

    ext = source.suffix.lower()
    allowed = {".png", ".jpg", ".jpeg", ".gif"}
    if ext not in allowed:
        return ""

    filename = f"{uuid.uuid4().hex}{ext}"
    dest = uploads_dir() / filename
    shutil.copy2(str(source), str(dest))
    return filename


def format_currency(amount) -> str:
    try:
        if amount is None:
            return "$0.00"
        if isinstance(amount, Decimal):
            value = float(amount)
        else:
            value = float(amount)
        return f"${value:,.2f}"
    except Exception:
        return "$0.00"


PH_VAT_RATE = Decimal("0.12")


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def round_money(value) -> Decimal:
    return _to_decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def compute_ph_vat_breakdown(amount, vat_rate: Decimal = PH_VAT_RATE, prices_include_vat: bool = True):
    vat_rate = _to_decimal(vat_rate)
    total = round_money(amount)

    if prices_include_vat:
        divisor = Decimal("1") + vat_rate
        vatable_sales = round_money(total / divisor)
        vat_amount = round_money(total - vatable_sales)
        return vatable_sales, vat_amount, total

    vatable_sales = total
    vat_amount = round_money(vatable_sales * vat_rate)
    total = round_money(vatable_sales + vat_amount)
    return vatable_sales, vat_amount, total
