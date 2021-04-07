""" Custom exceptions for Sikuli script """

class FindFailed(Exception):
    """ Exception: Unable to find the searched item """
    def __init__(self, event, reg = None):
        Exception.__init__(self, str(event), reg)

class ImageMissing(Exception):
    """ Exception: Unable to find the image file """
    def __init__(self, event):
        Exception.__init__(self, str(event))
