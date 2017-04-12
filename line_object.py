'''

'''

# import json
# import re


class Line(object):
    ''' Contains a line of a song '''
    def __init__(self, text="", category=""):
        self.text = text.rstrip()
        self.category = category  # find_line_type(self.text)
        if self.category != "":
            assert(find_line_type(self.text) == self.category)

    def __repr__(self):
        ''' Representation of the object '''
        return "{}Line('{}')".format(self.category, self.text)

    def get_chopro(self):
        ''' Placeholder for when is cast into a specific line '''
        return self.text


class BlankLine(Line):
    def __init__(self, text=""):
        super().__init__(text, BLANK)

    def __repr__(self):
        ''' Representation of the object '''
        return "{}Line()".format(self.category)

    def get_chopro(self):
        ''' Returns the ChordPro representation of the object '''
        return self.get_plaintext()

    def get_plaintext(self):
        ''' Returns the plain text representation of the object '''
        return ""


class ChordLine(Line):
    def __init__(self, text):
        super().__init__(text, CHORD)
        self.find_chords()

    def find_chords(self):
        ''' Extracts the chords '''
        #~ line_list = self.text.split(" ")

        chord_list = []
        count = 0
        count_latched = 0
        inline_word = ""
        for char in self.text + " ":
            if char != " ":
                if inline_word == "":  # Just started a word
                    count_latched = count
                inline_word += char
            else:
                if inline_word != "":  # Just ended a word
                    # Now process the inline word
                    chord = CHORD_REGEX.fullmatch(inline_word)
                    instruction = INSTRUCTION_REGEX.fullmatch(inline_word)

                    if chord is not None:
                        chord_list.append(Chord(chord.groupdict()["chord"], count_latched))
                    elif instruction is not None:
                        chord_list.append(Instruction(instruction.groupdict()["instruction"].lower(), count))
                    inline_word = ""
            count += 1

        self.chord_list = chord_list

    def get_chopro(self):
        ''' Returns the ChordPro representation of the object '''
        return self.text  # TODO: Convert this to processed version

    def get_plaintext(self):
        ''' Returns the plain text representation of the object '''
        return self.text  # TODO: Convert this to processed version


class LyricLine(Line):
    def __init__(self, text, chords=None):
        super().__init__(text, LYRIC)
        self.chords = chords

    def __repr__(self):
        ''' Representation of the object '''
        return "{}Line('{}', {})".format(self.category, self.text, repr(self.chords))

    def set_chords(self, chords):
        ''' Sets the chords associated with the lyrics '''
        assert(isinstance(chords, ChordLine))
        self.chords = chords

    def get_chopro(self):
        ''' Returns the ChordPro representation of the object '''
        ### TODO: Maybe switch this with get_plaintext (and in other Lines)?
        new_text = self.text
        if self.chords is not None:
            for chord in reversed(self.chords.chord_list):
                pre_chord = new_text[0:chord.spacing]
                post_chord = new_text[chord.spacing:]
                new_text = pre_chord + str(chord) + post_chord

        return new_text

    def get_plaintext(self):
        ''' Returns the plain text representation of the object '''
        ### TODO: Actually write this function
        new_text = self.text
        if self.chords is not None:
            for chord in reversed(self.chords.chord_list):
                pre_chord = new_text[0:chord.spacing]
                post_chord = new_text[chord.spacing:]
                new_text = pre_chord + str(chord) + post_chord

        return new_text


class LabelLine(Line):
    def __init__(self, text):
        super().__init__(text, LABEL)
        self.find_label()

    def __repr__(self):
        ''' Representation of the object '''
        return "{}Line('{} {}')".format(self.category, self.label, self.value)

    def find_label(self):
        ''' Extracts the label type '''
        group_dict = LINE_TYPES[self.category].fullmatch(self.text).groupdict()

        ## Get Label Type
        if group_dict["pre"] is not None:
            self.label = "PRE-" + group_dict["label"].upper()
        else:
            self.label = group_dict["label"].upper()
        ## Get Value
        if group_dict["value"].isdigit():
            self.value = int(group_dict["value"])
        elif group_dict["value"] == "":
            self.value = None
        else:
            self.value = group_dict["value"]

    def get_chopro(self):
        ''' Returns the ChordPro representation of the object '''
        if self.value==None:
            return "{{c:{}}}".format(self.label)
        else:
            return "{{c:{} {}}}".format(self.label, self.value)

    def get_plaintext(self):
        ''' Returns the plain text representation of the object '''
        if self.value==None:
            return "{}".format(self.label)
        else:
            return "{} {}".format(self.label, self.value)


class InfoLine(Line):
    def __init__(self, text):
        super().__init__(text, INFO)
        self.find_info()

    def __repr__(self):
        ''' Representation of the object '''
        return "{}Line('{}:{}')".format(self.category, self.info, self.value)

    def find_info(self):
        ''' Extracts the info type '''
        group_dict = LINE_TYPES[self.category].fullmatch(self.text).groupdict()

        ## Get Info
        self.info = group_dict["info"].lower()
        ## Get Value
        if group_dict["value"].isdigit():
            self.value = int(group_dict["value"])
        else:
            self.value = group_dict["value"]

    def get_chopro(self):
        ''' Returns the ChordPro representation of the object '''
        return "{{{}:{}}}".format(self.info, self.value)

    def get_plaintext(self):
        ''' Returns the plain text representation of the object '''
        return "{}: {}".format(self.info, self.value)


class TabLine(Line):
    def __init__(self, text):
        super().__init__(text, TAB)


if __name__ == "__main__":
    Inline()
    import doctest
    # doctest.testmod(verbose=True)
    doctest.testmod(verbose=False)
