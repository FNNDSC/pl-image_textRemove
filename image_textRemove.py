#!/usr/bin/env python

from pathlib import Path
from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter
import cv2
import math
import numpy as np
from chris_plugin import chris_plugin, PathMapper
from pflog import pflog

__version__ = '1.0.2'

DISPLAY_TITLE = r"""
       _        _                             _            _  ______                              
      | |      (_)                           | |          | | | ___ \                             
 _ __ | |______ _ _ __ ___   __ _  __ _  ___ | |_ _____  _| |_| |_/ /___ _ __ ___   _____   _____ 
| '_ \| |______| | '_ ` _ \ / _` |/ _` |/ _ \| __/ _ \ \/ / __|    // _ \ '_ ` _ \ / _ \ \ / / _ \
| |_) | |      | | | | | | | (_| | (_| |  __/| ||  __/>  <| |_| |\ \  __/ | | | | | (_) \ V /  __/
| .__/|_|      |_|_| |_| |_|\__,_|\__, |\___| \__\___/_/\_\\__\_| \_\___|_| |_| |_|\___/ \_/ \___|
| |                                __/ |  ______                                                  
|_|                               |___/  |______|                                                 
"""

parser = ArgumentParser(description='A ChRIS plugin to remove text from images',
                        formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument('-V', '--version', action='version',
                    version=f'%(prog)s {__version__}')
parser.add_argument('-f', '--fileFilter', default='png', type=str,
                    help='input file filter(only the extension)')
parser.add_argument('-o', '--outputType', default='png', type=str,
                    help='output file type(only the extension)')
parser.add_argument('-r', '--removeAll', default=False, action="store_true",
                    help='Remove all texts from image using text recognition model')
parser.add_argument(  '--pftelDB',
                    dest        = 'pftelDB',
                    default     = '',
                    type        = str,
                    help        = 'optional pftel server DB path')


# The main function of this *ChRIS* plugin is denoted by this ``@chris_plugin`` "decorator."
# Some metadata about the plugin is specified here. There is more metadata specified in setup.py.
#
# documentation: https://fnndsc.github.io/chris_plugin/chris_plugin.html#chris_plugin
@chris_plugin(
    parser=parser,
    title='Remove text from image',
    category='',  # ref. https://chrisstore.co/plugins
    min_memory_limit='100Mi',  # supported units: Mi, Gi
    min_cpu_limit='1000m',  # millicores, e.g. "1000m" = 1 CPU core
    min_gpu_limit=0  # set min_gpu_limit=1 to enable GPU
)
@pflog.tel_logTime(
            event       = 'image_textRemove',
            log         = 'Remove text from image'
)
def main(options: Namespace, inputdir: Path, outputdir: Path):
    """
    *ChRIS* plugins usually have two positional arguments: an **input directory** containing
    input files and an **output directory** where to write output files. Command-line arguments
    are passed to this main method implicitly when ``main()`` is called below without parameters.

    :param options: non-positional arguments parsed by the parser given to @chris_plugin
    :param inputdir: directory containing (read-only) input files
    :param outputdir: directory where to write output files
    """

    print(DISPLAY_TITLE)

    # Typically it's easier to think of programs as operating on individual files
    # rather than directories. The helper functions provided by a ``PathMapper``
    # object make it easy to discover input files and write to output files inside
    # the given paths.
    #
    # Refer to the documentation for more options, examples, and advanced uses e.g.
    # adding a progress bar and parallelism.
    mapper = PathMapper.file_mapper(inputdir, outputdir, glob=f"**/*.{options.fileFilter}")
    for input_file, output_file in mapper:
        # The code block below is a small and easy example of how to use a ``PathMapper``.
        # It is recommended that you put your functionality in a helper function, so that
        # it is more legible and can be unit tested.

        final_image = inpaint_text(str(input_file), options.removeAll)
        img_rgb = cv2.cvtColor(final_image, cv2.COLOR_BGR2RGB)
        output_file = str(output_file).replace(options.fileFilter, options.outputType)
        print(f"Saving output file as ----->{output_file}<-----\n\n")
        cv2.imwrite(output_file, img_rgb)


def midpoint(x1, y1, x2, y2):
    x_mid = int((x1 + x2) / 2)
    y_mid = int((y1 + y2) / 2)
    return x_mid, y_mid


def inpaint_text(img_path, remove_all):
    # Currently we have hardcoded the box coordinates for
    # first name, last name, MRN and DOB
    box_list = [('name&DoB', [[75.661415, 12.579701],
                           [499.21875, 14.421875],
                           [499.21875, 32.171875],
                           [75.10469, 30.951557]]),
                ('MRN', [[75.43749, 36.60937],
                         [148.65622, 36.60937],
                         [148.65622, 53.249996],
                         [75.43749, 53.249996]])]
    # read image
    print(f"Reading input file from ---->{img_path}<----")
    img = cv2.imread(img_path)

    print("Removing fname, lname, MRN, DoB")
    if remove_all:
        print("Place holder to use keras OCR(WIP)")
        # import keras_ocr
        # pipeline = keras_ocr.pipeline.Pipeline()
        # # generate (word, box) tuples
        # box_list = pipeline.recognize([img])[0]

    mask = np.zeros(img.shape[:2], dtype="uint8")
    for box in box_list:
        x0, y0 = box[1][0]
        x1, y1 = box[1][1]
        x2, y2 = box[1][2]
        x3, y3 = box[1][3]

        x_mid0, y_mid0 = midpoint(x1, y1, x2, y2)
        x_mid1, y_mi1 = midpoint(x0, y0, x3, y3)

        thickness = int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))

        cv2.line(mask, (x_mid0, y_mid0), (x_mid1, y_mi1), 255,
                 thickness)
        img = cv2.inpaint(img, mask, 7, cv2.INPAINT_NS)

    return img


if __name__ == '__main__':
    main()
