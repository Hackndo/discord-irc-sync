import re
from .utils import replace_all

IRC_BOLD, IRC_ITALIC, IRC_UNDERLINE, IRC_RESET = ("\x02","\x1d", "\x1f", "\x0f")
DSC_BOLD, DSC_ITALIC, DSC_UNDERLINE = ("**","*","__")

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
        return re.sub(r'\\([^A-Za-z0-9])',r'\1', message)

    def format(self, message):
        message = self.sanitize(message)
        for rule in self.rules:
            regex = self.syntax[rule]['re']
            m = regex.search(message)
            if m is not None:
                message = regex.sub(getattr(self, 'replace_%s' % rule), message)
        return message

class I2DFormatter: # @TODO

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
        message = self.sanitize(message)
        return message
