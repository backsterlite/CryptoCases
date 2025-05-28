from bson.codec_options import TypeCodec, TypeRegistry, CodecOptions
from bson import Decimal128
from decimal import Decimal

class Decimal128Codec(TypeCodec):
    @property
    def python_type(self) -> type[Decimal]:
        # Який Python-тип ми хочемо отримувати
        return Decimal

    @property
    def bson_type(self) -> type[Decimal128]:
        # Який BSON-тип ми перетворюємо
        return Decimal128       # Bson-тип, який декодуємо

    def transform_bson(self, value: Decimal128) -> Decimal:
        return value.to_decimal()

    def transform_python(self, value: Decimal) -> Decimal128:
        return Decimal128(value)

# Реєструємо кодек
type_registry = TypeRegistry([Decimal128Codec()])
codec_options = CodecOptions(type_registry=type_registry)