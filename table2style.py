# -*- coding: utf-8 -*-
"""
/***************************************************************************
 table2style
                                 A QGIS plugin
 Reads an attribute table (usually in dbf format) with pixel value 
information and attributes and creates a new style for raster display.
                              -------------------
        begin                : 2015-09-18
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Pedro Tarroso
        email                : ptarroso at cibio dot up dot pt
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; version 3.                              *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from builtins import map
from builtins import zip
from builtins import range
from builtins import object
from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.core import QgsRasterShader, QgsColorRampShader, QgsRasterLayer
from qgis.core import QgsProject
from qgis.core import QgsSingleBandPseudoColorRenderer as renderer
from random import randint

# Initialize Qt resources from file resources.py
from . import resources
# Import the code for the dialog
from .table2style_dialog import table2styleDialog
import os.path

def getListFields(lyr):
    """ Returns a list of field names available in the layer"""
    Fields = lyr.fields()
    FNames = [field.name() for field in Fields]
    return(FNames)

def readFieldData(layer, fieldnames):
    """ Reads all fields from layer using the list of field names
        returns a list of lists containig data from fields"""
    allfields = getListFields(layer)
    FIDs = [allfields.index(f) for f in fieldnames]
    
    fData = []
    iter = layer.getFeatures()
    for feature in iter:
        fData.append([feature.attributes()[i] for i in FIDs])
    
    return(fData)

def rndColor(alpha = 255):
    """ Generate a random color and returns a list of RGBA"""
    col = [randint(0, 255),
           randint(0, 255),
           randint(0, 255),
           alpha]
    return(col)

def rndColorRamp(n, alpha=255):
    cRamp = [rndColor(alpha) for x in range(n)]
    return(cRamp)

def createRasterShader(fields, mode = "rgb", scale = "float"):
    shader = QgsRasterShader()
    colRamp = QgsColorRampShader()
    colRamp.setColorRampType(QgsColorRampShader.Interpolated)
    
    ramp = []
    col = QColor()
    
    for line in fields:
        val = float(line[0])
        txt = str(line[1])
       
        if mode == "rgb" or mode == "rnd":
            if scale != "float":
                color = [float(x)/255.0 for x in line[2:6]]
            col.setRgbF(*color)
            
        elif mode == "hsv":
            if scale != "float":
                color = [float(x)/float(y) for x,y in zip(line[2:6], [360, 100, 100, 255])]
            col.setHsvF(*color)
            
        elif mode == "hex":
            col.setNamedColor(str(line[2]))

        ramp.append(QgsColorRampShader.ColorRampItem(val, col, txt))
    
    colRamp.setColorRampItemList(ramp)
    shader.setRasterShaderFunction(colRamp)
    
    return(shader)
    
def intClass(classList):
    uniqueList = list(map(list, set(map(tuple, [x[1:] for x in classList]))))
    uniqueCat = [x[0] for x in uniqueList]
    cat = [[uniqueCat.index(x[0])] + x for x in uniqueList]
    newclass = [[x[0], uniqueCat.index(x[1])] for x in classList]
    return(newclass, cat)

def reclassRaster(raster, classList, dstfile, xBSize=1000, yBSize=1000,
                  band=1):
    """ Generator raster blocks"""
    from osgeo import gdal
    
    provider = raster.dataProvider()
    rasterFile = str(provider.dataSourceUri())
    
    rasterData = gdal.Open(rasterFile)
    bandData = rasterData.GetRasterBand(int(band))
    
    geoTrans = rasterData.GetGeoTransform()
    proj = rasterData.GetProjection()
    dt = bandData.DataType
    
    ncols = rasterData.RasterXSize
    nrows = rasterData.RasterYSize
    nodata = bandData.GetNoDataValue()
    
    driver = gdal.GetDriverByName('GTiff')
    dstRaster = driver.Create(dstfile, ncols, nrows, 1, dt)
    dstRaster.SetGeoTransform(geoTrans)
    dstBand = dstRaster.GetRasterBand(1)
    dstBand.SetNoDataValue(nodata)
    
    # loop  over raster array with blocks
    count = 1
    for y in range(0, nrows, yBSize):
        blockRows = yBSize
        if y + yBSize >= nrows:
            blockRows = nrows - y
        for x in range (0, ncols, xBSize):
            blockCols = xBSize
            if x + xBSize >= ncols:
                blockCols = ncols - x
            
            data = bandData.ReadAsArray(x, y, blockCols, blockRows)
            
            # reclass the data
            if sum(sum(data==nodata)) != data.size:
                for cl in [c for c in classList if c[0] in data]:
                    data[data == cl[0]] = cl[1]
            
            dstBand.WriteArray(data, x, y)
            print(count)
            count += 1
            
    dstRaster.SetProjection(proj)
    dstBand.FlushCache()

    
class table2style(object):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'table2style_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = table2styleDialog(iface)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Table to style')

        if self.iface.pluginToolBar():
            self.toolbar = self.iface.pluginToolBar()
        else:
            self.toolbar = self.iface.addToolBar(u'table2style')
        self.toolbar.setObjectName(u'table2style')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('table2style', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToRasterMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/table2style/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Convert attributes to style'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginRasterMenu(
                self.tr(u'&Table to style'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def getLayerbyName(self, name):
        """ Returns a QGIS layer  found in the TOC by its name """
        layerTree = QgsProject.instance().layerTreeRoot().findLayers()
        allLayers = [lyr.layer() for lyr in layerTree]
        lyrnames = [lyr.name() for lyr in allLayers]
        if str(name) in lyrnames:
            lyr = allLayers[lyrnames.index(name)]
        else:
            raise NameError('Layer not found')
        return(lyr)
            
    def run(self):
        """Run method that performs all the real work"""

        # Update combos
        layerTree = QgsProject.instance().layerTreeRoot().findLayers()
        allLayers = [lyr.layer() for lyr in layerTree]
        rasterLayers = [lyr for lyr in allLayers if lyr.type() == 1]
        rasterNames = [lyr.name() for lyr in rasterLayers]
        vectorLayers = [lyr for lyr in allLayers if lyr.type() == 0]
        tableLayers = [lyr for lyr in vectorLayers if lyr.geometryType() == 4]
        tableNames = [lyr.name() for lyr in tableLayers]

        self.dlg.updateCombo(self.dlg.rasterCombo, rasterNames)
        self.dlg.updateCombo(self.dlg.tableCombo, tableNames)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()


        # See if OK was pressed
        if result:

            d = self.dlg
            table = self.getLayerbyName(d.getTable())
            fields = [str(d.getValue()), d.getDescription()]
            colorMode = d.colorMode
            
            if colorMode != "rnd":
                fields = fields + d.getColors()

            fieldData = readFieldData(table, fields)

            grid = self.getLayerbyName(d.getRaster())

            # If random colors, create a color for each category
            if colorMode == "rnd":
                cat = list(set([x[1] for x in fieldData]))
                colors = rndColorRamp(len(cat))
                fieldData = [x + colors[cat.index(x[1])] for x in fieldData]
                
            # Paint raster
            shader = createRasterShader(fieldData, colorMode, d.getScale)
            render = renderer(grid.dataProvider(), 1, shader)
            grid.setRenderer(render)
            grid.triggerRepaint()
                
            if d.getNewRaster():
                dstFile = d.getNewRasterFile()
                # Reclassify and create a new raster
                newclass, cat = intClass(fieldData)
                newraster = reclassRaster(grid, newclass, dstFile)

                # Add new raster to TOC and display
                baseName = os.path.basename(dstFile)
                newLayer = QgsRasterLayer(dstFile, baseName)
                QgsProject.instance().addMapLayer(newLayer)
                
                # Re-paint the new raster
                shader = createRasterShader(cat, colorMode, d.getScale)
                render = renderer(newLayer.dataProvider(), 1, shader)
                newLayer.setRenderer(render)
                newLayer.triggerRepaint()
