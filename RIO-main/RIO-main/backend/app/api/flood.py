"""Flood API — serves REAL HEC-RAS raster outputs to the 3D viewer.

All values originate from the four files in resources/ (EPSG:2271, US survey
feet). Depths/WSE are converted to metres and reprojected to EPSG:4326 for
map alignment. Nothing here is synthetic.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..services.flood import flood_pipeline

router = APIRouter()


@router.get("/meta")
async def flood_meta():
    """Inventory of the four source files + processing state for each.

    This is the single entry point the 3D viewer uses to discover what data
    actually exists on disk (including the broken VRT, which is reported as
    unreadable rather than silently replaced).
    """
    inv = flood_pipeline.inventory()
    states = {}
    for f in inv["files"]:
        name = f["state"]
        if not f.get("readable"):
            states[name] = {
                "label": f["label"], "kind": f["kind"], "available": False,
                "error": f.get("error"), "vrt_metadata": f.get("vrt_metadata"),
            }
            continue
        try:
            states[name] = {**flood_pipeline.process_state(name), "available": True}
        except Exception as e:
            states[name] = {"label": f["label"], "kind": f["kind"],
                            "available": False, "error": str(e)}
    return {
        "data_source": "HEC-RAS 2D model outputs (resources/*.tif, *.vrt)",
        "crs_native": "EPSG:2271 — NAD83 / Pennsylvania North (ftUS), Lambert Conformal Conic",
        "units_native": "US survey feet (horizontal + vertical)",
        "units_served": "metres; geographic coordinates EPSG:4326",
        "raster_dir": inv["raster_dir"],
        "files": inv["files"],
        "states": states,
        "terrain_source": {
            "type": "external DEM (real)",
            "provider": "Terrain Tiles (Terrarium encoding) — AWS Open Data, "
                        "USGS 3DEP / NED + other national DEM sources",
            "url_template": "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png",
            "note": "The four files only cover the ~1% wetted domain. Full-domain "
                    "terrain is draped from this real DEM; in-channel elevations "
                    "are additionally available from the WSE (Min) file.",
        },
    }


@router.get("/state/{state}/image.png")
async def flood_state_image(state: str):
    try:
        path = flood_pipeline.png_path(state)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"unknown state '{state}'")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"source file missing: {e}")
    return FileResponse(str(path), media_type="image/png")


@router.get("/state/{state}/grid")
async def flood_state_grid(state: str):
    try:
        return flood_pipeline.grid_summary(state)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"unknown state '{state}'")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"source file missing: {e}")
