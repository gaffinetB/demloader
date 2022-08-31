from pathlib import Path
from botocore import UNSIGNED
from botocore.config import Config
from osgeo import gdal
import boto3

def from_aws(prefixes, resolution, out_path='demloader_dem.tif'):
    """
    Download DEM corresponding to provided prefixes and save at provided path.

    Parameters:
    -----------
        prefixes (list):    Prefixes corresponding to the DEM to be downloaded.
                            Run functions from prefixes module to get them.
        resolution (int):   Resolution of DEM is either 30 or 90 (in meters)
        out_path (str):     Destination path for DEM raster to be saved at.
                            (Default: "demloader_dem.tif")
    """
    
    out_path = Path(out_path)
    temp_dir = out_path.parent/'temp'
    temp_dir.mkdir(parents=True, exist_ok=True)

    s3_resource = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
    aws_bucket = s3_resource.Bucket(f'copernicus-dem-{resolution}m')

    vrt_path = temp_dir/'combo.vrt'
    downloaded = []

    print(f"{len(prefixes)} DEM patches found for AOI. Ready for Download.")
    
    for prefix in prefixes:
        object_path = str(temp_dir/f"{prefix}.tif")
        aws_bucket.download_file(f"{prefix}/{prefix}.tif", object_path)
        downloaded.append(str(object_path))

    if len(downloaded) >= 1:
        gdal.BuildVRT(str(vrt_path), downloaded, options=gdal.BuildVRTOptions())
        gdal.Translate(str(out_path), str(vrt_path))

        [file_to_delete.unlink() for file_to_delete in Path(temp_dir).glob('*')]
        temp_dir.rmdir()

    else:
        raise RuntimeError("No DEM data found for given prefixes!")

    return out_path
