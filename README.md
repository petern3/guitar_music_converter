# Guitar Music Converter
A set of tools to convert between guitar music formats

## About
This project was initially an attempt to programmatically convert guitar music
from plaintext (as in most [guitar](https://www.ultimate-guitar.com/)
[music](http://www.e-chords.com/) websites) to the chordpro format (as
[chordie](http://www.chordie.com/) and [worship
together](http://www.worshiptogether.com/) can provide). This is similar to
several other git projects, with the difference that it is intended to be easy
to add new formats/sources (see below).

<!-- ## Dependencies
#### Essential
`pip install pychord` - For parsing chords, and finding finger placements -->

<!-- #### Optional
`pip install python-pptx` - For parsing from .pptx files -->


## File Breakdown
There are four parts of the project:
1. Command-line program to convert between formats
2. Parser to read/write to different sources (such as files or URLs)
3. Parser to read/write to a string from different formats
4. A intermediate format to store the information regardless of music type

### 1) Command-line Program
    convert_song.py

This hasn't been done properly yet. It doubles as an example of how to use the
python packages.

### 2) Source Parsers
    source_parsers/*

For each source, there is one parser capable of reading and writing from the
source and feeding it into one of the format_parsers. Sources include:
- Text files
- URLs**
  - HTTP/HTTPS**
  - FTP**
- MS Word files**
- MS Powerpoint files* (this is because I have lots of music in an obscure powerpoint format)

_*Will be implemented_

_**May be implemented_

### 3) Format Parsers
    format_parsers/*

When the source_parser has created a string of the relevant section, the
format_parsers will turn it into the Song format. Formats include:
- Plaintext


    VERSE
    Fm            Db
      I have this sinking feeling

- Chordpro*


    {c:VERSE}          
    [Fm]  I have this [Db]sinking feeling

- json (because this is the native format of the Song object, see below for
    example)

- Latex**
- HTML** (if not converted by the source_parser)

_*Will be implemented_

_**May be implemented_

Full examples can be found in the example_formats folder

### 4) Internal Song Format
    song_object.py
    song_primitives.py

The Song object is a structure for containing all the song meta-data (title,
author, capo etc) as well as the music itself. The data is all stored in a
dictionary/list tree structure so that it is easy to save as a json to debug.
The song primitives include classes for: Meta-data, Labels (eg Verses), Chords
and Instructions (eg 'Mute').

A sample of what a line looks like is below. It is by no means the most compact
or human-readible format, but it shows how the data is stored, and what kind
of information it holds.


    {
      "line_list": [
        {
          "chord_dict": {
            "0": {
              "bass": null,
              "root": "F",
              "mod": "m"
            },
            "14": {
              "bass": null,
              "root": "Db",
              "mod": null
            }
          },
          "lyric": "  I have this sinking feeling"
        }
      ],
      "label": {
        "alt": null,
        "label_type": "verse",
        "value": null,
        "pre": false
      }
    }

## Known Bugs

- The programs attempts to convert unicode characters to ascii, but does
not always work. Suspected to be related to the python build, see the
[unidecode page](https://pypi.python.org/pypi/Unidecode), under 'Requirements'
If fixed, be sure to check the chordpro parser line chord spacings.
