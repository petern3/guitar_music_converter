from . import plaintext_parser
from . import json_parser

encoders = {
    'plaintext': plaintext_parser.Encoder,
    'json': json_parser.Encoder,
}

decoders = {
    'plaintext': plaintext_parser.Decoder,
    'json': json_parser.Decoder,
}
