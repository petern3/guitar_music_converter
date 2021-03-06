'''

'''

import json
import re


class RegexFinder(dict):
    ''' A generic class for matching regular expressions, and extracting them
    into a key '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        ''' Representation of the object '''
        return "{}({})".format(self.__class__.__name__, repr(dict(self)))

    def find_regex_parts(self, text, regex_template, regex_config=None,
            ignore_case=True):
        ''' Attempts to find matches of 'text' the given regular expression.
        regex_template is the pattern (possibly with a .format spot)
        regex_config is a list of strings to insert into the template.
        '''

        config_str = ""
        if regex_config is not None:
            for config_type in regex_config:
                config_str = config_str + config_type + "|"

        if ignore_case:
            regex_pattern = re.compile(
                regex_template.format(config_str[:-1]), re.IGNORECASE)
        else:
            regex_pattern = re.compile(regex_template.format(config_str[:-1]))

        regex_match = regex_pattern.fullmatch(text)
        if regex_match is None:
            raise TypeError("\"{}\" is not a valid {}".format(
                text, self.__class__.__name__))

        for (key, value) in regex_match.groupdict().items():
            self[key] = value

        self.format_values()

    def format_values(self):
        ''' Converts values to the desired format. If this has not been
        overloaded, then it converts everything half-sensibly '''
        for (key, value) in self.items():
            if isinstance(value, str):
                if value == "":
                    self[key] = None
                elif value.isnumeric():
                    self[key] = int(value)
                else:
                    self[key] = value.lower()
            else:
                self[key] = value


class Instruction(RegexFinder):
    ''' This is any instruction you may apply to a chord (such as 'ring') '''

    def __init__(self, instruction):
        if isinstance(instruction, dict):
            for key in instruction.keys():
                assert key in ('instruction_type')
            super().__init__(**instruction)
        else:
            song_config_file = open("song_config.json")
            song_config = json.load(song_config_file)
            song_config_file.close()

            self.find_regex_parts(instruction,
                song_config['instruction_template'],
                song_config['instruction_types'])

    def __str__(self):
        ''' String representation of the object '''
        text = self['instruction_type'].capitalize()
        return text


class Chord(RegexFinder):
    ''' This is the class for chord objects '''
    def __init__(self, chord):
        if isinstance(chord, dict):
            for key in chord.keys():
                assert key in ('root', 'mod', 'bass')
            super().__init__(**chord)
        else:
            song_config_file = open("song_config.json")
            song_config = json.load(song_config_file)
            song_config_file.close()

            self.find_regex_parts(chord, song_config['chord_template'],
                song_config['chord_mod_types'], ignore_case=False)

    def __str__(self):
        ''' String representation of the object '''
        text = self['root']
        if self['mod'] is not None:
            text += self['mod']
        if self['bass'] is not None:
            text += "/{}".format(self['bass'])
        return text

    def format_values(self):
        ''' Converts values to the desired format '''
        self['root'] = self['root'].capitalize()

        # TODO: Change the mod so that 'sus#' turns into '#' or vice-versa
        if self['mod'] == "":
            self['mod'] = None
        else:
            self['mod'] = self['mod'].lower()

        if self['bass'] is not None:
            self['bass'] = self['bass'].capitalize()

    def transpose(self, semitones):
        ''' Transposes the chord '''
        key_list = ['A',
                    'A#',
                    'B',
                    'C',
                    'C#',
                    'D',
                    'D#',
                    'E',
                    'F',
                    'F#',
                    'G',
                    'G#'
                    ]
        # TODO: Implement


class Label(RegexFinder):
    ''' Contains the data for a label '''

    def __init__(self, label=""):
        if isinstance(label, dict):
            super().__init__(**label)
        else:
            song_config_file = open("song_config.json")
            song_config = json.load(song_config_file)
            song_config_file.close()

            temp_1 = song_config['label_template']
            temp_2 = song_config['label_template'].replace(
                "?P<pre>", "").replace(
                "?P<label_type>", "").replace(
                "?P<value>", "")
            regex_template = "{0}( ?/ ?(?P<alt>{1}))?".format(temp_1, temp_2)

            self.find_regex_parts(label, regex_template,
                song_config['label_types'])

    def __str__(self):
        ''' String representation of the object '''
        text = ""
        if self['pre'] is True:
            text += "PRE-"
        text += self['label_type'].upper()
        if self['value'] is not None:
            text += " {}".format(self['value'])
        if self['alt'] is not None:
            text += " / {}".format(str(self['alt']))
        return text

    def format_values(self):
        ''' Converts values to the desired format '''
        if isinstance(self['pre'], str):
            self['pre'] = (self['pre'].lower() == "pre")
        else:
            self['pre'] = False

        self['label_type'] = self['label_type'].lower()

        if self['value'] == "":
            self['value'] = None
        elif self['value'].isnumeric():
            self['value'] = int(self['value'])
        else:
            self['value'] = self['value'].lower()

        if self['alt'] is not None:
            self['alt'] = Label(self['alt'])


class SongInfo(RegexFinder):
    ''' Contains meta-data for the song '''

    def __init__(self, song_info=""):
        if isinstance(song_info, dict):
            super().__init__(**song_info)
        else:
            song_config_file = open("song_config.json")
            song_config = json.load(song_config_file)
            song_config_file.close()

            self.find_regex_parts(song_info, song_config['info_template'],
                song_config['song_single_info_types'] +
                song_config['song_multi_info_types'] +
                song_config['section_info_types'])

    def __str__(self):
        ''' String representation of the object '''
        text = "{}: {}".format(self['info_type'].capitalize(), self['value'])
        return text

    def format_values(self):
        ''' Converts values to the desired format '''
        self['info_type'] = self['info_type'].lower()

        if isinstance(self['value'], str):
            if self['value'] == "":
                self['value'] = None
            elif self['value'].isnumeric():
                self['value'] = int(self['value'])


def create_inline(text):
    try:
        inline = Chord(text)
        return inline
    except (TypeError, AssertionError) as e:
        pass
    try:
        inline = Instruction(text)
        return inline
    except (TypeError, AssertionError) as e:
        pass
    raise TypeError("\"{}\" is not a valid chord or instruction".format(text))


if __name__ == "__main__":
    import doctest
    # doctest.testmod(verbose=False)
    doctest.testfile("unit_tests/instruction_tests.txt")
    doctest.testfile("unit_tests/chord_tests.txt")
    doctest.testfile("unit_tests/label_tests.txt")
    doctest.testfile("unit_tests/info_tests.txt")
