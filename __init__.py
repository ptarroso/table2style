# -*- coding: utf-8 -*-
"""
/***************************************************************************
 table2style
                                 A QGIS plugin
 Reads an attribute table (usually in dbf format) with pixel value information and attributes and creates a new style for raster display.
                             -------------------
        begin                : 2015-09-18
        copyright            : (C) 2015 by Pedro Tarroso
        email                : ptarroso@cibio.up.pt
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load table2style class from file table2style.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .table2style import table2style
    return table2style(iface)
