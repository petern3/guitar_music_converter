'''

'''


from song_object import Song
import format_parsers.plaintext_parser

import unidecode


class Reader(object):
    ''' Reads a file into the Song object '''
    def __init__(self, decoder=None):
        if decoder is None:
            self.decoder = format_parsers.plaintext_parser.Decoder()
        else:
            self.decoder = decoder

    def read(self, file_handle):
        ''' Reads a file into the Song object '''
        string_to_parse = unidecode.unidecode(file_handle.read())
        # string_to_parse = file_handle.read()
        new_song = self.decoder.decode(string_to_parse)
        return new_song


class Writer(object):
    ''' Writes a file from the Song object '''
    def __init__(self, encoder=None):
        if encoder is None:
            self.encoder = format_parsers.plaintext_parser.Encoder()
        else:
            self.encoder = encoder

    def write(self, song_object, file_handle):
        ''' Writes a file from the Song object '''
        song_string = self.encoder.encode(song_object)
        file_handle.write(song_string)


def read(file_handle, decoder=None):
    ''' Reads a file into the Song object '''
    reader = Reader(decoder)
    return reader.read(file_handle)


def write(song_object, file_handle, encoder=None):
    ''' Writes a file from the Song object '''
    writer = Writer(encoder)
    writer.write(song_object, file_handle)


if __name__ == "__main__":
    print("Unable to run functions from this folder")
