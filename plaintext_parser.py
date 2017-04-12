'''

'''


import json
import re
from song_primitives import SongInfo, Label, Chord, Instruction
from song_object import Song

import unidecode


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

        # >>> decode("")
        '''
        # song_config_file = open("song_config.json")
        # song_config = json.load(song_config_file)
        # song_config_file.close()

        new_song = Song()
        new_song.add_section()

        chord_spacings = []
        prev_line_type = 'blank'

        for line_text in string_to_parse.splitlines():
            (curr_line_type, line_match) =
                self.find_line_type(line_text.strip())

            print("{0:<10} | {1}".format(curr_line_type, line_match))

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
    def __init__(self):
        self.gen_regex()

    def encode(self, song_to_parse):
        ''' Converts the song into plaintext '''
        pass


# class Inline(object):
#     def __init__(self, text, spacing=0, category="Inline"):
#         self.text = text
#         self.spacing = spacing
#         self.category = category
#         if self.category != "Inline":
#             assert(find_inline_type(self.text) == self.category)
#
#     def __repr__(self):
#         ''' Representation of the object '''
#         return "{}('{}', {})".format(self.category, self.text, self.spacing)
#
#     def get_chopro(self):
#         ''' Returns the ChordPro representation of the object '''
#         return "[{}]".format(self.text)
#
# class Instruction(Inline):
#     def __init__(self, text, spacing=0):
#         super().__init__(text, spacing, "Instruction")
#
#     def get_plaintext(self):
#         ''' Returns the plain text representation of the object '''
#         return "({})".format(self.text)
#
#
# class Chord(Inline):
#     def __init__(self, text, spacing=0):
#         super().__init__(text, spacing, "Chord")
#         self.find_chord_parts()
#
#     def find_chord_parts(self):
#         ''' Extracts the chord parts '''
#         group_dict = CHORD_REGEX.fullmatch(self.text).groupdict()
#         self.root = group_dict['root']
#         self.mod = group_dict['mod']
#         self.bass = group_dict['bass']
#
#     def transpose(self, semitones):
#         ''' Transposes the chord '''
#         pass
#
#     def get_plaintext(self):
#         ''' Returns the plain text representation of the object '''
#         # TODO: Extract from root, mod and bass
#         return "{}".format(self.text)
#
#
# class Line(object):
#     ''' Contains a line of a song '''
#     def __init__(self, text="", category=""):
#         self.text = text.rstrip()
#         self.category = category  # find_line_type(self.text)
#         if self.category != "":
#             assert(find_line_type(self.text) == self.category)
#
#     def __repr__(self):
#         ''' Representation of the object '''
#         return "{}Line('{}')".format(self.category, self.text)
#
#     def get_chopro(self):
#         ''' Placeholder for when is cast into a specific line '''
#         return self.text
#
#
# class BlankLine(Line):
#     def __init__(self, text=""):
#         super().__init__(text, BLANK)
#
#     def __repr__(self):
#         ''' Representation of the object '''
#         return "{}Line()".format(self.category)
#
#     def get_chopro(self):
#         ''' Returns the ChordPro representation of the object '''
#         return self.get_plaintext()
#
#     def get_plaintext(self):
#         ''' Returns the plain text representation of the object '''
#         return ""
#
#
# class ChordLine(Line):
#     def __init__(self, text):
#         super().__init__(text, CHORD)
#         self.find_chords()
#
#     def find_chords(self):
#         ''' Extracts the chords '''
#         line_list = self.text.split(" ")
#
#         chord_list = []
#         count = 0
#         count_latched = 0
#         inline_word = ""
#         for char in self.text + " ":
#             if char != " ":
#                 if inline_word == "":  # Just started a word
#                     count_latched = count
#                 inline_word += char
#             else:
#                 if inline_word != "":  # Just ended a word
#                     # Now process the inline word
#                     chord = CHORD_REGEX.fullmatch(inline_word)
#                     instruction = INSTRUCTION_REGEX.fullmatch(inline_word)
#
#                     if chord is not None:
#                         chord_list.append(
#                             Chord(chord.groupdict()["chord"], count_latched))
#                     elif instruction is not None:
#                         chord_list.append(Instruction(
#                             instruction.groupdict()[
#                             "instruction"].lower(), count))
#                     inline_word = ""
#             count += 1
#
#         self.chord_list = chord_list
#
#     def get_chopro(self):
#         ''' Returns the ChordPro representation of the object '''
#         return self.text  # TODO: Convert this to processed version
#
#     def get_plaintext(self):
#         ''' Returns the plain text representation of the object '''
#         return self.text  # TODO: Convert this to processed version
#
#
# class LyricLine(Line):
#     def __init__(self, text, chords=None):
#         super().__init__(text, LYRIC)
#         self.chords = chords
#
#     def __repr__(self):
#         ''' Representation of the object '''
#         return "{}Line('{}', {})".format(self.category, self.text,
#             repr(self.chords))
#
#     def set_chords(self, chords):
#         ''' Sets the chords associated with the lyrics '''
#         assert(isinstance(chords, ChordLine))
#         self.chords = chords
#
#     def get_chopro(self):
#         ''' Returns the ChordPro representation of the object '''
#         ### TODO: Maybe switch this with get_plaintext (and in other Lines)?
#         new_text = self.text
#         if self.chords is not None:
#             for chord in reversed(self.chords.chord_list):
#                 pre_chord = new_text[0:chord.spacing]
#                 post_chord = new_text[chord.spacing:]
#                 new_text = pre_chord + str(chord) + post_chord
#
#         return new_text
#
#     def get_plaintext(self):
#         ''' Returns the plain text representation of the object '''
#         ### TODO: Actually write this function
#         new_text = self.text
#         if self.chords is not None:
#             for chord in reversed(self.chords.chord_list):
#                 pre_chord = new_text[0:chord.spacing]
#                 post_chord = new_text[chord.spacing:]
#                 new_text = pre_chord + str(chord) + post_chord
#
#         return new_text
#
#
# class LabelLine(Line):
#     def __init__(self, text):
#         super().__init__(text, LABEL)
#         self.find_label()
#
#     def __repr__(self):
#         ''' Representation of the object '''
#         return "{}Line('{} {}')".format(self.category, self.label,
#             self.value)
#
#     def find_label(self):
#         ''' Extracts the label type '''
#         group_dict =
#             LINE_TYPES[self.category].fullmatch(self.text).groupdict()
#
#         ## Get Label Type
#         if group_dict["pre"] is not None:
#             self.label = "PRE-" + group_dict["label"].upper()
#         else:
#             self.label = group_dict["label"].upper()
#         ## Get Value
#         if group_dict["value"].isdigit():
#             self.value = int(group_dict["value"])
#         elif group_dict["value"] == "":
#             self.value = None
#         else:
#             self.value = group_dict["value"]
#
#     def get_chopro(self):
#         ''' Returns the ChordPro representation of the object '''
#         if self.value==None:
#             return "{{c:{}}}".format(self.label)
#         else:
#             return "{{c:{} {}}}".format(self.label, self.value)
#
#     def get_plaintext(self):
#         ''' Returns the plain text representation of the object '''
#         if self.value==None:
#             return "{}".format(self.label)
#         else:
#             return "{} {}".format(self.label, self.value)
#
#
# class InfoLine(Line):
#     def __init__(self, text):
#         super().__init__(text, INFO)
#         self.find_info()
#
#     def __repr__(self):
#         ''' Representation of the object '''
#         return "{}Line('{}:{}')".format(self.category, self.info, self.value)
#
#     def find_info(self):
#         ''' Extracts the info type '''
#         group_dict =
#             LINE_TYPES[self.category].fullmatch(self.text).groupdict()
#
#         ## Get Info
#         self.info = group_dict["info"].lower()
#         ## Get Value
#         if group_dict["value"].isdigit():
#             self.value = int(group_dict["value"])
#         else:
#             self.value = group_dict["value"]
#
#     def get_chopro(self):
#         ''' Returns the ChordPro representation of the object '''
#         return "{{{}:{}}}".format(self.info, self.value)
#
#     def get_plaintext(self):
#         ''' Returns the plain text representation of the object '''
#         return "{}: {}".format(self.info, self.value)

if __name__ == "__main__":
    plaintext_parser = Decoder()
    song = plaintext_parser.decode(unidecode.unidecode('''
    Author    GuitarLearner 780   follow
    Intro:Fm,Db,Eb,Ebmaj7,Eb7,Fm,Db,Eb

    Verse
    Fm            Db
      I have this sinking feeling
    Eb                Eb     Ebmaj7 Eb7
     Something's weighing me down
    Fm       Db          Eb
     I am completely saturated
    Fm             Db
     The waves are crashing closer
    Eb               Ab
     My feet already drowned
    Fm         Db             Eb
     Doing the thing I said I hated

    Bridge
    Fm        Ab                   Eb    Bb7
     They¡¦ve been swimming in the wrong waters
    Fm   Ab                   Eb
     Now they¡¦re  pulling me down
    Fm      Ab                  Eb7           F7
     But I  am clinging to you, never letting go
            Fm             Ab         Eb
    ¡¥Cos I know that you¡¦ll lift me out

    Chorus
    Bbm       Fm
    Have your way here
    Ab          Eb             Bbm        Fm          Eb
     To keep me afloat ¡¥cos I know I¡¦ll sink without you
    Bbm       Fm   Ab  Eb           Bbm Fm
    Take this ocean of pain that is mine
    Eb (ring)
    Throw me a lifeline

    Intro played once

    Verse
    Wake up feeling convicted
    I know something¡¦s not right
    Re-acquaint my knees with the carpet
    I have to get this out
    ¡¥Cos it¡¦s obstructing you and I
    Dry up the seas that keep us parted

    Bridge
    Fm             Ab                   Eb    Bb7
    ¡¥Cos they¡¦ve been swimming in the wrong waters
    Fm        Ab                  Eb
      And now they¡¦re pulling me down
    Fm     Ab                  Eb
     But I am clinging to you, never letting go
            Fm        Ab            Eb
    ¡¥Cos I know that you are gonna pull me out

    [Chorus]
    Have your way here
    Keep me afloat ¡¥cos I know I¡¦ll sink without you
    Take this ocean of pain that is mine
    Throw me a lifeline

    Guitar chord break, pianos,appegio the intro.

    Bride (strum once & ring)
    Fm             Ab              Eb    Bb7
     They¡¦ve been swimming in the wrong waters
    Fm               Ab         Eb
    And now they¡¦re pulling me down
    Fm        Ab               Eb
     But I am clinging to you, never letting go
            Fm         Ab       Eb                   Bbm
    ¡¥Cos I know-oh-oh-oh-oh-oh-oh-oh-oh-oh-oh-wo-wo-oh..
      Fm          Ab
    I won't let go
      Eb
    I won't...
            Bbm  Fm    Eb
    ¡¥cos I know,yeah,yeah

    Chorus
                 Bbm       Fm
    That you¡¦ll have your way here
    Ab          Eb             Bbm        Fm         Eb
     To keep me afloat ¡¥cos I know I¡¦ll sink without you
    Bbm       Fm   Ab   Eb           Bbm Fm
    Take this ocean  of pain that is mine
    Eb
     Yeah
    Bbm       Fm
    Have your way here
    Ab          Eb             Bbm        Fm          Eb
     To keep me afloat ¡¥cos I know I¡¦ll sink without you
    Bbm       Fm   Ab  Eb           Bbm Fm
    Take this ocean of pain that is mine
    Eb (ring)
    Throw me a lifeline
    '''))
    print(song)
    filehandle = open("song_json_test", "w")
    json.dump(song, filehandle, indent=2)
    filehandle.close()
    # import doctest
    # doctest.testmod(verbose=True)
