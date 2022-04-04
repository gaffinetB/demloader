from pathlib import Path
from botocore import UNSIGNED, Config
from pyproj import Proj, transform
from osgeo import gdal

import boto3
import warnings
import rasterio


def get_prefixes_from_aoi():
    pass

def get_prefixes_from_raster(raster_path):
    ds_raster = rasterio.open(str(raster_path))
    epsg = str(ds_raster.read_crs().to_epsg())
    zone_letter = 'N' if epsg[2] == '6' else 'S'

    if epsg[2] == '6':
        zone_letter = 'N'
    elif epsg[2] == '7':
        zone_letter = 'S'
    else:
        zone_letter = None
    bounds = ds_raster.bounds

    inProj = Proj(init='epsg:'+epsg)
    outProj = Proj(init='epsg:4326')

    lower_left = transform(inProj,outProj,bounds.left,bounds.bottom)
    upper_right = transform(inProj,outProj,bounds.right,bounds.top)

    lower_left = lower_left[::-1]
    upper_right = upper_right[::-1]

    if zone_letter == 'S':
        lower_left = list(lower_left)
        upper_right = list(upper_right)
        lower_left_temp = lower_left[0]
        upper_right_temp = upper_right[0]
        lower_left[0] = -(90. - upper_right_temp)
        upper_right[0] = -(90. - lower_left_temp)

    needed_northing = [int(lower_left[0])]
    if (int(lower_left[0]) - int(upper_right[0])) != 0:
        needed_northing.append(int(upper_right[0]))
    
    needed_easting = [int(lower_left[1])]
    if (int(lower_left[1]) - int(upper_right[1])) != 0:
        needed_easting.append(int(upper_right[1]))

    if zone_letter == 'S':
        needed_northing = list(
            range(min(needed_northing)-2, max(needed_northing)+1))
        needed_easting = list(
            range(min(needed_easting)-3, max(needed_easting)-2))
    elif zone_letter == 'N':
        needed_northing = list(
            range(min(needed_northing), max(needed_northing)+1))
        needed_easting = list(
            range(min(needed_easting)-2, max(needed_easting)+1))
    else:
        needed_northing = list(
            range(min(needed_northing), max(needed_northing)+1)
        )
        needed_easting = list(
            range(min(needed_easting), max(needed_easting)+1)
        )

    if needed_northing[0] >= 0:
        n_letter = 'N'
    else:
        n_letter = 'S'
        needed_northing = [abs(nn) for nn in needed_northing]

    if needed_easting[0] >= 0:
        e_letter = 'E'
    else:
        e_letter = 'W'
        needed_easting = [abs(ne) for ne in needed_easting]

    prefixes = []
    for north in needed_northing:
        north_string = str(north).zfill(2)
        for east in needed_easting:
            east_string = str(east).zfill(3)
            pfx = 'Copernicus_DSM_COG_10_' + n_letter + north_string + \
                '_00_' + e_letter + east_string + '_00_DEM'
            prefixes.append(pfx)

    return prefixes

def download_from_aws(prefixes, out_path):
    
    out_path = Path(out_path)
    temp_dir = out_path.parent/'temp'
    temp_dir.mkdir(parents=True, exist_ok=True)

    s3_resource = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
    aws_bucket = s3_resource.Bucket('copernicus-dem-30m')

    # Something VRT?
    vrt_path = temp_dir/'combo.vrt'


    downloaded = []

    for prefix in prefixes:
        objects = aws_bucket.objects.filter(Prefix=prefix)

        if len(list(objects.all())) > 0:
            for obj in objects:
                object_path = temp_dir/f"{prefix}.tif"
                aws_bucket.download_file(obj.key, str(object_path))
                downloaded.append(object_path)

    if len(downloaded) > 1:
        gdal.BuildVRT(str(vrt_path), downloaded)
        gdal.Translate(str(out_path), str(vrt_path))

        [file_to_delete.unlink() for file_to_delete in Path(temp_dir).glob('*')]
        temp_dir.rmdir()

    else:
        warnings.warn("No DEM data found for given prefixes!")

    return out_path