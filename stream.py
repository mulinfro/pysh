from syntax_check import Error
class stream():
    
    def __init__(self, lst, pos=0):
        self._stream = lst
        self.pos = pos
        self.token_record = []

    def lookahead(self):
        return self._stream[self.pos - 1]

    def peek(self):
        if self.eof():  self.crack("EOL while scanning string literal")
        return self._stream[self.pos]

    def back(self):
        self.pos = self.pos - 1
        #return self.looknext()

    def next(self):
        ch = self.peek()
        self.token_record.append(ch)
        self.pos = self.pos + 1
        return ch

    def eof(self):
        return self.pos >= len(self._stream)

    def hasnext(self):
        return self.pos < len(self._stream) - 1

    def looknext(self):
        self.next()
        ch = self.peek()
        self.back()
        return ch

    def leftnum(self):
        return len(self._stream) - self.pos

    def crack(self, msg):
        Error("Syntax Error: " + msg, 0,0)

    def get_record(self):
        val =  self.token_record
        self.token_record = []
        return val
