# Table2style

Table2style is a plug-in for QGIS (version >= 2.0; http://www.qgis.org). It reads
data from a table containing pixel values and a correspondent description and
creates a color style and legend for a raster. If the table does not contain RGB
values, random colors are attributed to each class in the description. 

This plugin also exports a the classification to a new raster, where pixels with
values corresponding to the same description are given a new unique value. To the
moment, table2style only exports geotiff rasters. 

## Features

The table2style plug-in allows to:
 
* Add a style to a raster based on a table
* Use RGB values for each class in the table or random colors
* Export the classification to a new raster

## Installation

Download the files to your computer in a folder table2style. Copy this folder to
the plug-in folder of your QGIS instalation. Usually is found in the 
PATH_TO_YOUR_USER/.qgis2/python/plugins/ (check http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/plugins.html for more details). 
In QGIS, activate the table2style in the plug-in manager.

## Usage instructions

Table2style must be activated in the plugin manager. An new icon and a new item 
under Raster menu will be available to initialize the plugin. 

The table2style plugin will look for rasters and tables in the QGIS table of 
contents (TOC), thus, it is necessary to open previously the raster with and the
table. The table can be imported from any supported file in QGIS. For instance, 
if you are using a .dbf, open as a vector layer and if you use a .csv open as a 
delimited text layer without geometry.

Start the plugin and fill the form. It should be pretty straightforward. Sometimes
the RGB may be given in the 0 to 255 scale or in decimals from 0 to 1 - choose the
scale accordingly! 
