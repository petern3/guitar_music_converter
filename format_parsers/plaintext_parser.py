'''

'''


import json
import re
from song_primitives import SongInfo, Label, Chord, Instruction
from song_object import Song


class Decoder(object):
    ''' Converter from plaintext to the Song object '''

    def __init__(self):
        self.gen_regex()

    def gen_regex(self):
        ''' Generates the regular expression dictionary. In general, the regex
        pipeline is:

            template \\
                      }-> pattern -> regex
               types /
        '''
        song_config_file = open("song_config.json")
        song_config = json.load(song_config_file)
        song_config_file.close()

        self.line_regex_dict = {
            'blank': self.gen_blank_regex(song_config),
            'chordline': self.gen_chordline_regex(song_config),
            'label': self.gen_label_regex(song_config),
            'info': self.gen_info_regex(song_config),
            'tab': self.gen_tab_regex(song_config)
        }
        self.inline_regex_dict = {
            'chord': self.gen_chord_regex(song_config),
            'instruction': self.gen_instruction_regex(song_config)
        }

    def gen_blank_regex(self, song_config=None):
        ''' Generates the blank line regular expression '''
        return re.compile("(?P<blank>\s*)")

    def gen_chordline_regex(self, song_config):
        ''' Generates the chord/instruction line regular expression '''

        config_str = ""
        for mod_type in song_config['chord_mod_types']:
            config_str = config_str + mod_type + "|"
        chord_pattern = song_config['chord_template'].format(config_str[:-1])

        config_str = ""
        for instruction_type in song_config['instruction_types']:
            config_str = config_str + instruction_type + "|"
        instruction_pattern = song_config['instruction_template'].format(
            config_str[:-1])

        chordline_pattern = "(?P<chordline>(\s*({0}|{1}))+)".format(
            chord_pattern, instruction_pattern)
        return re.compile(chordline_pattern, re.IGNORECASE)

    def gen_label_regex(self, song_config):
        ''' Generates the label regular expression '''
        temp_1 = song_config['label_template']
        temp_2 = song_config['label_template'].replace(
            "?P<pre>", "").replace(
            "?P<label_type>", "").replace(
            "?P<value>", "")
        label_template = \
            "\s*[\[\<\(]?(?P<label>{0}( ?/ ?(?P<alt>{1}))?)[\]\>\)]?".format(
                temp_1, temp_2)

        config_str = ""
        for label_type in song_config['label_types']:
            config_str = config_str + label_type + "|"
        label_pattern = label_template.format(config_str[:-1])
        return re.compile(label_pattern, re.IGNORECASE)

    def gen_info_regex(self, song_config):
        ''' Generates the info line regular expression '''
        all_info_types = song_config['song_info_types'] + \
            song_config['section_info_types']

        info_template = "\s*(?P<info>{0})".format(song_config['info_template'])

        config_str = ""
        for info_type in all_info_types:
            config_str = config_str + info_type + "|"
        info_pattern = info_template.format(config_str[:-1])
        return re.compile(info_pattern, re.IGNORECASE)

    def gen_tab_regex(self, song_config=None):
        ''' Generates the tab line regular expression '''
        tab_pattern = "\s*(?P<tab>(\|{0,2}[A-Gb]?\|{0,2}[-x0-9|:]{4,}))"
        return re.compile(tab_pattern)

    def gen_chord_regex(self, song_config):
        ''' Generates the chord regular expression '''
        chord_template = "(?P<chord>{0})".format(song_config['chord_template'])

        config_str = ""
        for mod_type in song_config['chord_mod_types']:
            config_str = config_str + mod_type + "|"
        chord_pattern = chord_template.format(config_str[:-1])

        return re.compile(chord_pattern, re.IGNORECASE)

    def gen_instruction_regex(self, song_config):
        ''' Generates the instruction regular expression '''
        instruction_template = \
            "(?P<instruction>{0})".format(song_config['instruction_template'])

        config_str = ""
        for instruction_type in song_config['instruction_types']:
            config_str = config_str + instruction_type + "|"
        instruction_pattern = instruction_template.format(config_str[:-1])

        return re.compile(instruction_pattern, re.IGNORECASE)

    def find_line_type(self, text):
        ''' Takes an estimate of the type of line it is  '''
        for (line_type, line_regex) in self.line_regex_dict.items():
            if line_regex.fullmatch(text):
                group_dict = line_regex.fullmatch(text).groupdict()
                return (line_type, group_dict[line_type])
        return ('lyric', text)

    def find_inline_type(self, text):
        ''' Decides whether text is a chord or instruction  '''
        if self.inline_regex_dict['chord'].fullmatch(text) is not None:
            return "chord"
        if self.inline_regex_dict['instruction'].fullmatch(text) is not None:
            return "instruction"
        else:
            raise TypeError(
                "\"{}\" is not a valid chord or instruction".format(text))

    def decode(self, string_to_parse):
        ''' Converter from plaintext to the Song object

        Various behavious of the decoder include:
            - If the input song attempts to redefine a section info variable,
                it creates a new section
        '''
        new_song = Song()
        new_song.add_section()

        chord_spacings = []
        prev_line_type = 'blank'

        for line_text in string_to_parse.splitlines():
            (curr_line_type, line_match) = \
                self.find_line_type(line_text.strip())

            if curr_line_type == 'info':
                line_info = SongInfo(line_match)
                if line_info['info_type'] in new_song:
                    new_song[line_info['info_type']] = line_info
                elif line_info['info_type'] in new_song.curr_section:
                    if new_song.curr_section[line_info['info_type']] is None:
                        new_song.add_section()
                    new_song.curr_section[line_info['info_type']] = line_info
                else:
                    raise TypeError("\"{}\" is a valid info type, but does not fit in the song or section".format(line_info.info))

            elif curr_line_type == 'label':
                if prev_line_type == 'blank':
                    new_song.set_label(Label(line_match))
                else:
                    new_song.add_element(Label(line_match))

            elif curr_line_type == 'blank':
                if prev_line_type != 'blank':
                    new_song.add_element()

            elif curr_line_type == 'chordline':
                new_song.add_line()
                chord_spacings = [-1]  # -1 so the spacing calc works
                for inline in line_text.split():
                    spacing = line_text.find(inline, chord_spacings[-1]+1)
                    if self.find_inline_type(inline) == 'chord':
                        new_song.add_inline(Chord(inline), spacing)
                    elif self.find_inline_type(inline) == 'instruction':
                        new_song.add_inline(Instruction(inline), spacing)
                    else:
                        raise TypeError("\"{}\" is not a valid chord or instruction".format(inline))
                    chord_spacings.append(spacing)

            elif curr_line_type == 'lyric':
                if prev_line_type == 'chordline':
                    new_song.set_lyric(line_text)
                else:
                    new_song.add_line()  # lyric=line_text
                    new_song.set_lyric(line_text)

            elif curr_line_type == 'tab':
                new_song.add_line()

            if curr_line_type != 'chordline':
                chord_spacings = []
            prev_line_type = curr_line_type

        return new_song


