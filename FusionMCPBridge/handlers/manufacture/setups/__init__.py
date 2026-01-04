# Setup Management Handler Package
# Contains handlers for CAM setup management including core setup operations,
# stock configuration, WCS configuration, and part position management.
#
# This module follows the same patterns as existing `operations/` and `tool_libraries/` modules.

__version__ = "1.0.0"

# Import all setup handlers to ensure they register with the router
from . import setup
from . import stock

# Import wcs and part_position modules
try:
    from . import wcs
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not import wcs module: {e}")

try:
    from . import part_position
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not import part_position module: {e}")

# =============================================================================
# Re-export from setup core module
# =============================================================================
from .setup import (
    # Business logic functions
    list_setups_detailed,
    get_setup_by_id_impl,
    create_setup_impl,
    modify_setup_impl,
    duplicate_setup_impl,
    delete_setup_impl,
    # Setup-Toolpath relationship functions
    get_toolpaths_for_setup_impl,
    find_setup_for_toolpath_impl,
    validate_setup_toolpath_relationship_impl,
    get_setup_toolpath_mapping_impl,
    move_toolpath_to_setup_impl,
    get_toolpath_with_setup_context_impl,
    # HTTP handlers
    handle_list_setups,
    handle_get_setup,
    handle_create_setup,
    handle_modify_setup,
    handle_duplicate_setup,
    handle_delete_setup,
    handle_get_setup_toolpaths,
    handle_find_toolpath_setup,
    handle_validate_setup_toolpath,
    handle_get_setup_toolpath_mapping,
    handle_move_toolpath_to_setup,
    handle_get_toolpath_with_setup_context,
)

# =============================================================================
# Re-export from stock module
# =============================================================================
from .stock import (
    configure_stock,
    validate_stock_configuration,
    configure_automatic_stock,
    configure_geometry_stock,
    configure_box_stock,
    configure_cylinder_stock,
    apply_stock_material,
)

# =============================================================================
# Re-export from WCS module
# =============================================================================
from .wcs import (
    configure_wcs,
    validate_wcs_configuration,
    integrate_model_id_with_wcs,
    validate_orientation_vectors,
)

# =============================================================================
# Re-export from part position module
# =============================================================================
from .part_position import (
    get_part_position_impl,
    set_part_position_impl,
    validate_part_position,
    handle_get_part_position,
    handle_set_part_position,
)

__all__ = [
    # Submodules
    'setup',
    'stock',
    'wcs',
    'part_position',
    # Setup core functions
    'list_setups_detailed',
    'get_setup_by_id_impl',
    'create_setup_impl',
    'modify_setup_impl',
    'duplicate_setup_impl',
    'delete_setup_impl',
    # Setup-Toolpath relationship functions
    'get_toolpaths_for_setup_impl',
    'find_setup_for_toolpath_impl',
    'validate_setup_toolpath_relationship_impl',
    'get_setup_toolpath_mapping_impl',
    'move_toolpath_to_setup_impl',
    'get_toolpath_with_setup_context_impl',
    # Setup HTTP handlers
    'handle_list_setups',
    'handle_get_setup',
    'handle_create_setup',
    'handle_modify_setup',
    'handle_duplicate_setup',
    'handle_delete_setup',
    'handle_get_setup_toolpaths',
    'handle_find_toolpath_setup',
    'handle_validate_setup_toolpath',
    'handle_get_setup_toolpath_mapping',
    'handle_move_toolpath_to_setup',
    'handle_get_toolpath_with_setup_context',
    # Stock functions
    'configure_stock',
    'validate_stock_configuration',
    'configure_automatic_stock',
    'configure_geometry_stock',
    'configure_box_stock',
    'configure_cylinder_stock',
    'apply_stock_material',
    # WCS functions
    'configure_wcs',
    'validate_wcs_configuration',
    'integrate_model_id_with_wcs',
    'validate_orientation_vectors',
    # Part position functions
    'get_part_position_impl',
    'set_part_position_impl',
    'validate_part_position',
    'handle_get_part_position',
    'handle_set_part_position',
]
