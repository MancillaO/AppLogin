import os
from .Firebase import Firestore

db = Firestore()

__all__ = ["db"]