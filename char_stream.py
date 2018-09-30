from stream import stream

class char_stream(stream):
    line, col = 1, 1

    def next(self):
        ch = self.peek()
        self.col = self.col + 1
        if ch == '\n':
            self.col = 1
            self.line = self.line + 1
        self.pos = self.pos + 1
        return ch


