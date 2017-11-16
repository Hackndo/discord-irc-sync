import re
from .utils import replace_all, is_included

IRC_BOLD, IRC_ITALIC, IRC_UNDERLINE, IRC_RESET = ("\x02","\x1d", "\x1f", "\x0f")
DSC_BOLD, DSC_ITALIC, DSC_UNDERLINE = ("**","*","__")
WORD_ELEMENTS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

class D2IFormatter():

    syntax = {
        'double_emphasis': {
            're': re.compile(r'(\*{2})([\s\S]+?)(\*{2})(?!\*)'),
            'irc': IRC_BOLD,
            'discord': DSC_BOLD 
        },
        'emphasis': {
            're': re.compile(
                r'\b(_)((?:__|[^_])+?)(_)\b'  # _word_
                r'|'
                r'(\*)((?:\*\*|[^\*])+?)(\*)(?!\*)'  # *word*
            ),
            'irc': IRC_ITALIC,
            'discord': DSC_ITALIC
        },
        'underline': {
            're': re.compile(r'(_{2})([\s\S]+?)(_{2})(?!_)'),
            'irc': IRC_UNDERLINE,
            'discord': DSC_UNDERLINE
        }
    }

    rules = ['double_emphasis', 'emphasis', 'underline']

    def replace_double_emphasis(self, matchobj):
        return self.syntax['double_emphasis']['irc'] + matchobj.group(2) + self.syntax['double_emphasis']['irc'] 

    def replace_emphasis(self, matchobj):
        if matchobj.group(2):
            res = matchobj.group(2)
        else:
            res = matchobj.group(5)
        return self.syntax['emphasis']['irc'] + res + self.syntax['emphasis']['irc'] 

    def replace_underline(self, matchobj):
        return self.syntax['underline']['irc'] + matchobj.group(2) + self.syntax['underline']['irc'] 

    def sanitize(self, message):
        message = re.sub(r'\\([^A-Za-z0-9])',r'\1', message)
        return message

    def format(self, message):
        message = self.sanitize(message)
        for rule in self.rules:
            regex = self.syntax[rule]['re']
            m = regex.search(message)
            if m is not None:
                message = regex.sub(getattr(self, 'replace_%s' % rule), message)
        return message

class I2DFormatter:

    B_FLAG, I_FLAG, U_FLAG = (0x01, 0x02, 0x04)

    symbols = {
        IRC_BOLD: B_FLAG,
        IRC_ITALIC: I_FLAG,
        IRC_UNDERLINE: U_FLAG,
        IRC_RESET: False
    }

    def sanitize(self, message):
        replacements = [('\\','\\\\'), ('*','\\*'), ('_','\\_')]
        message = replace_all(message, replacements)
        return re.sub(
                r'\x03\d{2}(?:,\d{2})'
                r'|'
                r'['+ IRC_BOLD + IRC_UNDERLINE + IRC_ITALIC + IRC_RESET +']',
                '',
                message)

    def format(self, message):
        char_list = [(c,0) for c in message]
        counter = 0
        while counter < len(char_list):
            char_tuple=char_list[counter]
            
            if char_tuple[0] in self.symbols: # Formatting character
                del char_list[counter]
                for i in range(counter, len(char_list)):
                    if self.symbols[char_tuple[0]]:
                        char_list[i] = (char_list[i][0], char_list[i][1]^self.symbols[char_tuple[0]])
                    else:
                        char_list[i] = (char_list[i][0], 0)
            else: # Common character. Goto next one
                counter+=1
        
        intervals = []
        bi = None
        ui = None
        ii = None
        for key, char_tuple in enumerate(char_list):
            if key == 0:
                if char_tuple[1] & self.B_FLAG:
                    bi = [DSC_BOLD, 0, False]
                if char_tuple[1] & self.I_FLAG:
                    ii = [DSC_ITALIC, 0, False]
                if char_tuple[1] & self.U_FLAG:
                    ui = [DSC_UNDERLINE, 0, False]
            else:
                if char_tuple[1] & self.B_FLAG ^ char_list[key-1][1] & self.B_FLAG:
                    if bi is not None:
                        bi[2] = key
                        intervals.append(bi)
                        bi = None
                    else:
                        bi = [DSC_BOLD, key, False]
                if char_tuple[1] & self.I_FLAG ^ char_list[key-1][1] & self.I_FLAG:
                    if ii is not None:
                        ii[2] = key
                        intervals.append(ii)
                        ii = None
                    else:
                        ii = [DSC_ITALIC, key, False]
                if char_tuple[1] & self.U_FLAG ^ char_list[key-1][1] & self.U_FLAG:
                    if ui is not None:
                        ui[2] = key
                        intervals.append(ui)
                        ui = None
                    else:
                        ui = [DSC_UNDERLINE, key, False]

        # Close unclosed intervals
        if bi is not None:
            bi[2] = len(char_list)
            intervals.append(bi)
        if ii is not None:
            ii[2] = len(char_list)
            intervals.append(ii)
        if ui is not None:
            ui[2] = len(char_list)
            intervals.append(ui)

        # No formatting necessary
        if intervals == []:
            return self.sanitize(message)
        
        key = 0
        ordered_intervals = [] if len(intervals) > 1 else intervals
        while len(intervals) > 1:
            included = False
            current = intervals[key]
            for k_tested, interval in enumerate(intervals[key+1:]):
                if is_included(current, interval) == 0:
                    included = True
                    continue
            if not included:
                ordered_intervals.append(intervals[key])
                del intervals[key]
            else:
                key = (key+1)%len(intervals)
            if len(intervals) == 1:
                ordered_intervals.append(intervals[0])
        
        res = ''.join([c[0] for c in char_list])
        add = []
        for c in range(len(res)+1):
            add.append([])
        for c in range(len(res)):
            for i in ordered_intervals[::-1]:
                if c == i[2]-1:
                    add[c+1].append(i[0])
            for i in ordered_intervals:
                if c == i[1]:
                    add[c].append(i[0])

        result = ''.join(''.join(add[i]) + res[i] for i in range(len(res)))
        return self.sanitize(result)

"""
print(I2DFormatter().format(IRC_BOLD + "no" + IRC_BOLD + IRC_UNDERLINE + "o" + IRC_UNDERLINE + "rmal " + IRC_BOLD + "bold " + IRC_ITALIC + "boldItalic " + IRC_ITALIC + "bold " + IRC_BOLD + "normal " + IRC_UNDERLINE + "AB" + IRC_ITALIC + "CD" + IRC_UNDERLINE + "EF" + IRC_ITALIC))
print(I2DFormatter().format(IRC_BOLD + "Haha"))
"""