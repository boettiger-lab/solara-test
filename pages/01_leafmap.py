import leafmap
import solara
import pystac_client
import planetary_computer
import odc.stac
import geopandas as gpd
import dask.distributed
import matplotlib.pyplot as plt
import rioxarray
from osgeo import gdal
import matplotlib.pyplot as plt

zoom = solara.reactive(8)
center = solara.reactive((34, -114))

nps = gpd.read_file("/vsicurl/https://huggingface.co/datasets/cboettig/biodiversity/resolve/main/data/NPS.gdb")
calfire = gpd.read_file("/vsicurl/https://huggingface.co/datasets/cboettig/biodiversity/resolve/main/data/fire22_1.gdb",  layer = "firep22_1")
jtree = nps[nps.PARKNAME == "Joshua Tree"].to_crs(calfire.crs)
jtree_fires = jtree.overlay(calfire, how="intersection")

recent = jtree_fires[jtree_fires.YEAR_ > "2015"]
big = recent[recent.Shape_Area == recent.Shape_Area.max()].to_crs("EPSG:4326")
datetime = big.ALARM_DATE.item() + "/" + big.CONT_DATE.item()
box = big.buffer(0.01).bounds.to_numpy()[0]  # Fire bbox + buffer  #box = jtree.to_crs("EPSG:4326").bounds.to_numpy()[0] # Park bbox

items = ( # STAC Search for this imagery in space/time window
     pystac_client.Client.
     open("https://planetarycomputer.microsoft.com/api/stac/v1",
          modifier=planetary_computer.sign_inplace).
     search(collections=["sentinel-2-l2a"],
            bbox=box,
            datetime=datetime,
            query={"eo:cloud_cover": {"lt": 10}}).
    item_collection())

# Time to compute:
client = dask.distributed.Client()
sentinel_bands = ["B08", "B12", "SCL"]
# The magic of gdalwarper. Can also resample, reproject, and aggregate on the fly
data = odc.stac.load(items, bands=sentinel_bands,  bbox=box)
swir = data["B12"].astype("float")
nir = data["B08"].astype("float")
# can resample and aggregate in xarray. compute with dask
nbs = (((nir - swir) / (nir + swir)).
      #  resample(time="MS").
      #  median("time", keep_attrs=True).
        compute()
)
nbs.rio.to_raster(raster_path="nbs.tif", driver="COG")



class Map(leafmap.Map):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Add what you want below
        self.add_gdf(jtree_fires)
        self.add_raster("nbs.tif")


@solara.component
def Page():
    with solara.Column(style={"min-width": "500px"}):
        # solara components support reactive variables
        # solara.SliderInt(label="Zoom level", value=zoom, min=1, max=20)
        # using 3rd party widget library require wiring up the events manually
        # using zoom.value and zoom.set
        Map.element(  # type: ignore
            zoom=zoom.value,
            on_zoom=zoom.set,
            center=center.value,
            on_center=center.set,
            scroll_wheel_zoom=True,
            toolbar_ctrl=False,
            data_ctrl=False,
            height="780px",
        )
        solara.Text(f"Zoom: {zoom.value}")
        solara.Text(f"Center: {center.value}")
