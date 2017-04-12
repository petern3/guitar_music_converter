'''

'''


import json
from song_primitives import SongInfo, Label, Chord, Instruction, create_inline
from song_object import Song, SongSection, SongElement, SongLine


class Decoder(object):
    ''' Converter from json to the Song object '''
    def decode(self, string_to_parse):
        ''' Converter from json to the Song object '''
        song_config_file = open("song_config.json")
        song_config = json.load(song_config_file)
        song_config_file.close()

        new_song = Song()
        song_dict = json.loads(string_to_parse)

        section_list = []
        for section in song_dict['section_list']:

            element_list = []
            for element in section['element_list']:

                line_list = []
                for line in element['line_list']:

                    chord_dict = dict()
                    if line['chord_dict'] != dict():
                        for (spacing, inline_dict) in \
                                line['chord_dict'].items():
                            if inline_dict.get('root') is not None:
                                inline = Chord(inline_dict['root'],
                                               inline_dict['mod'],
                                               inline_dict['bass'])
                            elif inline_dict.get('instruction_type') \
                                    is not None:
                                inline = Instruction(
                                    inline_dict.get('instruction_type'))
                            else:
                                raise TypeError("Unable to parse {}".format(
                                    inline_dict))
                            chord_dict[int(spacing)] = inline

                    line_list.append(SongLine(line['lyric'], chord_dict))

                if element['label'] is None:
                    label = None
                else:
                    label = Label(element['label']['label_type'],
                                  element['label']['pre'],
                                  element['label']['value'],
                                  element['label']['alt'])
                element_list.append(SongElement(label, line_list))

            section_list.append(SongSection(element_list))

            for section_info_type in song_config['section_info_types']:
                if section[section_info_type] is None:
                    section_info = None
                else:
                    section_info = \
                        SongInfo(section[section_info_type]['info_type'],
                                 section[section_info_type]['value'])
                section_list[-1][section_info_type] = section_info

        new_song['section_list'] = section_list
        if new_song['section_list'] != []:
            new_song.curr_section = new_song['section_list'][-1]
            if new_song.curr_section['element_list'] != []:
                new_song.curr_element = \
                    new_song.curr_section['element_list'][-1]
                if new_song.curr_element['line_list'] != []:
                    new_song.curr_line = new_song.curr_element['line_list'][-1]

        for song_info_type in song_config['song_info_types']:
            if song_dict[song_info_type] is None:
                song_info = None
            else:
                song_info = SongInfo(song_dict[song_info_type]['info_type'],
                                     song_dict[song_info_type]['value'])
            new_song[song_info_type] = song_info

        self.curr_section = None
        self.curr_element = None
        self.curr_line = None

        print(song_dict)
        print(new_song)

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
