import leafmap
import solara
import solara
import pystac_client
import planetary_computer
import odc.stac
import geopandas as gpd
import dask.distributed
import matplotlib.pyplot as plt

# Stashed public copies of NPS polygons and CalFire polygons


zoom = solara.reactive(2)
center = solara.reactive((20, 0))


class Map(leafmap.Map):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Add what you want below
        nps = gpd.read_file("/vsicurl/https://minio.carlboettiger.info/public-biodiversity/NPS.gdb")
        calfire = gpd.read_file("/vsicurl/https://minio.carlboettiger.info/public-biodiversity/fire22_1.gdb",  layer = "firep22_1")
        jtree = nps[nps.PARKNAME == "Joshua Tree"].to_crs(calfire.crs)
        jtree_fires = jtree.overlay(calfire, how="intersection")
        
        # Extract a polygon if interest.   > 2015 for Sentinel, otherwise we can use LandSat
        recent = jtree_fires[jtree_fires.YEAR_ > "2015"]
        big = recent[recent.Shape_Area == recent.Shape_Area.max()].to_crs("EPSG:4326")
        datetime = big.ALARM_DATE.item() + "/" + big.CONT_DATE.item()
        box = big.buffer(0.005).bounds.to_numpy()[0]  # Fire bbox + buffer
        #box = jtree.to_crs("EPSG:4326").bounds.to_numpy()[0] # Park bbox
        
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
        
        
        # Time to compute:
        
        client = dask.distributed.Client()
        # landsat_bands = ["nir08",  "swir16"]
        sentinel_bands = ["B08", "B12", "SCL"]
        
        # The magic of gdalwarper. Can also resample, reproject, and aggregate on the fly
        data = odc.stac.load(items,
                             bands=sentinel_bands,
                             bbox=box
        )
        
        swir = data["B12"].astype("float")
        nir = data["B08"].astype("float")
        
        # can resample and aggregate in xarray. compute with dask
        nbs = (((nir - swir) / (nir + swir)).
              #  resample(time="MS").
              #  median("time", keep_attrs=True).
                compute()
        )
        nbs.rio.to_raster(raster_path="nbs.tif", driver="COG")

        self.add_gdf(jtree)
        self.add_gdf(big)
        self.add_raster("nbs.tif")
        #self.add_stac_gui()


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
