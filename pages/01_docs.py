import solara


@solara.component
def Page():
    with solara.Column(align="center"):
        markdown = """
        ## A Solara Template for Geospatial Applications
        
        ### Introduction

        **A collection of [Solara](https://github.com/widgetti/solara) web apps for geospatial applications.**

        - Web App: <https://cboettig-solara-test.hf.space>
        - GitHub Source code: <https://github.com/boettiger-lab/solara-test>
        - Docker container: `ghcr.io/boettiger-lab/solara-geospatial:latest`

        This application accesses boundary polygons from the National Parks Service
        and fire polygon data from CalFire to determine the location of all recorded
        fires in Joshua Tree national park.  We select the largest area fire since
        2015 in the database (currently turns out to be Elk Trail Fire) and access
        all Sentinel-2 imagery from the two weeks before and after the fire alarm date.
        From this imagery, we compute the Normalized Burn Severity metric (NBS)
        around the fire polygon before and after the fire (using cloud-native approach
        of `pystac`, `odc.stac`, and dask), and plot this on a leaflet map overlay with
        splitmap and fire polygons. 
        """

        solara.Markdown(markdown)
