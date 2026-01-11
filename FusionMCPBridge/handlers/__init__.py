# Handler modules for the modular Fusion 360 Add-In system
# This package contains all HTTP request handler modules organized by Fusion 360 workspace categories
# Design workspace handlers have been removed as part of CAD removal

from .system import lifecycle
from . import manufacture  # Import manufacture handlers to register with router

__all__ = [
    'lifecycle',
    'manufacture'
]