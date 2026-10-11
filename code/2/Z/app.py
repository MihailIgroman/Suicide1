import sys

from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ProductEntryForm(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Product Entry - Andrii Zelyuk")
        self.setFixedSize(400, 280)

        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText("e.g. Wireless Mouse")

        self.sku_field = QLineEdit()
        self.sku_field.setPlaceholderText("e.g. AB-1234")

        self.quantity_field = QLineEdit()
        self.quantity_field.setPlaceholderText("0 - 10000")
        self.quantity_field.setValidator(QIntValidator(0, 10000, self))

        self.price_field = QLineEdit()
        self.price_field.setPlaceholderText("0.01 - 999999.99")
        self.price_field.setValidator(QDoubleValidator(0.01, 999999.99, 2, self))

        self.total_field = QLineEdit("$0.00")
        self.total_field.setReadOnly(True)

        self.add_button = QPushButton("Add to warehouse")
        self.add_button.setEnabled(False)

        self.reset_button = QPushButton("Reset")

        form_layout = QFormLayout()
        form_layout.addRow("Name:", self.name_field)
        form_layout.addRow("SKU:", self.sku_field)
        form_layout.addRow("Quantity:", self.quantity_field)
        form_layout.addRow("Unit price:", self.price_field)
        form_layout.addRow("Total value:", self.total_field)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

        self.name_field.textChanged.connect(self.on_field_changed)
        self.sku_field.textChanged.connect(self.on_field_changed)
        self.quantity_field.textEdited.connect(self.on_numeric_edited)
        self.price_field.textEdited.connect(self.on_numeric_edited)

        self.add_button.clicked.connect(self.on_add)
        self.reset_button.clicked.connect(self.on_reset)

    def is_name_valid(self):
        text = self.name_field.text().strip()
        if not (3 <= len(text) <= 40):
            return False
        return text.replace(" ", "").isalpha()

    def is_sku_valid(self):
        text = self.sku_field.text().strip()
        if text.count("-") != 1:
            return False
        prefix, suffix = text.split("-")
        return (2 <= len(prefix) <= 3) and prefix.isupper() and prefix.isalpha() and len(suffix) == 4 and suffix.isdigit()

    def is_form_valid(self):
        return (
            self.is_name_valid()
            and self.is_sku_valid()
            and self.quantity_field.hasAcceptableInput()
            and self.price_field.hasAcceptableInput()
        )

    def update_total(self):
        if self.quantity_field.hasAcceptableInput() and self.price_field.hasAcceptableInput():
            try:
                qty = int(self.quantity_field.text())
                price = float(self.price_field.text().replace(",", "."))
                self.total_field.setText(f"${qty * price:.2f}")
                return
            except ValueError:
                pass
        self.total_field.setText("$0.00")

    def on_field_changed(self):
        self.add_button.setEnabled(self.is_form_valid())

    def on_numeric_edited(self):
        self.update_total()
        self.add_button.setEnabled(self.is_form_valid())

    def on_add(self):
        name = self.name_field.text().strip()
        sku = self.sku_field.text().strip()
        qty = self.quantity_field.text().strip()
        total = self.total_field.text()

        print(f"Added: {name} ({sku}) x{qty} = {total}")

        self.on_reset()

    def on_reset(self):
        self.name_field.clear()
        self.sku_field.clear()
        self.quantity_field.clear()
        self.price_field.clear()
        self.total_field.setText("$0.00")
        self.add_button.setEnabled(False)


def main():
    app = QApplication(sys.argv)
    window = ProductEntryForm()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()