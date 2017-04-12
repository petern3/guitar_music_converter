'''

'''


import re


import source_parsers
import format_parsers

FILENAME_REGEX = re.compile("^([A-Z]:)?(([\\\/])?[\w|\.-]+)+$")
URL_REGEX = re.compile("^(http|https):\/\/.+$")  # ftp, smtp, tftp, sftp, nntp

# if FILENAME_REGEX.fullmatch(input_var):
#     self.parse_file(input_var)
# elif URL_REGEX.fullmatch(input_var):
#     self.parse_website(input_var)
# else:
#     self.parse_string(input_var)


if __name__ == "__main__":
    filehandle = open("example_formats/song_original.txt")
    filehandle2 = open("example_formats/song_plain3.txt", "w")
    song = source_parsers.unicode_file_parser.read(filehandle, format_parsers.plaintext_parser.Decoder())
    source_parsers.unicode_file_parser.write(song, filehandle2, format_parsers.plaintext_parser.Encoder())
    filehandle.close()
    filehandle2.close()
