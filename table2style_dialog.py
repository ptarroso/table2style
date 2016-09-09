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
        self.setupUi(self)
        self.iface = iface
        self.colorMode = "rgb"
        self.tableCombo.currentIndexChanged.connect(self.updateFields)
        
        self.rgbColorsCheck.setChecked(True)
        
        self.rgbColorsCheck.clicked.connect(self.updateState)
        self.hsvColorsCheck.clicked.connect(self.updateState)
        self.hexColorsCheck.clicked.connect(self.updateState)
        self.rndColorsCheck.clicked.connect(self.updateState)
        
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
        if self.colorMode == "rnd":
            return(None)
        elif self.colorMode == "rgb":
            red = unicode(self.redCombo.currentText())
            green = unicode(self.greenCombo.currentText())
            blue = unicode(self.blueCombo.currentText())
            alpha = unicode(self.alphaCombo.currentText())
            return([red, green, blue, alpha])
        elif self.colorMode == "hsv":
            hue = unicode(self.hueCombo.currentText())
            sat = unicode(self.satCombo.currentText())
            val = unicode(self.valCombo.currentText())
            alpha = unicode(self.alphahsvCombo.currentText())
            return([hue, sat, val, alpha])
        elif self.colorMode == "hex":
            hexcol = unicode(self.hexCombo.currentText())
            return([hexcol])

    def getScale(self):
        if self.colorMode == "rgb" | self.colorMode == "hsv":
            if self.scaleInt.isChecked():
                return("int")
            if self.scaleFloat.isChecked():
                return("float")
        else:
            return("int")

    def getNewRaster(self):
        return(bool(self.newrasterCheck.checkState()))

    def getNewRasterFile(self):
        return(self.newrasterText.displayText())

    def setColorMode(self, mode):
        self.colorMode = mode

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
                fillCombo(self.hueCombo, fields, "*hue*")
                fillCombo(self.satCombo, fields, "*sat*")
                fillCombo(self.valCombo, fields, "*val*")
                fillCombo(self.alphahsvCombo, fields, "*opacity*")
                fillCombo(self.hexCombo, fields, "*hex*")
 
    def updateState(self):
        self.stateRGB()
        self.stateHSV()
        self.stateHEX()
        self.stateRND()
        self.stateScale()
                
    def stateRGB(self):
        state = bool(self.rgbColorsCheck.checkState())
        self.redCombo.setEnabled(state)
        self.greenCombo.setEnabled(state)
        self.blueCombo.setEnabled(state)
        self.alphaCombo.setEnabled(state)
        self.redLabel.setEnabled(state)
        self.greenLabel.setEnabled(state)
        self.blueLabel.setEnabled(state)
        self.alphaLabel.setEnabled(state)
        if state: 
            self.setColorMode("rgb")

    def stateHSV(self):
        state = bool(self.hsvColorsCheck.checkState())
        self.hueCombo.setEnabled(state)
        self.satCombo.setEnabled(state)
        self.valCombo.setEnabled(state)
        self.alphahsvCombo.setEnabled(state)
        self.hueLabel.setEnabled(state)
        self.satLabel.setEnabled(state)
        self.valLabel.setEnabled(state)
        self.alphahsvLabel.setEnabled(state)
        if state: 
            self.setColorMode("hsv")
            
    def stateHEX(self):
        state = bool(self.hexColorsCheck.checkState())    
        self.hexCombo.setEnabled(state)
        self.hexLabel.setEnabled(state)
        if state: 
            self.setColorMode("hex")

    def stateRND(self):
        if bool(self.rndColorsCheck.checkState()):
            self.setColorMode("rnd")
            
    def stateScale(self):
        state = bool(self.rgbColorsCheck.checkState()) | bool(self.hsvColorsCheck.checkState())
        self.scaleByte.setEnabled(state)
        self.scaleOne.setEnabled(state)
        self.scaleLabel.setEnabled(state)
            
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

