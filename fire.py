
import pystac_client
import planetary_computer
import odc.stac
import geopandas as gpd
import dask.distributed
import matplotlib.pyplot as plt
import rioxarray
from datetime import datetime, timedelta


def stac_search(box, datetime):    
    # STAC Search for this imagery in space/time window
    items = (
        pystac_client.Client.
        open("https://planetarycomputer.microsoft.com/api/stac/v1",
            modifier=planetary_computer.sign_inplace).
        search(collections=["sentinel-2-l2a"],
                bbox=box,
                datetime=datetime,
                query={"eo:cloud_cover": {"lt": 10}}).
        item_collection())
    return items

def compute_nbs(items, box):
    # Time to compute:
    client = dask.distributed.Client()
    # landsat_bands = ["nir08",  "swir16"]
    sentinel_bands = ["B08", "B12", "SCL"] # NIR, SWIR, and Cloud Mask

    # The magic of gdalwarper. Can also resample, reproject, and aggregate on the fly
    data = odc.stac.load(items,
                        bands=sentinel_bands,
                        bbox=box
    )
    # Compute the Normalized Burn Ratio, must be float
    swir = data["B12"].astype("float")
    nir = data["B08"].astype("float")
    # can resample and aggregate in xarray. compute with dask
    nbs = (((nir - swir) / (nir + swir)).
        #  resample(time="MS").
        #  median("time", keep_attrs=True).
            compute()
    )
    return nbs


nps = gpd.read_file("/vsicurl/https://huggingface.co/datasets/cboettig/biodiversity/resolve/main/data/NPS.gdb")
calfire = gpd.read_file("/vsicurl/https://huggingface.co/datasets/cboettig/biodiversity/resolve/main/data/fire22_1.gdb",  layer = "firep22_1")
# fire = gpd.read_file("/vsizip/vsicurl/https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/MTBS_Fire/data/composite_data/burned_area_extent_shapefile/mtbs_perimeter_data.zip"

# extract and reproject the Joshua Tree NP Polygon
jtree = nps[nps.PARKNAME == "Joshua Tree"].to_crs(calfire.crs)

# All Fires in the DB that intersect the Park
jtree_fires = jtree.overlay(calfire, how="intersection")

# Extract a polygon if interest.   > 2015 for Sentinel, otherwise we can use LandSat
recent = jtree_fires[jtree_fires.YEAR_ > "2015"]
big = recent[recent.Shape_Area == recent.Shape_Area.max()].to_crs("EPSG:4326")

# Get bounding box + dates before & after fire for STAC search
box = big.buffer(0.01).bounds.to_numpy()[0]  # Fire bbox + buffer
alarm_date = datetime.strptime(big.ALARM_DATE.item(), "%Y-%m-%dT%H:%M:%S+00:00")  
before_date = alarm_date - timedelta(days=14)
after_date = alarm_date + timedelta(days=14)
search_dates = before_date.strftime("%Y-%m-%d") + "/" + after_date.strftime("%Y-%m-%d")


def run():
     # here we go!
     items = stac_search(box, search_dates)
     nbs = compute_nbs(items, box)

     # write first and last date to tif
     nbs.isel(time=0).rio.to_raster(raster_path="before.tif", driver="COG")
     nbs.isel(time=(nbs.time.size-1)).rio.to_raster(raster_path="after.tif", driver="COG")


if __name__ == "__main__":
    run()

