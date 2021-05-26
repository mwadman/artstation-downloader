#!/usr/bin/env python

import argparse
import urllib2
import json
import os

# Command line arguments
def get_arguments():
    parser = argparse.ArgumentParser(description="Downloads pictures from ArtStation artist/s")
    parser_group = parser.add_mutually_exclusive_group()

    ## Required arguments
    parser.add_argument("artist", help="The name of the artist")
    ## Optional Arguments (designated with "--" infront)
    ### 'action="store_true"' turns the argument into a boolean, 'True' if set and 'False' if unset. The opposite for "store_false".
    parser.add_argument("-v", "--verbose", help="Verbose output mode", action="store_true")
    ### Sets a default if none is specified
    parser.add_argument("-d", "--destination", help="Local directory to download pictures into. Defaults to ~/Pictures/Wallpapers/", default=(os.path.expanduser('~') + "/Pictures/Wallpapers/"))
    ### 'type=int' specifies the argument needs to be an integer, otherwise this is taken as a string by default
    parser.add_argument("-w", "--minimum-width", help="Specify the minimum picture width (in pixels)", type=int, default=0)
    parser.add_argument("-W", "--maximum-width", help="Specify the maximum picture width (in pixels)", type=int, default=999999)
    parser.add_argument("-t", "--minimum-height", help="Specify the minimum picture height (in pixels)", type=int, default=0)
    parser.add_argument("-T", "--maximum-height", help="Specify the maximum picture height (in pixels)", type=int, default=999999)
    parser.add_argument("-r", "--minimum-ratio", help="Specify the minimum picture ratio (in format '5/4')")
    parser.add_argument("-R", "--maximum-ratio", help="Specify the maximum picture ratio (in format '21/9')")
    ## Mutually exclusive group (can not be used together)
    parser_group.add_argument("-p", "--portrait-only", help="Only download portrait oriented pictures", action="store_true")
    parser_group.add_argument("-P", "--landscape-only", help="Only download landscape oriented pictures", action="store_true")

    # To get the value of an argument, use args.$ARG (i.e. args.foo is the value of the "foo" argument)
    ## If the argument has a hyphen, substitute this for an underscore when referencing
    ## (i.e. args.foo_bar is the value of the --foo-bar argument)
    args = parser.parse_args()

    return args

# Function to form a HTTP request and response. Used within other functions
def get_http(url):
    # Required so that urllib2 doesn't give a "403: Forbidden" error
    user_agent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}

    # Creates a http_request with included headers
    http_request = urllib2.Request(url, headers=user_agent)

    # Sends the above request and creates a variable with the response
    http_response = urllib2.urlopen(http_request)

    return http_response


