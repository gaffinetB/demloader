import argparse
import demloader.download as download
import demloader.prefixes as prefixes


parser = argparse.ArgumentParser(description='Download DEM for given AOI or raster')
parser.add_argument('-aoi', nargs=4, type=float, dest='aoi', help='Provide AOI in WGS84 as sequence of four floats. The order needs to be [left, bottom, right, top]')
parser.add_argument('--raster', type=str, dest='raster', help='Path to raster from which the extent of DEM download is extracted. Functions as alternative to providing an AOI explicitely')
parser.add_argument('--res', type=int, dest='resolution', help='(optional) DEM resolution in meter provided as integer. Both 30m and 90m are available. By default 30m', default=30)
parser.add_argument('--out', type=str, dest='outpath', help='(optional) Path at which downloaded DEM is saved. By default \"data/demloader_dem.tif\"', default="data/demloader_dem.tif")

args = parser.parse_args()
args = vars(args)

if args['raster'] is not None:
    prefixes = prefixes.get_from_raster(args['raster'], args['resolution'])
else:
    prefixes = prefixes.get_from_aoi(args['aoi'], args['resolution'])

outpath = download.from_aws(prefixes, args['resolution'], args['outpath'])

print(f"DEM downloaded and saved at {outpath}")
