from slowapi import Limiter
from slowapi.util import get_remote_address

# Єдиний лімітер на всю апліку
limiter = Limiter(key_func=get_remote_address)