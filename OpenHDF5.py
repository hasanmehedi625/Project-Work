from osgeo import gdal
import os

## CHANGE THIS TO YOUR FOLDER WITH .h5 FILES
os.chdir('C:/WSU Journey/Weekly Report to Prof. Lee/Black Marble Experiment')
rasterFiles = os.listdir(os.getcwd())

# Filter only .h5 files
rasterFiles = [f for f in rasterFiles if f.endswith('.h5')]

if not rasterFiles:
    print("No H5 files found in folder")
else:
    # Get File Name Prefix
    rasterFilePre = rasterFiles[0][:-3]
    print(rasterFilePre)
    
    fileExtension = "_BBOX.tif"
    
    ## Open HDF file
    hdflayer = gdal.Open(rasterFiles[0], gdal.GA_ReadOnly)
    
    # Open raster layer (first subdataset)
    subhdflayer = hdflayer.GetSubDatasets()[0][0]
    rlayer = gdal.Open(subhdflayer, gdal.GA_ReadOnly)
    
    # Subset the Long Name
    outputName = subhdflayer[92:]
    
    outputNameNoSpace = outputName.strip().replace(" ","_").replace("/","_")
    outputNameFinal = outputNameNoSpace + rasterFilePre + fileExtension
    print(outputNameFinal)
    
    ## CHANGE THIS TO YOUR OUTPUT FOLDER
    outputFolder = "C:/WSU Journey/Weekly Report to Prof. Lee/Black Marble Experiment"
    
    outputRaster = outputFolder + outputNameFinal
    
    # Collect bounding box coordinates
    HorizontalTileNumber = int(rlayer.GetMetadata_Dict()["HorizontalTileNumber"])
    VerticalTileNumber = int(rlayer.GetMetadata_Dict()["VerticalTileNumber"])
        
    WestBoundCoord = (10*HorizontalTileNumber) - 180
    NorthBoundCoord = 90-(10*VerticalTileNumber)
    EastBoundCoord = WestBoundCoord + 10
    SouthBoundCoord = NorthBoundCoord - 10
    
    EPSG = "-a_srs EPSG:4326"
    
    translateOptionText = EPSG+" -a_ullr " + str(WestBoundCoord) + " " + str(NorthBoundCoord) + " " + str(EastBoundCoord) + " " + str(SouthBoundCoord)
    
    translateoptions = gdal.TranslateOptions(gdal.ParseCommandLine(translateOptionText))
    gdal.Translate(outputRaster, rlayer, options=translateoptions)
    
    print(f"Successfully created: {outputRaster}")
    
    # Display image in QGIS
    iface.addRasterLayer(outputRaster, outputNameFinal)
    
    print("Done")