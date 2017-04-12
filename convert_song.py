'''

'''


import re


#~ import song_parsers
import song_parsers#.chordpro_parser

[print(t) for t in song_parsers.__dict__.items()]

FILENAME_REGEX = re.compile("^([A-Z]:)?(([\\\/])?[\w|\.-]+)+$")
URL_REGEX = re.compile("^(http|https):\/\/.+$")  # ftp, smtp, tftp, sftp, nntp

        #~ if FILENAME_REGEX.fullmatch(input_var):
            #~ self.parse_file(input_var)
        #~ elif URL_REGEX.fullmatch(input_var):
            #~ self.parse_website(input_var)
        #~ else:
            #~ self.parse_string(input_var)


if __name__ == "__main__":
    import doctest
    #~ doctest.testmod(verbose=True)
    #~ doctest.testfile("regex_doctests.py")

