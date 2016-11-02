# -*- coding: utf-8 -*-
from random import choice
import sys

class Piece:
    PAWN = 0
    BISHOP = 1
    KNIGHT = 2
    ROOK = 3
    QUEEN = 4
    KING = 5
    
    def __init__(self, typecode, white):
        #if not 0 <= typecode <= 5:
        #    raise NameError("Bad typecode")
        self.type = typecode
        self.white = white

    def __str__(self):
        #(("♟", "♙"), ("♝", "♗"), ("♞", "♘"), ("♜", "♖"), ("♛", "♕"), ("♚", "♔"))
        return (("p", "P"), ("b", "B"), ("n", "N"), ("r", "R"), ("q", "Q"), ("k", "K"))[self.type][self.white]

    def valid_moves(self, source_file, source_rank, board, gamestate):
        res = set()
        if self.type == Piece.PAWN:
            step = 1 if self.white else -1
            if not board.get_piece(source_file, source_rank + step):
                res.add((source_file, source_rank, source_file, source_rank + step))
                if source_rank == (1 if self.white else 6) and not board.get_piece(source_file, source_rank + step + step): #2 rank difference ok
                    res.add((source_file, source_rank, source_file, source_rank + step + step))
            if source_file > 0:
                p = board.get_piece(source_file - 1, source_rank + step)
                if p and p.white ^ self.white:
                    res.add((source_file, source_rank, source_file - 1, source_rank + step))
            if source_file < 7:
                p = board.get_piece(source_file + 1, source_rank + step)
                if p and p.white ^ self.white:
                    res.add((source_file, source_rank, source_file + 1, source_rank + step))

        elif self.type == Piece.KING:
            for file in range(max(0, source_file - 1), min(7, source_file + 1) + 1):
                for rank in range(max(0, source_rank - 1), min(7, source_rank + 1) + 1):
                    p = board.get_piece(file, rank)
                    if not p or p.white ^ self.white:
                        res.add((source_file, source_rank, file, rank))
            #kolla rokad

        elif self.type == Piece.KNIGHT:
            for delta in [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]:
                file = source_file + delta[0]
                rank = source_rank + delta[1]
                if 0 <= file <= 7 and 0 <= rank <= 7:
                    p = board.get_piece(file, rank)
                    if not p or p.white ^ self.white:
                        res.add((source_file, source_rank, file, rank))

        elif self.type == Piece.ROOK or self.type == Piece.QUEEN:
            for file in range(source_file + 1, 8):
                p = board.get_piece(file, source_rank)
                if not p:
                    res.add((source_file, source_rank, file, source_rank))
                else:
                    if p.white ^ self.white:
                        res.add((source_file, source_rank, file, source_rank))
                    break
            for file in range(source_file - 1, -1, -1):
                p = board.get_piece(file, source_rank)
                if not p:
                    res.add((source_file, source_rank, file, source_rank))
                else:
                    if p.white ^ self.white:
                        res.add((source_file, source_rank, file, source_rank))
                    break
            for rank in range(source_rank + 1, 8):
                p = board.get_piece(source_file, rank)
                if not p:
                    res.add((source_file, source_rank, source_file, rank))
                else:
                    if p.white ^ self.white:
                        res.add((source_file, source_rank, source_file, rank))
                    break
            for rank in range(source_rank - 1, -1, -1):
                p = board.get_piece(source_file, rank)
                if not p:
                    res.add((source_file, source_rank, source_file, rank))
                else:
                    if p.white ^ self.white:
                        res.add((source_file, source_rank, source_file, rank))
                    break

        if self.type == Piece.BISHOP or self.type == Piece.QUEEN:
            #print("Piece at", "abcdefgh"[source_file] + str(source_rank + 1))
            for filedir in [-1, 1]:
                for rankdir in [-1, 1]:
                    file = source_file + filedir
                    rank = source_rank + rankdir
                    #print(filedir, rankdir)
                    while 0 <= file <= 7 and 0 <= rank <= 7:
                        p = board.get_piece(file, rank)
                        #print(p or "-", "abcdefgh"[file] + str(rank + 1))
                        if not p:
                            res.add((source_file, source_rank, file, rank))
                        else:
                            if p.white ^ self.white:
                                res.add((source_file, source_rank, file, rank))
                            break
                        file += filedir
                        rank += rankdir
        
        return res


