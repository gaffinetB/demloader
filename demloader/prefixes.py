import math
from click import FileError
import rasterio
from pathlib import Path
from pyproj import Proj, transform

def get_from_aoi(aoi, resolution):

    resolution = str(int(resolution/3))
    left, bottom, right, top = list(aoi)
    downloads = []

    if left * right < 0 and bottom * top > 0:
        northwards = 'N' if bottom > 0 else 'S'
        max_northing = math.floor(top) if northwards == 'N' else -math.floor(bottom)
        min_northing = math.floor(bottom) if northwards == 'N' else -math.floor(top)

        for northing in range(min_northing, max_northing+1):
            eastwards = 'E'
            min_easting, max_easting = 0, math.floor(right)
            for easting in range(min_easting, max_easting+1):
                downloads.append(f'Copernicus_DSM_COG_{resolution}_{northwards}{str(northing).zfill(2)}_00_{eastwards}{str(easting).zfill(3)}_00_DEM')

            eastwards = 'W'
            min_easting, max_easting = 1, -math.floor(left)
            for easting in range(min_easting, max_easting+1):
                downloads.append(f'Copernicus_DSM_COG_{resolution}_{northwards}{str(northing).zfill(2)}_00_{eastwards}{str(easting).zfill(3)}_00_DEM')

    elif bottom * top < 0 and left * right > 0:
        eastwards = 'E' if left > 0 else 'W'
        max_easting = math.floor(right) if eastwards == 'E' else -math.floor(left)
        min_easting = math.floor(left) if eastwards == 'E' else -math.floor(right)

        for easting in range(min_easting, max_easting+1):
            northwards = 'N'
            min_northing, max_northing = 0, math.floor(top)
            for northing in range(min_northing, max_northing+1):
                downloads.append(f'Copernicus_DSM_COG_{resolution}_{northwards}{str(northing).zfill(2)}_00_{eastwards}{str(easting).zfill(3)}_00_DEM')

            northwards = 'S'
            min_northing, max_northing = 1, -math.floor(bottom)
            for northing in range(min_northing, max_northing+1):
                downloads.append(f'Copernicus_DSM_COG_{resolution}_{northwards}{str(northing).zfill(2)}_00_{eastwards}{str(easting).zfill(3)}_00_DEM')

    elif bottom * top < 0 and left * right < 0:
        raise NotImplementedError("Please choose AOI that does not contain both Prime Meridian and Equator simulataneously.")

    else:
        northwards = 'N' if bottom > 0 else 'S'
        max_northing = math.floor(top) if northwards == 'N' else -math.floor(bottom)
        min_northing = math.floor(bottom) if northwards == 'N' else -math.floor(top)

        eastwards = 'E' if left > 0 else 'W'
        max_easting = math.floor(right) if eastwards == 'E' else -math.floor(left)
        min_easting = math.floor(left) if eastwards == 'E' else -math.floor(right)        

        for northing in range(min_northing, max_northing+1):
            for easting in range(min_easting, max_easting+1):
                downloads.append(f'Copernicus_DSM_COG_{resolution}_{northwards}{str(northing).zfill(2)}_00_{eastwards}{str(easting).zfill(3)}_00_DEM')

    return downloads

def get_from_raster(raster_path, resolution):
    if not Path(raster_path).exists():
        raise FileNotFoundError(f'File not found at {str(raster_path)}')
    ds_raster = rasterio.open(str(raster_path))
    if ds_raster is None:
        raise FileError(f'Failed to load raster at {str(raster_path)}')
    epsg = str(ds_raster.read_crs().to_epsg())
    bounds = ds_raster.bounds

    inProj = Proj(init='epsg:'+epsg)
    outProj = Proj(init='epsg:4326')

    lower_left = transform(inProj, outProj, bounds.left, bounds.bottom)
    upper_right = transform(inProj, outProj, bounds.right, bounds.top)

    downloads = get_from_aoi(list(lower_left) + list(upper_right), resolution=resolution)
    return downloads