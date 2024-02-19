#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from PIL import Image
from tinyscript import *


__author__    = "Alexandre D'Hondt"
__version__   = "1.4"
__copyright__ = ("A. D'Hondt", 2019)
__license__   = "gpl-3.0"
__examples__  = ["-v -i G test.png"]
__docformat__ = "md"
__doc__ = """
*StegoPIT* allows to apply steganography based on PIT (Pixel Indicator Technique) in order to retrieve hidden data from an image.
"""


BANNER_FONT       = "standard"
BANNER_STYLE      = {'fgcolor': "lolcat"}
SCRIPTNAME_FORMAT = "none"


get2lsb = lambda n: ["00", "01", "10", "11"][n % 4]
parity = lambda i: ts.int2bin(int(i)).count("1") % 2
is_prime = lambda n: all(n % i for i in range(2, int(n**0.5)+1)) and n > 1


class PIT(object):
    """ Base on the following paper:
    https://pdfs.semanticscholar.org/7105/e33b5887ed26c7f470df7fdd0928c636242c.pdf
    """
    def __init__(self, filepath):
        if not os.path.exists(filepath):
            raise ValueError("File does not exist")
        self.__filepath = filepath
        self.__obj = Image.open(filepath)
        logger.debug("Image size: {}x{}".format(*self.__obj.size))

    def __read_len(self):
        pixels = self.__obj.load()
        t = []
        for i in range(3):
            t.append(ts.int2bin(pixels[i, 0][0]))
            t.append(ts.int2bin(pixels[i, 0][1]))
            t.append(ts.int2bin(pixels[i, 0][2]))
        t.pop()  # remove the 9th octet
        self.__rms = ts.bin2int("".join(t))
        logger.debug("RMS:        {}".format(self.__rms))

    def __select_sequence(self, ic=None):
        l = self.__rms
        if (ic is None and l % 2 == 0) or ic == "R":     # if even:  R..
            self.__seq = "R" + ["BG", "GB"][parity(l)]
            logger.debug("N even:     IC=R")
        elif (ic is None and is_prime(l)) or ic == "B":  # if prime: B..
            self.__seq = "B" + ["GR", "RG"][parity(l)]
            logger.debug("N prime:    IC=B")
        else:              # else:     G..
            self.__seq = "G" + ["BR", "RB"][parity(l)]
            logger.debug("N other:    IC=G")
        logger.debug("Channels:   {}".format(self.__seq))

    def extract(self, ic=None):
        # 1. extract length of hidden message from 8B (/8 pixels ?) of first row
        # 2. copy into RMS (Remaining Message Size)
        self.__read_len()
        # 3. start from second row, select indicator channel from RGB channels
        self.__select_sequence(ic)
        # 4. check 2 LSB's of indicator channel from RGB channels
        #    case 00 => next pixel
        #    case 01 => extract 2 LSB's from ch2, RMS -= 2, next pixel
        #    case 10 => extract 2 LSB's from ch1, RMS -= 2, next pixel
        #    case 11 => extract 2 LSB's from ch1 & ch2, RMS -= 4, next pixel
        #    if RMS > 0, goto 4.
        data = ""
        w, h = self.__obj.size
        pixels = self.__obj.load()
        i = w
        ic, c1, c2 = map(lambda x: "RGB".index(x), self.__seq)
        while self.__rms > 0:
            x, y = i % w, i // w
            if y >= h:
                break
            pixel = self.__obj.getpixel((x, y))
            lsb = pixel[ic] % 4
            if lsb == 1:
                data += get2lsb(pixel[c2])
                self.__rms -= 2
            elif lsb == 2:
                data += get2lsb(pixel[c1])
                self.__rms -= 2
            elif lsb == 3:
                data += get2lsb(pixel[c1])
                data += get2lsb(pixel[c2])
                self.__rms -= 4
            i += 1
        self.data = ts.bin2str(data)
        return self

    def hide(self, data):
        bin_data = ts.str2bin(data)
        bin_len = ts.int2bin(len(bin_data))
        return self

    def write(self, filename=None):
        if filename is None:
            filename = os.path.basename(self.__filepath)
            filename, _ = os.path.splitext(filename)
            filename = "{}-secret.txt".format(filename)
        with open(filename, 'wb') as f:
            f.write(b(self.data))
        return self


if __name__ == "__main__":
    parser.add_argument("image", type=ts.file_exists, help="image file path")
    parser.add_argument("-i", "--ic", choices=list("RGB"), help="force IC")
    parser.add_argument("-w", "--write", help="write to a file")
    initialize(noargs_action="demo")
    p = PIT(args.image)
    p.extract(args.ic)
    if args.write:
        p.write(args.write)
    logger.info("Hidden data:\n" + p.data)
    #TODO: implement hiding data (using PIT.hide(data))