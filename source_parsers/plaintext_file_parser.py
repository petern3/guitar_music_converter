'''

'''


from song_object import Song
import format_parsers.plaintext_parser

# import unidecode


class Reader(object):
    ''' Reads a file into the Song object '''
    def __init__(self):
        pass

    def read(self, file_handle):
        ''' Reads a file into the Song object '''
        # string_to_parse = unidecode.unidecode(file_handle.read())
        string_to_parse = file_handle.read()
        new_song = format_parsers.plaintext_parser.decode(string_to_parse)
        return new_song


class Writer(object):
    ''' Writes a file from the Song object '''
    def __init__(self):
        pass

    def write(self, song_object, file_handle):
        ''' Writes a file from the Song object '''
        song_string = format_parsers.plaintext_parser.encode(song_object)
        file_handle.write(song_string)


def read(file_handle):
    ''' Reads a file into the Song object '''
    reader = Reader()
    return reader.read(file_handle)


def write(song_object, file_handle):
    ''' Writes a file from the Song object '''
    writer = Writer()
    writer.write(song_object, file_handle)


if __name__ == "__main__":
    print("Unable to run functions from this folder")
