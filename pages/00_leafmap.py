import leafmap
import solara

# external script defines polygons, etc
from fire import *

zoom = solara.reactive(14)
center = solara.reactive((34, -116))

# location of cached COGs
before_url = "https://huggingface.co/datasets/cboettig/solara-data/resolve/main/before.tif"
after_url = "https://huggingface.co/datasets/cboettig/solara-data/resolve/main/after.tif"

# custom polygon appearance
style = {
    "stroke": False,
    "fill": True,
    "fillColor": "#ff6666",
    "fillOpacity": 0.5,
}

class Map(leafmap.Map):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Add what you want below
        self.add_gdf(jtree_fires, "All Fires", )
        self.add_gdf(big, big.FIRE_NAME.item())
        self.split_map(before_url, after_url, 
                       left_label = "NBS before fire",
                       right_label = "NBS after fire")


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