class Encoder(object):
    ''' Converter from the Song object to plaintext '''

    def encode(self, song_object):
        ''' Converts the song into plaintext '''
        song_config_file = open("song_config.json")
        song_config = json.load(song_config_file)
        song_config_file.close()

        song_string = ""

        for song_info_type in song_config['song_info_types']:
            if song_object[song_info_type] is not None:
                song_string += str(song_object[song_info_type]) + "\n"

        for section in song_object['section_list']:
            for section_info_type in song_config['section_info_types']:
                if section[section_info_type] is not None:
                    song_string += str(section[section_info_type]) + "\n"

            for element in section['element_list']:
                song_string += "\n"
                if element['label'] is not None:
                    song_string += str(element['label']) + "\n"

                for line in element['line_list']:
                    chord_line = ""
                    lyric_line = ""
                    if line['chord_dict'] != dict():
                        for (spacing, chord) in \
                                sorted(line['chord_dict'].items()):
                            padding = spacing - len(chord_line)
                            if padding < 0:
                                raise ValueError("{} is not a large enough spacing (minimum {})".format(spacing, len(chord_line)))
                            chord_line += " "*padding + str(chord)
                        chord_line += "\n"
                    if line['lyric'] is not None:
                        lyric_line = line['lyric'] + "\n"
                    song_string += chord_line + lyric_line

        song_string += "\n"
        return song_string


def decode(string_to_parse):
    ''' Convert from plaintext to the Song object '''
    decoder = Decoder()
    return decoder.decode(string_to_parse)


def encode(song_object):
    ''' Convert from the Song object to plaintext '''
    encoder = Encoder()
    return encoder.encode(song_object)


if __name__ == "__main__":
    print("Unable to run functions from this folder")
