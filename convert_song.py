'''

'''

import source_parsers
import format_parsers

import re

HTTP_REGEX = re.compile("^(http|https):\/\/.+$")  # ftp, smtp, tftp, sftp, nntp
PPTX_REGEX = re.compile("^([A-Z]:)?(([\\\/])?[\w|\.-])+\.pptx$", re.IGNORECASE)


def find_source_type(filename):
    ''' Attempt to determine the source type based on the filename '''
    if HTTP_REGEX.fullmatch(filename):
        return 'http'
    elif PPTX_REGEX.fullmatch(filename):
        return 'powerpoint_file'
    return 'unicode_file'

def find_format_type(filename):
    ''' Attempt to determine the format type based on the file extension '''
    return 'plaintext'


class SongConverter(object):
    ''' Object for converting songs from one format to another '''
    def __init__(self):
        self.input_address = None
        self.input_source = None
        self.input_format = None
        self.output_address = None
        self.output_source = None
        self.output_format = None

    def set_input_address(self, input_address):
        ''' Set the address to the input file '''
        self.input_address = input_address

    def set_input_source(self, input_source):
        ''' Set the type of file to convert from '''
        self.input_source = input_source

    def set_input_format(self, input_format):
        ''' Set the format of the file to convert from '''
        self.input_format = input_format

    def set_output_address(self, output_address):
        ''' Set the address to output file '''
        self.output_address = output_address

    def set_output_source(self, output_source):
        ''' Set the type of file to convert to '''
        self.output_source = output_source

    def set_output_format(self, output_format):
        ''' Set the format of the file to convert to '''
        self.output_format = output_format

    def convert(self, input_address=None, output_address=None):
        ''' Performs the conversion '''
        print("\nConverting song file")

        if input_address is not None:
            self.input_address = input_address
        print("Input address: '{}'".format(self.input_address))
        if self.input_source is None:
            self.input_source = find_source_type(self.input_address)
        print("Input source:  '{}'".format(self.input_source))
        if self.input_format is None:
            self.input_format = find_format_type(self.input_format)
        print("Input format:  '{}'".format(self.input_format))

        if output_address is not None:
            self.output_address = output_address
        print("Output address: '{}'".format(self.output_address))
        if self.output_source is None:
            self.output_source = find_source_type(self.output_address)
        print("Output source:  '{}'".format(self.output_source))
        if self.output_format is None:
            self.output_format = find_format_type(self.output_format)
        print("Output format:  '{}'".format(self.output_format))

        input_filehandle = open(self.input_address, 'r')
        song = source_parsers.readers[self.input_source].read(
            input_filehandle,
            format_parsers.decoders[self.input_format]()
        )
        input_filehandle.close()

        output_filehandle = open(self.output_address, 'w')
        source_parsers.writers[self.output_source].write(
            song,
            output_filehandle,
            format_parsers.encoders[self.output_format]())
        output_filehandle.close()


if __name__ == "__main__":
    import doctest
    doctest.testfile("unit_tests/format_tests.txt")
    # converter = SongConverter()
    # converter.convert('example_formats/lifeline_original.txt',
    #                   'example_formats/lifeline_out.txt')
