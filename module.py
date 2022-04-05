from pathlib import Path
from botocore import UNSIGNED
from botocore.config import Config
from pyproj import Proj, transform
from osgeo import gdal

import math
import boto3
import warnings
import rasterio


def get_prefixes_from_aoi(aoi, resolution=30):

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

def get_prefixes_from_raster(raster_path, resolution=30):
    ds_raster = rasterio.open(str(raster_path))
    epsg = str(ds_raster.read_crs().to_epsg())
    bounds = ds_raster.bounds

    inProj = Proj(init='epsg:'+epsg)
    outProj = Proj(init='epsg:4326')

    lower_left = transform(inProj, outProj, bounds.left, bounds.bottom)
    upper_right = transform(inProj, outProj, bounds.right, bounds.top)

    downloads = get_prefixes_from_aoi(list(lower_left) + list(upper_right), resolution=resolution)
    return downloads

def download_from_aws(prefixes, out_path, resolution=30):
    
    out_path = Path(out_path)
    temp_dir = out_path.parent/'temp'
    temp_dir.mkdir(parents=True, exist_ok=True)

    s3_resource = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
    aws_bucket = s3_resource.Bucket(f'copernicus-dem-{resolution}m')

    # Something VRT?
    vrt_path = temp_dir/'combo.vrt'
    downloaded = []

    for prefix in prefixes:
        objects = aws_bucket.objects.filter(Prefix=prefix)

        if len(list(objects.all())) > 0:
            for obj in objects:
                object_path = temp_dir/f"{prefix}.tif"
                aws_bucket.download_file(obj.key, str(object_path))
                downloaded.append(str(object_path))

    if len(downloaded) >= 1:
        print(vrt_path)
        print(downloaded)
        gdal.BuildVRT(str(vrt_path), downloaded, options=gdal.BuildVRTOptions())
        gdal.Translate(str(out_path), str(vrt_path))

        [file_to_delete.unlink() for file_to_delete in Path(temp_dir).glob('*')]
        temp_dir.rmdir()

    else:
        warnings.warn("No DEM data found for given prefixes!")

    return out_path


if __name__ == '__main__':
    
    prefixes = get_prefixes_from_raster('data/clipped_clean_BinaryFloodMap_20190503.tif')

    print(len(prefixes))
    print(prefixes)

    download_from_aws(prefixes, 'data/merged_DEM.tif')