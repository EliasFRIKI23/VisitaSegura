from PySide6.QtWidgets import QTableWidget, QHeaderView, QAbstractItemView
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

_DARK_SELECTION = "rgba(255, 184, 28, 0.32)"
_DARK_HOVER = "rgba(96, 165, 250, 0.22)"
_LIGHT_SELECTION = "rgba(14, 82, 140, 0.16)"
_LIGHT_HOVER = "#f4f7fb"


def configure_modern_table(
    table: QTableWidget,
    *,
    row_height: int = 60,
    header_font_size: int = 11,
) -> None:
    """Configura el comportamiento base para una tabla moderna."""
    header = table.horizontalHeader()
    header.setHighlightSections(False)

    font = QFont()
    font.setPointSize(header_font_size)
    font.setBold(True)
    header.setFont(font)
    header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setSelectionMode(QAbstractItemView.SingleSelection)
    table.setAlternatingRowColors(False)
    table.setShowGrid(False)
    table.verticalHeader().setVisible(False)
    table.setFocusPolicy(Qt.NoFocus)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
    table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

    if row_height > 0:
        table.verticalHeader().setDefaultSectionSize(row_height)


def apply_modern_table_theme(table: QTableWidget, dark_mode: bool = False) -> None:
    """Aplica el esquema visual moderno a la tabla."""
    if dark_mode:
        stylesheet = f"""
            QTableWidget {{
                background-color: #0f172a;
                border: none;
                border-top-left-radius: 18px;
                border-top-right-radius: 18px;
                color: #e2e8f0;
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 16px 18px;
                border-bottom: 1px solid rgba(148, 163, 184, 0.16);
            }}
            QTableWidget::item:selected {{
                background-color: {_DARK_SELECTION};
                color: #0b1120;
            }}
            QTableWidget::item:hover {{
                background-color: {_DARK_HOVER};
            }}
            QHeaderView::section {{
                background-color: #0b1220;
                color: #94a3b8;
                font-weight: 600;
                border: none;
                padding: 16px 18px;
                border-bottom: 1px solid rgba(148, 163, 184, 0.2);
            }}
            QHeaderView::section:first {{
                border-top-left-radius: 18px;
            }}
            QHeaderView::section:last {{
                border-top-right-radius: 18px;
            }}
            QTableCornerButton::section {{
                background-color: #0b1220;
                border: none;
                border-top-left-radius: 18px;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 12px;
                margin: 8px 4px 8px 0;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(148, 163, 184, 0.4);
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(148, 163, 184, 0.6);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """
    else:
        stylesheet = f"""
            QTableWidget {{
                background-color: #ffffff;
                border: none;
                border-top-left-radius: 18px;
                border-top-right-radius: 18px;
                color: #1f2937;
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 16px 18px;
                border-bottom: 1px solid #e2e8f0;
            }}
            QTableWidget::item:selected {{
                background-color: {_LIGHT_SELECTION};
                color: #0b1120;
            }}
            QTableWidget::item:hover {{
                background-color: {_LIGHT_HOVER};
            }}
            QHeaderView::section {{
                background-color: #0b1120;
                color: #e2e8f0;
                font-weight: 600;
                border: none;
                padding: 16px 18px;
                border-bottom: 1px solid rgba(15, 23, 42, 0.12);
            }}
            QHeaderView::section:first {{
                border-top-left-radius: 18px;
            }}
            QHeaderView::section:last {{
                border-top-right-radius: 18px;
            }}
            QTableCornerButton::section {{
                background-color: #0b1120;
                border: none;
                border-top-left-radius: 18px;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 12px;
                margin: 8px 4px 8px 0;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(148, 163, 184, 0.45);
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(148, 163, 184, 0.65);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """

    table.setStyleSheet(stylesheet)
