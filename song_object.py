'''

'''

import json
from song_primitives import SongInfo, Label, Chord, Instruction


class SongLine(dict):
    ''' The structure contains a series of chords and associated text  '''
    def __init__(self, lyric=None, chord_dict=None):
        if lyric is not None:
            assert(isinstance(lyric, str))
        if chord_dict is not None:
            for (key, value) in chord_dict.items():
                assert(isinstance(key, int))
                assert(isinstance(value, Chord) or
                       isinstance(value, Instruction))

        self['lyric'] = lyric
        self['chord_dict'] = chord_dict if chord_dict is not None else dict()

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
    def __init__(self, label=None, line_list=None):
        if label is not None:
            assert(isinstance(label, Label))
        if line_list is not None:
            for item in line_list:
                assert(isinstance(item, SongLine))

        self['label'] = label
        self['line_list'] = line_list if line_list is not None else []

    def set_label(self, label):
        ''' Sets the label '''
        assert(isinstance(label, Label))
        self['label'] = label


class SongSection(dict):
    ''' This is any section of song with a common tempo, key etc. Most of the
    time there will only be one SongSection in a Song.
    '''
    def __init__(self, element_list=None):
        if element_list is not None:
            for item in element_list:
                assert(isinstance(item, SongElement))

        song_config_file = open("song_config.json")
        song_config = json.load(song_config_file)
        song_config_file.close()

        for info in song_config['section_info_types']:
            self[info] = None
        self['element_list'] = element_list if element_list is not None else []


class Song(dict):
    ''' The Song object contains all the data for a single song. '''
    def __init__(self):

        song_config_file = open("song_config.json")
        song_config = json.load(song_config_file)
        song_config_file.close()

        for info in song_config['song_info_types']:
            self[info] = None
        self['section_list'] = []

        self.curr_section = None
        self.curr_element = None
        self.curr_line = None

    def add_section(self, *args):
        ''' Appends an empty section to the section list '''
        self['section_list'].append(SongSection(*args))
        self.curr_section = self['section_list'][-1]

    def add_element(self, *args):
        ''' Appends an empty element to the current section '''
        if self.curr_section is None:
            self.add_section()

        self.curr_section['element_list'].append(SongElement(*args))
        self.curr_element = self.curr_section['element_list'][-1]

    def add_line(self, *args):
        ''' Appends an empty line to the current element '''
        if self.curr_section is None:
            self.add_section()
        if self.curr_element is None:
            self.add_element()

        self.curr_element['line_list'].append(SongLine(*args))
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
