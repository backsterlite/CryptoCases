# app/utils/fields.py
from typing import Any
from decimal import Decimal, ROUND_DOWN
from pydantic import FieldSerializationInfo
from beanie.odm.fields import ExpressionField

class SafeDecimalField(ExpressionField):
  
    def __init__(self, *args, **kwargs):
        """_summary_
        """
        self.decimal_places = kwargs.pop("decimal_places", 8)
        super().__init__(*args, **kwargs)

    def serialize(self, value: Decimal, info: FieldSerializationInfo) -> str:
        # Створюємо маску: 0.00000001 для 8 знаків
        precision = Decimal("1." + "0" * self.decimal_places)
        return str(value.quantize(precision, rounding=ROUND_DOWN))

    def parse(self, value: Any) -> Decimal:
        return Decimal(value)
