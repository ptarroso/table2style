# -*- coding: utf-8 -*-
"""
/***************************************************************************
 table2styleDialog
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
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic, QtCore

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'table2style_dialog_base.ui'))

def fillCombo(combo, strings, match=None):
    combo.clear()
    for string in strings:
        combo.addItem(string)
    if match != None:
        index = combo.findText(match, QtCore.Qt.MatchWildcard)
        if index >= 0:
            combo.setCurrentIndex(index)
                
class table2styleDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(table2styleDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.iface = iface
        self.tableCombo.currentIndexChanged.connect(self.updateFields)
        self.rndColorsCheck.clicked.connect(self.stateRGB)
        self.newrasterCheck.clicked.connect(self.stateNewRaster)
        self.rasterBrowse.clicked.connect(self.browseNewRaster)

    def getRaster(self):
        return(unicode(self.rasterCombo.currentText()))

    def getTable(self):
        return(unicode(self.tableCombo.currentText()))

    def getValue(self):
        return(unicode(self.valueCombo.currentText()))

    def getDescription(self):
        return(unicode(self.descriptionCombo.currentText()))

    def getRandomCol(self):
        return(bool(self.rndColorsCheck.checkState()))

    def getColors(self):
        if self.getRandomCol():
            return(None)
        else:
            red = unicode(self.redCombo.currentText())
            green = unicode(self.greenCombo.currentText())
            blue = unicode(self.blueCombo.currentText())
            alpha = unicode(self.alphaCombo.currentText())
            return([red, green, blue, alpha])

    def getScale(self):
        if self.getRandomCol():
            return(None)
        else:
            if self.scaleByte.isChecked():
                return("byte")
            if self.scaleOne.isChecked():
                return("one")

    def getNewRaster(self):
        return(bool(self.newrasterCheck.checkState()))

    def getNewRasterFile(self):
        return(self.newrasterText.displayText())

    def updateCombo(self, combo, items):
        if len(items) > 0:
            combo.clear()
            for item in items:
                combo.addItem(item)
                
    def updateFields(self):
        table = self.getTable()
        if table == "":
            self.valueCombo.setEnabled(False)
            self.descriptionCombo.setEnabled(False)
        else:
            self.valueCombo.setEnabled(True)
            self.descriptionCombo.setEnabled(True)
            allLayers = self.iface.legendInterface().layers()
            allLyrNames = [lyr.name() for lyr in allLayers]
            if table in allLyrNames:
                lyr = allLayers[allLyrNames.index(table)]
                fields = [f.name() for f in lyr.pendingFields()]
                fillCombo(self.valueCombo, fields, "*value*")
                fillCombo(self.descriptionCombo, fields, "*descr*")
                fillCombo(self.redCombo, fields, "*red*")
                fillCombo(self.greenCombo, fields, "*green*")
                fillCombo(self.blueCombo, fields, "*blue*")
                fillCombo(self.alphaCombo, fields, "*opacity*")


    def stateRGB(self):
        self.redCombo.setEnabled(not self.getRandomCol())
        self.greenCombo.setEnabled(not self.getRandomCol())
        self.blueCombo.setEnabled(not self.getRandomCol())
        self.alphaCombo.setEnabled(not self.getRandomCol())
        self.redLabel.setEnabled(not self.getRandomCol())
        self.greenLabel.setEnabled(not self.getRandomCol())
        self.blueLabel.setEnabled(not self.getRandomCol())
        self.alphaLabel.setEnabled(not self.getRandomCol())
        self.scaleByte.setEnabled(not self.getRandomCol())
        self.scaleOne.setEnabled(not self.getRandomCol())
        self.scaleLabel.setEnabled(not self.getRandomCol())


    def getSugestedDir(self):
        sugesteddir = ""
        allLayers = self.iface.legendInterface().layers()
        allLyrNames = [lyr.name() for lyr in allLayers]
        if self.getRaster() in allLyrNames:
            lyr = allLayers[allLyrNames.index(self.getRaster())]
            sugesteddir = os.path.dirname(lyr.dataProvider().dataSourceUri())
        return(sugesteddir)
    
    def stateNewRaster(self):
        state = self.getNewRaster()
        self.newrasterText.setEnabled(state)
        self.rasterBrowse.setEnabled(state)
        if state:
            sugestion = os.path.join(self.getSugestedDir(),
                                     self.getDescription() + ".tif")
            self.newrasterText.setText(sugestion)
            
    def browseNewRaster(self):
        defaultdir = self.getSugestedDir()
        ext = u'geoTif (*.tif)' # Only tif extension (for now)
        filename = QtGui.QFileDialog.getSaveFileName(self, "Select new raster ", defaultdir, ext)
        if filename != "":
            if (filename[-4:].lower() != ".tif" and
                filename[-5:].lower() != ".tiff" and
                filename != ""):
                filename += ".tif"
            self.newrasterText.clear()
            self.newrasterText.setText(filename)

