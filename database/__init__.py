import os
from .MongoDB import MongoDB
from .Firebase import Firestore

# Seleccionar base de datos según variable de entorno
database_type = os.getenv("DATABASE", "MongoDB").lower()

if database_type == "firestore":
    db = Firestore()
elif database_type == "mongodb":
    db = MongoDB()
else:
    raise ValueError(f"Base de datos no soportada: {database_type}")

__all__ = ["db"]