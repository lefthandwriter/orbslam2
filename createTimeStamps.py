'''
Script to create timestamps.txt file for a set of images in a folder.

The format will be matching the mono_tum1.cc, based on the fr1/xyz dataset rgb.txt file available at 
https://vision.in.tum.de/data/datasets/rgbd-dataset/download, 
with the slight modificition of removing the first three lines.

Output Format: 
timestamp filename

Example Output in timestamps.txt file:
1.1 images/001.jpeg
1.2 images/002.jpeg
1.3 images/003.jpeg
1.4 images/004.jpeg

Usage Format:
python createTimeStamps.py <path-to-video-folder> <output-filename.txt>

Example Usage:
run createTimeStamps.py "../../../Desktop/SmartCityAI/SignLocalization/SmartPhone/0/images" "smartphone0times.txt"
run createTimeStamps.py "../../../Desktop/SmartCityAI/SignLocalization/SmartPhone/1/images" "smartphone1times.txt"
run createTimeStamps.py "../../Desktop/SmartCityAI/SignLocalization/GTSV/i285/images" "i285times.txt"
run createTimeStamps.py "../../Desktop/SmartCityAI/SignLocalization/GTSV/i75/images" "i75times.txt"
run createTimeStamps.py "../../Desktop/SmartCityAI/SignLocalization/GTSV/state_route_2/images" "state_route_2times.txt"

Full Dataset: all_gather
run createTimeStamps.py "all_gather/interstate/curve/i75_ramp_1/images" "all_gather/interstate/curve/i75_ramp_1/rgb.txt"
run createTimeStamps.py "all_gather/interstate/curve/i75_ramp_2/images" "all_gather/interstate/curve/i75_ramp_2/rgb.txt"

run createTimeStamps.py "all_gather/interstate/straight/i75_1/images" "all_gather/interstate/straight/i75_1/rgb.txt"
run createTimeStamps.py "all_gather/interstate/straight/i75_2/images" "all_gather/interstate/straight/i75_2/rgb.txt"
run createTimeStamps.py "all_gather/interstate/straight/i75_3/images" "all_gather/interstate/straight/i75_3/rgb.txt"

run createTimeStamps.py "all_gather/non-interstate/straight/northside_dr_nw_1/images" "all_gather/non-interstate/straight/northside_dr_nw_1/rgb.txt"
run createTimeStamps.py "all_gather/non-interstate/straight/northside_dr_nw_2/images" "all_gather/non-interstate/straight/northside_dr_nw_2/rgb.txt"
run createTimeStamps.py "all_gather/non-interstate/straight/northside_dr_nw_3/images" "all_gather/non-interstate/straight/northside_dr_nw_3/rgb.txt"

run createTimeStamps.py "all_gather/non-interstate/curve/northside_i75/images" "all_gather/non-interstate/curve/northside_i75/rgb.txt"
run createTimeStamps.py "all_gather/non-interstate/curve/techwood_10th/images" "all_gather/non-interstate/curve/techwood_10th/rgb.txt"
run createTimeStamps.py "all_gather/non-interstate/curve/west_wesley/images" "all_gather/non-interstate/curve/west_wesley/rgb.txt"



## Custom 3 lines at the top
# yaml: Examples/Dev/smartphone.yaml
# images: ../Desktop/SmartCityAI/SignLocalization/SmartPhone/1/images/
# timestamp filename

# yaml: Examples/Dev/gtsv.yaml
# location: ../Desktop/SmartCityAI/SignLocalization/GTSV/state_route_2
# timestamp filename

# yaml:
# images:
# timestamp filename
'''
import os
import re
import sys


def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(data, key=alphanum_key)

def main(sequence_path, out_file):
    image_list = os.listdir(sequence_path)
    # if ".DS_Store" in image_list:
        # image_list.remove(".DS_Store")
    image_list = sorted_alphanumeric(image_list)
    image_list = [os.path.join("images", f) for f in image_list]
    image_list = [f for f in image_list if f.endswith('jpg') or f.endswith('.png')]

    num_images = len(image_list)
    print("Number of images: ", num_images)

    offset = 10
    fps = 10.0
    timestamps = [i/fps for i in range(offset, num_images+offset, 1)]

    with open(out_file, "w+") as txtf:
        txtf.write("# yaml:")
        txtf.write('\n')
        txtf.write("# images:")
        txtf.write('\n')
        txtf.write("# timestamp filename")
        txtf.write('\n')
        for (tVar, image_name) in zip(timestamps, image_list):
            text_line = "{:0.2f}".format(tVar) + " " + image_name
            # text_line = text_line + " " + image_name
            print(text_line)
            txtf.write(text_line)
            txtf.write('\n')
    print("Created timestamps file!")


if __name__ == '__main__':
    if (len(sys.argv) < 3):
        raise ValueError("Unable to make timestamps file, please insert path to video folder in argument \n \
            Format: python makeTimeStampsFile <path_to_video_folder> <output-filename.txt>");
    else:
        sequence_path = sys.argv[1]
        output_filename = sys.argv[2]
        main(sequence_path, output_filename)
