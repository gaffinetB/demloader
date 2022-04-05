import argparse
import module


parser = argparse.ArgumentParser(description='Download DEM for given AOI or raster')
parser.add_argument('-aoi', nargs=4, type=float, dest='aoi', help='Provide AOI in WGS84 in order [left, bottom, right, top]')
parser.add_argument('--res', type=int, dest='resolution', help='DEM resolution in meter. Both 30m and 90m are available')
parser.add_argument('--raster', type=str, dest='raster', help='Use extent of raster at target path to download DEM.')
parser.add_argument('--out', type=str, dest='outpath', help='Specify path to save DEM', default="DEM.tif")

args = parser.parse_args()
print(args)
args = vars(args)
print(args)

print(args['aoi'])


if args['raster'] is not None:
    if args['resolution'] is not None:
        prefixes = module.get_prefixes_from_raster(args['raster'], args['resolution'])
    else:
        prefixes = module.get_prefixes_from_raster(args['raster'])

else:
    if args['resolution'] is not None:
        prefixes = module.get_prefixes_from_aoi(args['aoi'], args['resolution'])
    else:
        prefixes = module.get_prefixes_from_aoi(args['aoi'])

print(prefixes)

if args['resolution'] is not None:
    module.download_from_aws(prefixes, args['outpath'], args['resolution'])
else:
    module.download_from_aws(prefixes, args['outpath'])