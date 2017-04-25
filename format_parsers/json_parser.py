'''

'''


import json
from song_primitives import SongInfo, Label, Chord, Instruction
from song_object import Song, SongSection, SongElement, SongLine


class Decoder(object):
    ''' Converter from json to the Song object '''
    def decode(self, string_to_parse):
        ''' Converter from json to the Song object '''
        song_config_file = open("song_config.json")
        song_config = json.load(song_config_file)
        song_config_file.close()

        song_dict = json.loads(string_to_parse)
        new_song = Song(song_dict)

        return new_song


class Encoder(object):
    ''' Converter from the Song object to json '''
    def encode(self, song_object):
        ''' Converts the song into json '''
        song_string = json.dumps(song_object, indent=2)
        return song_string


def decode(string_to_parse):
    ''' Convert from json to the Song object '''
    decoder = Decoder()
    return decoder.decode(string_to_parse)


def encode(song_object):
    ''' Convert from the Song object to json '''
    encoder = Encoder()
    return encoder.encode(song_object)


if __name__ == "__main__":
    print("Unable to run functions from this folder")