class Board:
    def __init__(self, empty=False):
        self.content = [[None for rank in range(8)] for file in range(8)]
        if not empty:
            #place pawns
            for file in range(8):
                self.place_piece(Piece(Piece.PAWN, True), file, 1)
                self.place_piece(Piece(Piece.PAWN, False), file, 6)
            #place rooks
            for file in [0, 7]:
                self.place_piece(Piece(Piece.ROOK, True), file, 0)
                self.place_piece(Piece(Piece.ROOK, False), file, 7)
            #place knights
            for file in [1, 6]:
                self.place_piece(Piece(Piece.KNIGHT, True), file, 0)
                self.place_piece(Piece(Piece.KNIGHT, False), file, 7)
            #place bishops
            for file in [2, 5]:
                self.place_piece(Piece(Piece.BISHOP, True), file, 0)
                self.place_piece(Piece(Piece.BISHOP, False), file, 7)
            #place kings, queens
            self.place_piece(Piece(Piece.QUEEN, True), 3, 0)
            self.place_piece(Piece(Piece.QUEEN, False), 3, 7)
            self.place_piece(Piece(Piece.KING, True), 4, 0)
            self.place_piece(Piece(Piece.KING, False), 4, 7)

                
    def get_piece(self, file, rank):
        return self.content[file][rank]

    def place_piece(self, piece, file, rank, override=False):
        if not override and self.content[file][rank] is not None:
            raise NameError("Square already occupied")
        self.content[file][rank] = piece

    def move(self, source_file, source_rank, dest_file, dest_rank):
        mover = self.get_piece(source_file, source_rank)
        if not mover:
            raise NameError("No piece to move")
        removed = self.get_piece(dest_file, dest_rank)
        self.place_piece(None, source_file, source_rank, True)
        self.place_piece(mover, dest_file, dest_rank, True)

        return removed

    def valid_move(self, piece, source_file, source_rank, dest_file, dest_rank, gamedata):
        if not (0 <= source_file <= 7 and 0 <= source_rank <= 7 and 0 <= dest_file <= 7 and 0 <= dest_rank <= 7):
            return False
        if source_file == dest_file and source_rank == dest_rank:
            return False

        if piece.type == Piece.PAWN and dest_rank == source_rank + (1 if piece.white else -1): #rank difference 1 for pawns
            if source_file == dest_file and not self.get_piece(dest_file, dest_rank): #same file and no piece in the way
                return True
            elif abs(source_file - dest_file) == 1: #file difference 1
                p = self.get_piece(dest_file, dest_rank)
                if p and p.white ^ piece.white: #there exists a captured piece of opposing color
                    return True
            #kolla en passant!
        elif piece.type == Piece.PAWN and dest_rank == source_rank + (2 if piece.white else -2) == (3 if piece.white else 4) and source_file == dest_file: #rank difference 2 if in starting position
            if not self.get_piece(source_file, source_rank + (1 if piece.white else -1)) and not self.get_piece(source_file, dest_rank): #nothing in the way of the move
                return True

        elif piece.type == Piece.KING and abs(source_file - dest_file) <= 1 and abs(source_rank - dest_rank) <= 1: #rank and file difference 1 for kings
            p = self.get_piece(dest_file, dest_rank)
            if not p or p.white ^ piece.white: #piece absent or of opposing color
                return True

        elif (piece.type == Piece.ROOK or piece.type == Piece.QUEEN) and (dest_file - source_file == 0 or dest_rank - source_rank == 0): #rook stays on same file or rank
            endpiece = self.get_piece(dest_file, dest_rank)
            if not endpiece or endpiece.white ^ piece.white: #piece absent or of opposing color
                if dest_file > source_file:
                    for file in range(source_file + 1, dest_file):
                        if self.get_piece(file, dest_rank):
                            return False
                elif dest_file < source_file:
                    for file in range(dest_file + 1, source_file):
                        if self.get_piece(file, dest_rank):
                            return False
                elif dest_rank > source_rank:
                    for rank in range(source_rank + 1, dest_rank):
                        if self.get_piece(dest_file, rank):
                            return False
                else: # dest_rank < source_rank
                    for rank in range(dest_rank + 1, source_rank):
                        if self.get_piece(dest_file, rank):
                            return False
                return True

        elif (piece.type == Piece.BISHOP or piece.type == Piece.QUEEN) and abs(dest_file - source_file) == abs(dest_rank - source_rank): #rank difference equal to file difference
            endpiece = self.get_piece(dest_file, dest_rank)
            if not endpiece or endpiece.white ^ piece.white: #piece absent or of opposing color
                filedir = 1 if dest_file - source_file > 0 else -1
                rankdir = 1 if dest_rank - source_rank > 0 else -1
                diff = abs(dest_file - source_file)
                for i in range(1, diff):
                    if self.get_piece(source_file + filedir * i, source_rank + rankdir * i):
                        return False
                return True

        elif piece.type == Piece.KNIGHT and abs((dest_file - source_file) * (dest_rank - source_rank)) == 2: #rank difference * file difference is two for knights
            p = self.get_piece(dest_file, dest_rank)
            if not p or p.white ^ piece.white:
                return True

        return False
            
    def parse_move(self, s, white, gamedata):
        if not s or len(s) < 2:
            raise NameError("Bad move")

        #kingside castling
        if s == "0-0" or s == "O-O":
            raise NameError("Kingside castling not implemented")
        #queenside castling
        if s == "0-0-0" or s == "O-O-O":
            raise NameError("Queenside castling not implemented")

        #get promotion

        #get destination
        i = len(s) - 1
        while not 48 <= ord(s[i]) <= 57: #while s[i] isn't 0-9
            i -= 1
        dest_rank = ord(s[i]) - 48 - 1
        i -= 1
        dest_file = ord(s[i].lower()) - 97 #a -> 0, b ..., h -> 7
        i -= 1
        
        #indicates capture
        if i >= 0:
            if s[i] == ":" or s[i] == "x":
                i -= 1
        
        #disambiguating
        source_file, source_rank = -1, -1
        if i >= 0:
            if 0 <= ord(s[i]) - 97 <= 7:
                source_file = ord(s[i]) - 97
                i -= 1
            elif 0 <= ord(s[i]) - 48 - 1 <= 7:
                source_rank = ord(s[i]) - 48 - 1
                i -= 1
        if i >= 0:
            if 0 <= ord(s[i]) - 97 <= 7:
                source_file = ord(s[i]) - 97
                i -= 1

        #moving piece type
        piece_type = Piece.PAWN
        if i >= 0:
            if s[i] == "B":
                piece_type = Piece.BISHOP
            elif s[i] == "N":
                piece_type = Piece.KNIGHT
            elif s[i] == "R":
                piece_type = Piece.ROOK
            elif s[i] == "Q":
                piece_type = Piece.QUEEN
            elif s[i] == "K":
                piece_type = Piece.KING

        if source_file == -1 or source_rank == -1:
            source_file, source_rank, dest_file, dest_rank = self._find_moving_piece(white, piece_type, source_file, source_rank, dest_file, dest_rank, gamedata)

        return self.move(source_file, source_rank, dest_file, dest_rank)

    #returns a move tuple instead of a piece. sorry :/
    def _find_moving_piece(self, white, typecode, source_file, source_rank, dest_file, dest_rank, gamedata):
        #ineffektivt, antagligen
        if source_file != -1:
            for rank in range(8):
                p = self.get_piece(source_file, rank)
                if p and p.white == white and p.type == typecode and self.valid_move(p, source_file, rank, dest_file, dest_rank, gamedata):
                    return source_file, rank, dest_file, dest_rank

        elif source_rank != -1:
            for file in range(8):
                p = self.get_piece(file, source_rank)
                if p and p.white == white and p.type == typecode and self.valid_move(p, file, source_rank, dest_file, dest_rank, gamedata):
                    return file, source_rank, dest_file, dest_rank
        else:
            for file in range(8):
                for rank in range(8):
                    p = self.get_piece(file, rank)
                    if p and p.white == white and p.type == typecode and self.valid_move(p, file, rank, dest_file, dest_rank, gamedata):
                        return file, rank, dest_file, dest_rank

        raise NameError("Couldn't find the piece, may be invalid move")

    #actually yields pieces (and source file and rank)
    def _enumerate_moving_pieces(self, white, typecode, source_file, source_rank, dest_file, dest_rank, gamedata):
        #ineffektivt, antagligen
        if source_file != -1:
            for rank in range(8):
                p = self.get_piece(source_file, rank)
                if p and p.white == white and p.type == typecode and self.valid_move(p, source_file, rank, dest_file, dest_rank, gamedata):
                    yield p, source_file, rank

        elif source_rank != -1:
            for file in range(8):
                p = self.get_piece(file, source_rank)
                if p and p.white == white and p.type == typecode and self.valid_move(p, file, source_rank, dest_file, dest_rank, gamedata):
                    yield p, file, source_rank
        else:
            for file in range(8):
                for rank in range(8):
                    p = self.get_piece(file, rank)
                    if p and p.white == white and p.type == typecode and self.valid_move(p, file, rank, dest_file, dest_rank, gamedata):
                        yield p, file, rank

    def format_move(self, source_file, source_rank, dest_file, dest_rank, gamedata):
        #print(chr(source_file + 97) + chr(source_rank + 48 + 1), "->", chr(dest_file + 97) + chr(dest_rank + 48 + 1)) 
        mover = self.get_piece(source_file, source_rank)
        if not mover:
            raise NameError("No piece to move, from " + chr(source_file + 97) + chr(source_rank + 48 + 1) + " to " + chr(dest_file + 97) + chr(dest_rank + 48 + 1))
        removed = self.get_piece(dest_file, dest_rank)
        white = mover.white
        possible_pieces = [(piece, file, rank) for piece, file, rank in self._enumerate_moving_pieces(white, mover.type, -1, -1, dest_file, dest_rank, gamedata) if piece.type == mover.type]
        #print([(str(a), b, c) for a, b, c in possible_pieces])
        if len(possible_pieces) == 1:
            return ("" if mover.type == Piece.PAWN else str(mover)).upper() + ("x" if removed else "") + chr(dest_file + 97) + chr(dest_rank + 48 + 1)
        
        file_unique, rank_unique = True, True
        for piece, file, rank in possible_pieces:
            if not (file == source_file and rank == source_rank):
                if file == source_file:
                    file_unique = False
                if rank == source_rank:
                    rank_unique = False

        if file_unique:
            return ("" if mover.type == Piece.PAWN else str(mover)).upper() + chr(source_file + 97) + ("x" if removed else "") + chr(dest_file + 97) + chr(dest_rank + 48 + 1)
        elif rank_unique:
            return ("" if mover.type == Piece.PAWN else str(mover)).upper() + chr(source_rank + 48 + 1) + ("x" if removed else "") + chr(dest_file + 97) + chr(dest_rank + 48 + 1)
        else:
            return ("" if mover.type == Piece.PAWN else str(mover)).upper() + chr(source_file + 97) + chr(source_rank + 48 + 1) + ("x" if removed else "") + chr(dest_file + 97) + chr(dest_rank + 48 + 1)

    def __str__(self):
        res = ""
        for rank in range(7, -1, -1):
            for file in range(0, 8):
                res += str(self.get_piece(file, rank) or " ")
            res += " " + str(rank + 1) + "\n"
        res += "abcdefgh"
        return res


class ChessBot:
    pass

b = Board()

white = True
while True:
    print()
    print(b)
    print()

    moves = []
    for rank in range(8):
        for file in range(8):
            if b.get_piece(file, rank) and not b.get_piece(file, rank).white ^ white:
                #print("Possible moves involving " + str(b.get_piece(file, rank)) + " at " + chr(file + 97) + chr(rank + 48 + 1))
                for move in [b.format_move(s_f, s_r, d_f, f_r, {}) for s_f, s_r, d_f, f_r in b.get_piece(file, rank).valid_moves(file, rank, b, {})]:
                    moves.append(move)
    print(*moves, sep="\t")

    try:
        b.parse_move(input(("White" if white else "Black") + ">"), white, {})
    except BaseException as e:
        print(e)
        continue
    white ^= True