# Takes the name of the artist and returns a json file with data about all images they have
def get_artist_data(artist):
    print "Getting the artist data..."

    json_artist_data = []
    page = 1

    # Instantiates the total pictures as '50' so that the while loop can start
    total_pictures = 50

    while page <= (total_pictures // 50) + 1:
        # Concatenate base url with the artist name and page number
        artist_data_url = "https://www.artstation.com/users/{}/projects.json?page={}".format(artist, str(page))

        # Gets data from the url and turns it into json
        artist_data_response = get_http(artist_data_url)
        page_json = json.load(artist_data_response)

        # On the first run, get the total amount of pictures the artist has and stop if they have none.
        if page == 1:
            total_pictures = int(page_json["total_count"])
            if total_pictures == 0:
                print "Either the artist has no pictures or (most likely) you've entered an incorrect artist name"
                os._exit(1)

        # Append the pages data to the artist data
        json_artist_data += page_json['data']

        # Output page progress
        ## Divided by 50, as that is the number of pictures that data is stored for per page
        if verbose_mode:
            print "Getting page {}/{} for artist {}".format(str(page), str(total_pictures // 50 + 1), artist)

        page += 1

    return json_artist_data

# Creates the directory the images will be downloaded into
def create_directory(root_path, artist):
    # Concatenate the artist name onto the end of the directory, so that they go under an individual folder
    artist_path = os.path.join(root_path, artist)

    # Create the directory if it doesn't already exist
    if not os.path.exists(artist_path):
        if verbose_mode:
            print "Creating artist directory '{}'.".format(artist_path)
        os.makedirs(artist_path)

    return artist_path

# Takes the artist data and returns the data for all images
def get_image_data(json_artist_data):
    print "Getting the images data..."

    json_all_image_data = []

    # Add data for all images to 'json_all_image_data' variable
    for image in json_artist_data:
        # Concatenate base url with the artist name and page number
        image_data_url = "https://www.artstation.com/projects/{}.json".format(image["hash_id"])

        # Gets data from the url and turns it into json
        if verbose_mode:
            print "Getting image data - {}".format(image_data_url)
        image_data_response = get_http(image_data_url)
        image_json = json.load(image_data_response)

        # Adds the title of the image as a key/value into the asset dictionary
        for asset in image_json["assets"]:
            asset["title"] = image_json["title"]

        # Appends the image data to the artist data
        json_all_image_data += image_json["assets"]

    return json_all_image_data

# Takes the command line arguments and trims the json data to include only matching images
def meet_image_conditions(args, json_all_image_data):
    matching_images = []

    # Calculates the minimum and maximum ratios as a float from the arguments given
    if args.minimum_ratio:
        ratio_minimum_first = args.minimum_ratio.rsplit('/')[0]
        ratio_minimum_second = args.minimum_ratio.rsplit('/')[1]
        ratio_minimum = float(ratio_minimum_first) / float(ratio_minimum_second)
    if args.maximum_ratio:
        ratio_maximum_first = args.maximum_ratio.rsplit('/')[0]
        ratio_maximum_second = args.maximum_ratio.rsplit('/')[1]
        ratio_maximum = float(ratio_maximum_first) / float(ratio_maximum_second)

    # Loop through all assets from the artist
    for asset in json_all_image_data:
        # Only completes checks if the asset is an image
        if asset["has_image"]:
            # Creates variables which are either set to true/false based on whether the image meets requirements
            image_width_match = asset['width'] >= args.minimum_width and asset['width'] <= args.maximum_width
            image_height_match = asset['height'] >= args.minimum_height and asset['height'] <= args.maximum_height

            # Determines image orientation
            if asset['height'] > asset['width']:
                image_orientation = "Portrait"
            elif asset['width'] > asset['height']:
                image_orientation = "Landscape"
            else:
                image_orientation = "Square"

            # Determines if the orientation meets requirements
            orientation_match = False
            if args.portrait_only and image_orientation == "Portrait":
                orientation_match = True
            elif args.landscape_only and image_orientation == "Landscape":
                orientation_match = True
            else:
                orientation_match = True

            # Determines if ratio requirements are met
            ratio_match = True
            if args.minimum_ratio or args.maximum_ratio:
                # Calculates the ratio of the image, factoring in its orientation
                if image_orientation == "Landscape":
                    image_ratio = float(asset['width']) / float(asset['height'])
                elif image_orientation == "Portrait":
                    image_ratio = float(asset['height']) / float(asset['width'])
                elif image_orientation == "Square":
                    image_ratio = 1.0
                else:
                    print "Error encountered when determining an images orientation"
                    os._exit(1)

                # Setting ratio match to False if it doesn't match either requirement
                if args.minimum_ratio and image_ratio < ratio_minimum:
                    ratio_match = False
                if args.maximum_ratio and image_ratio > ratio_maximum:
                    ratio_match = False

            # Append to "json_matching_image_data" if all matches are true.
            if image_width_match and image_height_match and orientation_match and ratio_match:
                matching_images.append((asset['title'], asset['image_url']))

    # Check if the list of matching images is empty
    if not matching_images:
        print "Your arguments didn't match any of the images from the artist, try changing your requirements"
        os._exit(1)
    else:
        return matching_images

# Encode image title as a unicode string and replace slashes in it
def sanitise_title(title):
    utf = title.encode('utf-8')
    sanitised = utf.replace('/', '_')
    return sanitised

# Matching image urls and downloads them as seperate files into the artist directory
def download_images(artist_path, matching_images):
    print "Downloading the images..."

    for image in matching_images:
        title, image_url = image
        # Gets the file extension for each image
        file_name = image_url.rsplit('?')[0].rsplit('/')[-1]
        file_name = '{}-{}'.format(sanitise_title(title), file_name)

        # Concatenates the artists directory with the file name and extension for the file path for each image
        file_path = os.path.join(artist_path, file_name)

        # Don't download if the file already exists
        if os.path.exists(file_path):
            if verbose_mode:
                print "The image {} already exists, skipping.".format(file_path)

        # Get the image via urllib2 then write the data to a file
        else:
            if verbose_mode:
                print "Downloading {} to path {}".format(image_url, file_path)
            image_download = get_http(image_url)
            image_to_write = image_download.read()
            with open(file_path, "wb") as image:
                image.write(image_to_write)

def main():
    args = get_arguments()

    global verbose_mode
    verbose_mode = args.verbose

    json_artist_data = get_artist_data(args.artist)
    artist_path = create_directory(args.destination, args.artist)
    json_all_image_data = get_image_data(json_artist_data)
    matching_images = meet_image_conditions(args, json_all_image_data)

    download_images(artist_path, matching_images)

if __name__ == '__main__':
    main()
