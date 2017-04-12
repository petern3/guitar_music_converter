'''


'''


import re

BLANK = "Blank"
CHORD = "Chord"
LYRIC = "Lyric"
LABEL = "Label"
INFO = "Info"
TAB = "Tab"

CHORD_REGEX = re.compile("(?P<chord>(?P<root>[A-G][#b]?)(?P<mod>(m|sus|add|maj|dim|aug)?[0-9]?)*(?P<bass>\/[A-G][#b])?)")
INSTRUCTION_REGEX = re.compile("\(?(?P<instruction>[Rr]ing|[Mm]ute|[Rr]ake|PM|pm)\)?")
LABEL_TYPES = [
    "intro",
    "verse",
    "chorus",
    "bridge",
    "solo",
    "tab",
    "tag",
    "ending",
    "outro",
    "repeat",
]
INFO_TYPES = [
    "title",
    "subtitle",
    "author",
    "album",
    "copyright",
    "ccli",
    "capo",
    "key",
    "time",
    "tempo",
]

def chord_regex_gen():
    ''' Generates the chord regular expression '''
    regex = "( *({0}|{1}))+".format(CHORD_REGEX.pattern, INSTRUCTION_REGEX.pattern)
    return re.compile(regex)

def label_regex_gen():
    ''' Generates the label regular expression '''
    middle = ""
    for label in LABEL_TYPES:
        middle = middle + label + "|"
    regex = " *(?P<pre>pre)?[ \-]?(?P<label>{0}) *(?P<value>x?[0-9]*)".format(middle[:-1])
    return re.compile(regex, re.IGNORECASE)

def info_regex_gen():
    ''' Generates the info regular expression '''
    middle = ""
    for info in INFO_TYPES:
        middle = middle + info + "|"
    regex = " *(?P<info>{0})\W+(?P<value>[0-9]+|.+)".format(middle[:-1])
    return re.compile(regex, re.IGNORECASE)

def tab_regex_gen():
    ''' Generates the tab regular expression '''
    regex = "\s*(\|{0,2}[A-Gb]?\|{0,2}[-x0-9|:]{4,})"
    return re.compile(regex)

LINE_TYPES = {
    BLANK: re.compile("(\s*)"),
    CHORD: chord_regex_gen(),
    LABEL: label_regex_gen(),
    INFO: info_regex_gen(),
    TAB: tab_regex_gen()
}

def find_inline_type(text):
    ''' Decides whether text is a chord or instruction  '''
    if CHORD_REGEX.fullmatch(text) is not None:
        return "Chord"
    if INSTRUCTION_REGEX.fullmatch(text) is not None:
        return "Instruction"
    return "Inline"

def find_line_type(text):
    ''' Takes an estimate of the type of line it is  '''
    for (line_type, line_regex) in LINE_TYPES.items():
        if line_regex.fullmatch(text):
            return line_type
    return LYRIC

def create_line(text):
    ''' Creates a line of the correct category '''
    category = find_line_type(text)
    return eval("{}Line({})".format(category, repr(text)))


class Inline(object):
    def __init__(self, text, spacing=0, category="Inline"):
        self.text = text
        self.spacing = spacing
        self.category = category
        if self.category != "Inline":
            assert(find_inline_type(self.text) == self.category)

    def __repr__(self):
        ''' Representation of the object '''
        return "{}('{}', {})".format(self.category, self.text, self.spacing)

    def __str__(self):
        ''' String representation of the object '''
        return self.get_chopro()

    def get_chopro(self):
        ''' Returns the ChordPro representation of the object '''
        return "[{}]".format(self.text)

class Instruction(Inline):
    def __init__(self, text, spacing=0):
        super().__init__(text, spacing, "Instruction")

    def get_plaintext(self):
        ''' Returns the plain text representation of the object '''
        return "({})".format(self.text)


class Chord(Inline):
    def __init__(self, text, spacing=0):
        super().__init__(text, spacing, "Chord")
        self.find_chord_parts()

    def find_chord_parts(self):
        ''' Extracts the chord parts '''
        group_dict = CHORD_REGEX.fullmatch(self.text).groupdict()
        self.root = group_dict['root']
        self.mod = group_dict['mod']
        self.bass = group_dict['bass']

    def transpose(self, semitones):
        ''' Transposes the chord '''
        pass

    def get_plaintext(self):
        ''' Returns the plain text representation of the object '''
        # TODO: Extract from root, mod and bass
        return "{}".format(self.text)


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

    def __str__(self):
        ''' String representation of the object '''
        return self.get_chopro()

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
    import doctest
    doctest.testmod(verbose=True)
    #~ doctest.testfile("regex_doctests.py")
