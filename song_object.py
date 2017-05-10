'''

'''

import json
from song_primitives import SongInfo, Label, Chord, Instruction, create_inline


class SongLine(dict):
    ''' The structure contains a series of chords and associated text  '''
    def __init__(self, line_dict=None):
        self['lyric'] = None
        self['chord_dict'] = dict()

        if isinstance(line_dict, dict):
            self['lyric'] = line_dict['lyric']
            for (spacing, chord_components) in line_dict['chord_dict'].items():
                self['chord_dict'][int(spacing)] = \
                    create_inline(chord_components)

    def set_lyric(self, lyric):
        ''' Sets the lyrics '''
        assert(isinstance(lyric, str))
        self['lyric'] = lyric

    def add_inline(self, inline, spacing):
        ''' Appends a chord or instruction to the chord dict '''
        assert(isinstance(inline, Chord) or
               isinstance(inline, Instruction))
        self['chord_dict'][spacing] = inline


class SongElement(dict):
    ''' This is a verse/chorus/bridge/tab etc structure '''
    def __init__(self, element_dict=None):
        self['label'] = None
        self['line_list'] = []

        if isinstance(element_dict, dict):
            if element_dict['label'] is not None:
                self['label'] = Label(element_dict['label'])
            for line_components in element_dict['line_list']:
                self['line_list'].append(SongLine(line_components))

    def set_label(self, label):
        ''' Sets the label '''
        assert(isinstance(label, Label))
        self['label'] = label


class SongSection(dict):
    ''' This is any section of song with a common tempo, key etc. Most of the
    time there will only be one SongSection in a Song.
    '''
    def __init__(self, section_dict=None):
        song_config_file = open("song_config.json")
        song_config = json.load(song_config_file)
        song_config_file.close()

        # for info in song_config['section_info_types']:
        #     self[info] = None
        self['element_list'] = []

        if isinstance(section_dict, dict):
            # super().__init__(**section_dict)
            for (key, info_components) in section_dict.items():
                if key != 'element_list':
                    if info_components is not None:
                        self[key] = SongInfo(info_components)
            for element_components in section_dict['element_list']:
                self['element_list'].append(SongElement(element_components))


class Song(dict):
    ''' The Song object contains all the data for a single song. '''
    def __init__(self, song_dict=None):
        song_config_file = open("song_config.json")
        song_config = json.load(song_config_file)
        song_config_file.close()

        # for single_info in song_config['song_single_info_types']:
        #     self[single_info] = None
        # for multi_info in song_config['song_multi_info_types']:
        #     self[multi_info] = []
        self['section_list'] = []

        self.curr_section = None
        self.curr_element = None
        self.curr_line = None

        if isinstance(song_dict, dict):
            for (key, info_components) in song_dict.items():
                if key != 'section_list':
                    if isinstance(info_components, list):
                        for actual_info_components in info_components:
                            if self.get(key) is None:
                                self[key] = []
                            self[key].append(SongInfo(actual_info_components))
                    elif info_components is not None:
                        self[key] = SongInfo(info_components)
            for section_components in song_dict['section_list']:
                # print(2, section_components)
                self['section_list'].append(SongSection(section_components))

            if self['section_list'] != []:
                self.curr_section = self['section_list'][-1]
                if self.curr_section['element_list'] != []:
                    self.curr_element = self.curr_section['element_list'][-1]
                    if self.curr_element['line_list'] != []:
                        self.curr_line = self.curr_element['line_list'][-1]

    def set_info(self, info):
        ''' Sets the info and inserts into the correct field. Note that some
        info types can have more than one set of data (there can be more than
        one author, for example). In this case the info is appended.
        '''
        assert(isinstance(info, SongInfo))
        song_config_file = open("song_config.json")
        song_config = json.load(song_config_file)
        song_config_file.close()

        info_type = info['info_type']
        if info_type in song_config['song_single_info_types']:
            self[info_type] = info
        elif info_type in song_config['song_multi_info_types']:
            if self.get(info_type) is None:
                self[info_type] = []
            self[info_type].append(info)
        elif info_type in song_config['section_info_types']:
            if self.curr_section is None:
                self.add_section()
            self.curr_section[info_type] = info
        else:
            raise TypeError("Info type '{}' is not a song or section attribute.".format(info_type))

    def add_section(self, section_dict=None):
        ''' Appends an empty section to the section list '''
        self['section_list'].append(SongSection(section_dict))
        self.curr_section = self['section_list'][-1]

    def add_element(self, element_dict=None):
        ''' Appends an empty element to the current section '''
        if self.curr_section is None:
            self.add_section()

        self.curr_section['element_list'].append(SongElement(element_dict))
        self.curr_element = self.curr_section['element_list'][-1]

    def add_line(self, line_dict=None):
        ''' Appends an empty line to the current element '''
        if self.curr_section is None:
            self.add_section()
        if self.curr_element is None:
            self.add_element()

        self.curr_element['line_list'].append(SongLine(line_dict))
        self.curr_line = self.curr_element['line_list'][-1]

    def set_label(self, label):
        ''' Sets the label of the current element '''
        assert(isinstance(label, Label))
        self.curr_element.set_label(label)

    def add_inline(self, inline, spacing):
        ''' Appends a chord or instruction to the chord dict '''
        assert(isinstance(inline, Chord) or
               isinstance(inline, Instruction))
        self.curr_line.add_inline(inline, spacing)

    def set_lyric(self, lyric):
        ''' Sets the lyrics of the current phrase '''
        assert(isinstance(lyric, str))
        self.curr_line.set_lyric(lyric)

    def transpose(self, semitones):
        ''' Transposes the song '''
        pass
        # TODO: Implement


if __name__ == "__main__":
    pass
    # import doctest
    # doctest.testmod(verbose=False)
    # doctest.testfile("unit_tests/song_tests.txt")
