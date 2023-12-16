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
        self.add_gdf(jtree)
        self.add_stac_gui()


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
