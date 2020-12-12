# ArtStation Wallpaper Downloader

## About

This script is meant as a quick way to download all pictures from a given artist on ArtStation.

## Using

Run the script using:

`artstation-downloader.py [OPTION/S] ARTIST`

### Options

- -h, --help: Show help message
- -v, --verbose: Verbose output mode
- -d, --destination: Specify the local directory to download images into. Defaults to "~/Pictures/Wallpapers/".
- -l, --minimum-length: Specify the minimum picture length (in pixels)
- -L, --maximum-length: Specify the maximum picture length (in pixels)
- -t, --minimum-height: Specify the minimum picture height (in pixels)
- -T, --maximum-height: Specify the maximum picture height (in pixels)
- -p, --portrait-only: Only download portrait oriented pictures
- -P, --landscape-only: Only download landscape oriented pictures
- -r, --minimum-ratio: Specify the minimum picture ratio (in format '5/4')
- -R, --maximum-ratio: Specify the maximum picture ratio (in format '21/9')

### Examples

- Download all pictures from an artist:  
  `./artstation-downloader.py $ARTIST`

- Download all landscape wallpapers of atleast 1920px x 1080px in size:  
  `./artstation-downloader.py -w 1920 -t 1080 -P $ARTIST`

- Download all images with an aspect ratio between 5/4 and 21/9:  
  `./artstation-downloader.py -r 5/4 -R 21/9 $ARTIST`
