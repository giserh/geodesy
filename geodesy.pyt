import arcpy
import get_area


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Calculate area raster"
        self.description = "Calculate area for Lat/Lon pixels. Outputs a new raster with same extent and pixel size as input raster. Pixel value is pixel area in square meter base on ellipsoid parameters"
        self.canRunInBackground = True

    def getParameterInfo(self):
		# First parameter
		param0 = arcpy.Parameter(
			displayName="Input Raster",
			name="in_raster",
			datatype=["DERasterDataset", "GPRasterDataLayer", "DERasterBand", "GPRasterLayer"],
			parameterType="Required",
			direction="Input")
		param1 = arcpy.Parameter(
			displayName="Output Raster",
			name="out_raster",
			datatype="DERasterDataset",
			parameterType="Required",
			direction="Output")
		param2 = arcpy.Parameter(
			displayName="Maximum Block Size",
			name="max_size",
			datatype="GPLong",
			parameterType="Optional",
			direction="Input",
			#value = 10000,
			category = "Advanced")
		#param0.description = "Spatial reference of input raster must be an (unprojected) geographic coordinate system (eg WGS 1984)"
		#param1.description = "Location of output raster. Output raster will be a 32bit raster, which pixel values represent the area of a pixel in square meter"
		#param2.description = "Maximum block size of tiles for intermediate results. If running into memory issues, value should be reduced."
		
		param2.value = 10000
		params = [param0, param1, param2]
		return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
		"""The source code of the tool."""
		in_raster = parameters[0].valueAsText
		out_raster = parameters[1].valueAsText
		max_size = int(parameters[2].valueAsText)
		
		get_area.get_area(in_raster, out_raster, max_size)
		
		return
