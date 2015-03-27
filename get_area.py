import numpy as np
import math
import arcpy
import gc
import os
import glob
import sys
import zipfile
import subprocess

arcpy.env.overwriteOutput = True
#@profile


def get_raster_properties(raster):
    prop = {}

    desc = arcpy.Describe(raster)
    prop["srs"] = desc.spatialReference
    
    # Returns the top or YMax value of the extent.
    r_top = arcpy.GetRasterProperties_management(raster, "TOP")
    prop["top"] = r_top.getOutput(0)
    
    # Returns the left or XMin value of the extent.
    r_left = arcpy.GetRasterProperties_management(raster, "LEFT")
    prop["left"] = r_left.getOutput(0)

    # Returns the right or XMax value of the extent.
    r_right = arcpy.GetRasterProperties_management(raster, "RIGHT")
    prop["right"] = r_right.getOutput(0)

    # Returns the bottom or YMin value of the extent.
    r_bottom = arcpy.GetRasterProperties_management(raster, "BOTTOM")
    prop["bottom"] = r_bottom.getOutput(0)
    
    # Returns the cell size in the x-direction.
    r_cellsizex = arcpy.GetRasterProperties_management(raster, "CELLSIZEX")
    prop["cellsizex"] = r_cellsizex.getOutput(0)

    # Returns the cell size in the y-direction.
    r_cellsizey = arcpy.GetRasterProperties_management(raster, "CELLSIZEY")
    prop["cellsizey"] = r_cellsizey.getOutput(0)

    # Returns the number of columns in the input raster.
    r_col = arcpy.GetRasterProperties_management(raster, "COLUMNCOUNT")
    prop["col"] = r_col.getOutput(0)
    
    # Returns the number of columns in the input raster.
    r_row = arcpy.GetRasterProperties_management(raster, "ROWCOUNT")
    prop["row"] = r_row.getOutput(0)
    
    return prop


def get_area(in_raster, out_raster, max_size=10000):

    arcpy.AddMessage("Getting infos for {0}.".format(in_raster))
    
    prop = get_raster_properties(in_raster)

    arcpy.env.outputCoordinateSystem = prop["srs"]

    out_basename = os.path.basename(out_raster)
    out_dir = os.path.dirname(out_raster)
    os.chdir = out_dir
    

    a = prop["srs"].semiMajorAxis
    b = prop["srs"].semiMinorAxis
    e = math.sqrt(1 - (b/a)**2)


    if prop["srs"].name != prop["srs"].GCS.name:
        arcpy.AddError("Spatial reference system of {0} is not a geographic coordinate system.".format(in_raster))
    elif a == b:
        arcpy.AddError("Spatial reference system of {0} is based on spheroid, not ellipsoid.".format(in_raster))

    else:
        
        d_lat = float(prop["cellsizey"])
        d_lon = float(prop["cellsizex"])

        pi = math.pi

        d_lat = float(prop["cellsizey"])
        d_lon = float(prop["cellsizex"])

        q = d_lon/360
        
        y = float(prop["row"])/ max_size
        x = float(prop["col"])/ max_size

        if math.trunc(y) == y:
            i_range = range(math.trunc(y))
        else:
            i_range = range(math.trunc(y)+1)

        if math.trunc(x) == x:
            j_range = range(math.trunc(x))
        else:
            j_range = range(math.trunc(x)+1)


        arcpy.AddMessage("Calculate area for...")
        l = 0
        for i in i_range:
            
            if i == math.trunc(y):
                row = int(round(((y- math.trunc(y)) * max_size)))
                
            else:
                row = max_size

            miny = float(prop["top"]) - ((max_size * i + row) * d_lon)
            
            for j in j_range:
                
		l += 1
                if j == math.trunc(x):
                    col = int(round((((x- math.trunc(x)) * max_size))))    
                else:
                    col = max_size

                minx = float(prop["left"]) + (max_size * d_lat * j)
            
                ll = arcpy.Point(minx,miny)
                

                lat = np.empty((row, col))
                for k in range(row):
                    lat[k] = (d_lat * (row - k - 1)) + (miny - d_lat/2)

                arcpy.AddMessage("... tile {0}".format(l))
                area = abs((pi * b**2 * ( 2*np.arctanh(e*np.sin(np.radians(lat+d_lat))) / (2*e) + np.sin(np.radians(lat+d_lat)) / ((1 + e*np.sin(np.radians(lat+d_lat)))*(1 - e*np.sin(np.radians(lat+d_lat)))))) -
                        (pi * b**2 * ( 2*np.arctanh(e*np.sin(np.radians(lat))) / (2*e) + np.sin(np.radians(lat)) / ((1 + e*np.sin(np.radians(lat)))*(1 - e*np.sin(np.radians(lat))))))) * q
                
                area_raster = arcpy.NumPyArrayToRaster(area,ll, d_lat, d_lon)
                area_raster.save(r"%s\%s_%i_%i.tif" %(out_dir,out_basename[:-4], i, j))

                
                del lat, area, area_raster
                
                gc.collect()
            
        input_rasters = glob.glob(r"%s\%s_*.tif" % (out_dir, out_basename[:-4]))

        arcpy.AddMessage("Mosaicing tiles.")
        arcpy.MosaicToNewRaster_management (input_rasters, out_dir, out_basename, prop["srs"], "32_BIT_FLOAT", d_lon, 1)

        arcpy.AddMessage("Deleting temporary files.")
        for input_raster in input_rasters:
            arcpy.Delete_management(input_raster)
                                     
        arcpy.AddMessage("Done.")
        gc.collect()


if __name__ == '__main__':

    if len(sys.argv) == 4:
        get_area(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    else:
        print "wrong number of arguments"
