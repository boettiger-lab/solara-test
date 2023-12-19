---
title: Solara Template
emoji: 🏃
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
app_port: 8765
---

NOTE: The YAML header above is required for HuggingFace Spaces deployment.  Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

-----

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/boettiger-lab/solara-test)


# Simple Solara demo

This respository demonstrates how we can deploy an interactive map tool from a few lines of python to an app on HuggingFace spaces using Solara. 

[Solara App on HuggingFace](https://huggingface.co/spaces/cboettig/solara-test)

### Overview

This application accesses boundary polygons from the National Parks Service and fire polygon data from CalFire to determine the location of all recorded fires in Joshua Tree national park.  We select the largest area fire since 2015 in the database (currently turns out to be Elk Trail Fire) and access all Sentinel-2 imagery from the two weeks before and after the fire alarm date. From this imagery, we compute the Normalized Burn Severity metric (NBS) around the fire polygon before and after the fire (using cloud-native approach of `pystac`, `odc.stac`, and dask), and plot this on a leaflet map overlay with splitmap and fire polygons. 


### Code

The required code for analysis is in `fire.py`, with solara visualization in `pages/01_leafmap.py`.  (For interactive use, see `solar-app.pynb`)
