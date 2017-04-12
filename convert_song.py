'''

'''


import re


import source_parsers
# import source_parsers.plaintext_file_parser

# [print(t) for t in source_parsers.__dict__.items()]

FILENAME_REGEX = re.compile("^([A-Z]:)?(([\\\/])?[\w|\.-]+)+$")
URL_REGEX = re.compile("^(http|https):\/\/.+$")  # ftp, smtp, tftp, sftp, nntp

# if FILENAME_REGEX.fullmatch(input_var):
#     self.parse_file(input_var)
# elif URL_REGEX.fullmatch(input_var):
#     self.parse_website(input_var)
# else:
#     self.parse_string(input_var)


if __name__ == "__main__":
    filehandle = open("song.txt")
    filehandle2 = open("song2.txt", "w")
    song = source_parsers.plaintext_file_parser.read(filehandle)
    source_parsers.plaintext_file_parser.write(song, filehandle2)
    filehandle.close()
