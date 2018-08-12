from tetromino.pieces.abstractpiece import Piece


class IPiece(Piece):
    _templates = [
        ['..O..',
         '..O..',
         '..O..',
         '..O..',
         '.....'],
        ['.....',
         '.....',
         'OOOO.',
         '.....',
         '.....']
    ]

    def __init__(self):
        super().__init__()
        self._piece_type= 'I'

