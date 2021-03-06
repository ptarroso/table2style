# Table2style

Table2style is a plug-in for QGIS (version >= 3.0; http://www.qgis.org). It reads
data from a table containing pixel values and a correspondent description and
creates a color style and legend for a raster. If the table does not contain RGB,
HSV values or Hexadecimal triplets, random colors are attributed to each class in 
the description. 

This plugin also exports a the classification to a new raster, where pixels with
values corresponding to the same description are given a new unique value. To the
moment, table2style only exports geotiff rasters. 

This feature is particularly useful for categorical rasters with an intended 
visualization that is given in accessory file (e.g. [Global ecosystems](http://rmgsc.cr.usgs.gov/ecosystems/)).

## Features

The table2style plug-in allows to:
 
* Add a style to a raster based on a table
* Use RGB,HSV or hexadecimal values for each class in the table or random colors
* RGB and HSV can be either with **integer** values (range 0-255 for RGB channels; 0-360, 
0-100, 0-100 fro Hue, saturation, Value, respectively) or **float** (range between 0 and 1.0)
* Export the classification to a new raster

## Installation

### QGIS plugin manager

The Table to Style is in the QGIS plugin repository. Using the plugin manager inside QGIS, search Table2Style and install.

### Manual install

Download the files to your computer in a folder table2style. Copy this folder to
the plug-in folder of your QGIS instalation. Usually is found in the 
PATH_TO_YOUR_USER/.qgis2/python/plugins/ ([check the QGIS manuals](http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/plugins.html) for more details). 
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


## Example
The Table2Style includes an example dataset located in the QGIS plugins folder (usually some form of *PATH_TO_YOUR_USER/.qgis2/python/plugins/Table2Style*; [see QGIS manuals](http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/plugins.html)). The example has one raster file, **raster.tif**, and one text file, **colortable.txt** with the color information for each pixel value. This file contains RGB, HSV and Hex color codes with different coloring schemes.

1. Open the raster the usual way in QGIS.

2. Open the color table with the [Add Delimited Text Layer Button](http://docs.qgis.org/2.14/en/docs/user_manual/working_with_vector/supported_data.html?highlight=delimited%20text#delimited-text-files). Do not forget to check the "No Geometry" option.

3. Start the table2style plugin, either with the icon in the panel or menu *Raster -> table to style -> Convert attributes to style*. 

4. Choose the raster as the *Raster layer* and the color table as *Attribute table*. The *Pixel Value field* in the example is "value" and the *description field* is "description". If in your data sets there is no description available, you can use the pixel value. 

5. Choose the type of color code (RGB, HSV or Hex) and select the respective fields in the combo boxes. The plugin will try to identify the fields based on the name. Confirm if the fields are ok. The value of the HSV might be incorrect: choose the field "val" instead of "value". Optionally, choose random colors.

6. Check the export the new raster button if you want to save a new raster. This option is useful as it reclassifies the raster to unique values. If you have different pixel values with the same color/description, those will be merge to a single class in the new raster.
