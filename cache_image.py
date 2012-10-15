"""
Script to download images from url and save it to local 

Usage:
cache_image('http://www.google.com/image1.jpg', '/home/jimit/images/', (128, 128))
"""

import os
import urllib2
import urllib
import StringIO
from PIL import Image

class ImageCacheError(Exception):
    pass

def get_image_format(url):
    extension = os.path.splitext(url)[1][1:]
    return extension.upper()

def get_image_name(url):
    return url.split('/')[-1]

def cache_image(url, path, size):
    """
    Scape an image from the url, and save it to a file on the disk
    after converting it into thumbnail

    Args:
        url - [string] location of the image.
        path - [path] Path 
        size - [tuple `(width, height)`] size of the thumbnail.
    """
    try:
        image = urllib2.urlopen(urllib.quote(url.encode('utf8'), safe="%/:=&?~#+!$,;'@()*[]"))
    except (urllib2.URLError, urllib2.HTTPError) as e:
        # :todo permanent fix: KeyError is being handled as a
        # temporary fix in case of URI being an IRI
        # ie. Internationalized RI in which there are unicode chars.
        # The urllib.quote fails for these
        raise ImageCacheError(e.message)

    try:
        format_ = get_image_format(url)
        #on some machine JPG gives error
        format_ = 'JPEG' if format_ == 'JPG' else format_
        im = StringIO.StringIO(image.read())
        image = Image.open(im)
        image.thumbnail(size, Image.NEAREST)
        path = path + get_image_name(url)
        print path
        if image.size[0] > size[0] or image.size[1] > size[1]:
            background = Image.new('RGBA', size, (255, 255, 255, 0))
            background.paste(image,
                             ((size[0] - image.size[0]) / 2, (size[1] - image.size[1]) / 2))
            background.save(path, format_)
        else:
            image.save(path, format_)
    except IOError:
        pass # handled cannot identify image file error
    except Exception, e:
        raise ImageCacheError(e)


