'''

'''


import json
import re
from song_primitives import SongInfo, Label, Chord, Instruction, create_inline
from song_object import Song


class Decoder(object):
    ''' Converter from chordpro to the Song object '''

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

        chordline_pattern = "(?P<chordline>(\W*({0}|{1}))+\W*)".format(
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
        single_info_types = song_config['song_single_info_types'] + \
            song_config['section_info_types']
        multi_info_types = song_config['song_multi_info_types']

        info_template = "\s*(?P<info>{0})".format(song_config['info_template'])

        config_str = ""
        for info_type in single_info_types:
            config_str = config_str + info_type + "|"
        for info_type in multi_info_types:
            config_str = config_str + info_type + "[s]?|"
        info_pattern = info_template.format(config_str[:-1])
        return re.compile(info_pattern, re.IGNORECASE)

    def gen_tab_regex(self, song_config=None):
        ''' Generates the tab line regular expression '''
        tab_pattern = "\s*(?P<tab>(\|{0,2}[A-Gb]?\|{0,2}[-x0-9|:]{4,}))"
        return re.compile(tab_pattern)

    def find_line_type(self, text):
        ''' Takes an estimate of the type of line it is  '''
        for (line_type, line_regex) in self.line_regex_dict.items():
            if line_regex.fullmatch(text):
                group_dict = line_regex.fullmatch(text).groupdict()
                return (line_type, group_dict[line_type])
        return ('lyric', text)

    def decode(self, string_to_parse):
        ''' Converter from chordpro to the Song object

        Various behavious of the decoder include:
            - If the input song attempts to redefine a section info variable,
                it creates a new section
        '''
        new_song = Song()
        new_song.add_section()

        started_song = False
        chord_spacings = []
        prev_line_type = 'blank'

        for line_text in string_to_parse.splitlines():
            (curr_line_type, line_match) = \
                self.find_line_type(line_text.strip())

            if curr_line_type == 'info':
                new_song.set_info(SongInfo(line_match))

            elif curr_line_type == 'label':
                if prev_line_type != 'blank':
                    new_song.add_element()
                new_song.set_label(Label(line_match))
                started_song = True

            elif curr_line_type == 'blank':
                if prev_line_type != 'blank':
                    new_song.add_element()

            elif curr_line_type == 'chordline':
                new_song.add_line()
                chord_spacings = [-1]  # -1 so the spacing calc works
                line_text = line_text.replace(
                    '|', '').replace(
                    '/', ' ').replace(
                    '\'', '')
                for inline_text in line_text.split():
                    spacing = line_text.find(inline_text, chord_spacings[-1]+1)
                    inline = create_inline(inline_text)
                    new_song.add_inline(inline, spacing)
                    chord_spacings.append(spacing)

                started_song = True

            elif curr_line_type == 'lyric':
                if not started_song:  # There is likely meta-data here
                    meta_data = {'info_type': None, 'value': None}
                    if new_song['author'] == []:
                        if line_text.startswith('by') or \
                                new_song['title'] is not None:
                            # Assume second line is author
                            meta_data['info_type'] = 'author'
                            meta_data['value'] = line_text[2:].strip()
                            new_song.set_info(SongInfo(meta_data))
                            continue
                    if new_song['title'] is None:
                        # Assume first line is title
                        meta_data['info_type'] = 'title'
                        meta_data['value'] = line_text.strip()
                        new_song.set_info(SongInfo(meta_data))
                        continue
                    if new_song['copyright'] is None:
                        if line_text.startswith('(c)'):
                            meta_data['info_type'] = 'copyright'
                            meta_data['value'] = line_text[3:].strip()
                            new_song.set_info(SongInfo(meta_data))
                            continue
                else:
                    if prev_line_type == 'chordline':
                        new_song.set_lyric(line_text)
                    else:
                        new_song.add_line()  # lyric=line_text
                        new_song.set_lyric(line_text)

            elif curr_line_type == 'tab':
                new_song.add_line()
                started_song = True

            if curr_line_type != 'chordline':
                chord_spacings = []
            prev_line_type = curr_line_type

        return new_song


class Encoder(object):
    ''' Converter from the Song object to chordpro '''

    def encode(self, song_object):
        ''' Converts the song into chordpro '''
        song_config_file = open("song_config.json")
        song_config = json.load(song_config_file)
        song_config_file.close()

        song_string = ""

        for song_info_type in song_config['song_single_info_types']:
            if song_object.get(song_info_type) is not None:
                song_string += "{{{}:{}}}\n".format(
                    song_object[song_info_type]['info_type'],
                    song_object[song_info_type]['value'])

        for song_info_type in song_config['song_multi_info_types']:
            if song_object.get(song_info_type) is not None:
                for song_info in song_object[song_info_type]:
                    song_string += "{{{}:{}}}\n".format(
                        song_info['info_type'],
                        song_info['value'])

        for section in song_object['section_list']:
            for section_info_type in song_config['section_info_types']:
                if section.get(section_info_type) is not None:
                    song_string += "{{{}:{}}}\n".format(
                        section[section_info_type]['info_type'],
                        section[section_info_type]['value'])

            for element in section['element_list']:
                start_of_x_tag = None

                song_string += "\n"
                if element['label'] is not None:
                    curr_label = element['label']
                    song_string += "{{c:{}}}\n".format(element['label'])

                    if not curr_label['pre']:
                        if curr_label['label_type'] == "verse":
                            song_string += "{start_of_verse}\n"
                            start_of_x_tag = "verse"
                        elif curr_label['label_type'] == "chorus":
                            song_string += "{start_of_chorus}\n"
                            start_of_x_tag = "chorus"
                        elif curr_label['label_type'] == "bridge":
                            song_string += "{start_of_bridge}\n"
                            start_of_x_tag = "bridge"

                for line in element['line_list']:
                    line_text = ""
                    if line['chord_dict'] != dict():
                        if line['lyric'] is not None:
                            line_text = line['lyric']

                        if line['chord_dict'] is not None:
                            for (spacing, chord) in reversed(sorted(
                                    line['chord_dict'].items())):
                                pre_chord = line_text[0:spacing]
                                post_chord = line_text[spacing:]
                                line_text = "{}[{}]{}".format(
                                    pre_chord, chord, post_chord)
                        line_text += "\n"
                    song_string += line_text

                if start_of_x_tag == 'verse':
                    song_string += "{end_of_verse}\n"
                elif start_of_x_tag == 'chorus':
                    song_string += "{end_of_chorus}\n"
                elif start_of_x_tag == 'bridge':
                    song_string += "{end_of_bridge}\n"

        return song_string


def decode(string_to_parse):
    ''' Convert from chordpro to the Song object '''
    decoder = Decoder()
    return decoder.decode(string_to_parse)


def encode(song_object):
    ''' Convert from the Song object to chordpro '''
    encoder = Encoder()
    return encoder.encode(song_object)


if __name__ == "__main__":
    print("Unable to run functions from this folder")
