'''

'''

import json
from song_primitives import SongInfo, Label, Chord, Instruction


class SongLine(dict):
    ''' The structure contains a series of chords and associated text  '''
    def __init__(self, chord_dict=None, lyric=None):
        if chord_dict is not None:
            for (key, value) in chord_dict.items():
                assert(isinstance(key, int))
                assert(isinstance(value, Chord) or
                       isinstance(value, Instruction))
        if lyric is not None:
            assert(isinstance(chord, str))

        self['chord_dict'] = chord_dict if chord_dict is not None else dict()
        self['lyric'] = lyric

    def add_inline(self, inline, spacing):
        ''' Appends a chord or instruction to the chord dict '''
        assert(isinstance(inline, Chord) or
               isinstance(inline, Instruction))
        self['chord_dict'][spacing] = inline

    def set_lyric(self, lyric):
        ''' Sets the lyrics '''
        assert(isinstance(lyric, str))
        self['lyric'] = lyric


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

###############################################################################
#         if FILENAME_REGEX.fullmatch(input_var):
#             self.parse_file(input_var)
#         elif URL_REGEX.fullmatch(input_var):
#             self.parse_website(input_var)
#         else:
#             self.parse_string(input_var)
#
#
#     def parse_string(self, song_string):
#         ''' Parses the string into the metadata and the song itself '''
#         text_list = song_string.splitlines()
#         line_list = [line_parser.create_line(
#             unidecode.unidecode(text)) for text in text_list]
#
#         new_lines = list()
#
#         if len(line_list) < 2:
#             return line_list
#
#         prev_line = line_parser.BlankLine()
#         for curr_line in line_list:
#
#             print(curr_line)
#
#             keep_line = True
#             if isinstance(prev_line, line_parser.ChordLine):
#                 if isinstance(curr_line, line_parser.LyricLine):
#                     curr_line.set_chords(prev_line)
#                     keep_line = False
#             if isinstance(prev_line, line_parser.BlankLine):
#                 if isinstance(curr_line, line_parser.BlankLine):
#                     keep_line = False
#             if keep_line:
#                 new_lines.append(prev_line)
#
#             prev_line = curr_line
#
#         # Deal with the last line
#         if not isinstance(curr_line, line_parser.BlankLine):
#             new_lines.append(curr_line)
#
#         [print(line) for line in new_lines]
#
#
#     def parse_file(self, song_filename):
#         ''' Extracts the song string from the given file and parses '''
#         pass
#
#     def parse_wesite(self, web_url):
#         ''' Extracts the song string from the given website and parses '''
#         pass
#
# ##############################################################################
#
# def get_lines(text):
#     ''' Splits the text into its lines '''
#     text_list = text.splitlines()
#     line_list = [line_parser.create_line(
#         unidecode.unidecode(text)) for text in text_list]
#     return line_list
#
# def connect_chord_lines(line_list):
#     ''' Finds pairs of chord and lyric lines '''
#     new_lines = list()
#
#     if len(line_list) < 2:
#         return line_list
#
#     prev_line = line_parser.BlankLine()
#     for curr_line in line_list:
#
#         print(curr_line)
#
#         keep_line = True
#         if isinstance(prev_line, line_parser.ChordLine):
#             if isinstance(curr_line, line_parser.LyricLine):
#                 curr_line.set_chords(prev_line)
#                 keep_line = False
#         if isinstance(prev_line, line_parser.BlankLine):
#             if isinstance(curr_line, line_parser.BlankLine):
#                 keep_line = False
#         if keep_line:
#             new_lines.append(prev_line)
#
#         prev_line = curr_line
#
#     # Deal with the last line
#     if not isinstance(curr_line, line_parser.BlankLine):
#         new_lines.append(curr_line)
#
#     return new_lines
#
# def to_chopro(to_format):
#     ''' Formats a text block to the chopro format. Makes many assumptions '''
#     line_list = get_lines(to_format)
#     new_lines = connect_chord_lines(line_list)
#
#     print(new_lines)
#
#     [print(line.__repr__()) for line in new_lines]
#     [print(line) for line in new_lines]
#
#
# to_chopro(test_text_2)


if __name__ == "__main__":
    import doctest
    # doctest.testmod(verbose=False)
    # doctest.testfile("unit_tests/song_tests.txt")
