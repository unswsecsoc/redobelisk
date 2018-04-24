import misaka as m
from pygments import highlight
from pygments.formatters import HtmlFormatter, ClassNotFound
from pygments.lexers import get_lexer_by_name
from pygments.styles import manni
import re

class HighlighterRenderer(m.HtmlRenderer):
    def blockcode(self, text, lang):
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except ClassNotFound:
            lexer = None

        if lexer:
            formatter = HtmlFormatter(style='manni')
            return highlight(text, lexer, formatter)
        # default
        return '\n<pre><code>{}</code></pre>\n'.format(text.strip())

class MarkdownRenderer():
    def __init__(self):
        self.mdRenderer = m.Markdown(HighlighterRenderer(), extensions=('fenced-code',))

    def manualReplace(self, s, r, t):
        l = len(s)
        for i in range(0,len(t)-l):
            if t[i:i+l] == s:
                t = t[0:i] + r + t[i+l:]
        return t
    def render(self, text, **kargs):
        if "plus" not in kargs:
            plus = False
        else:
            plus = kargs["plus"]
        return self.renderPlus(self.mdRenderer(text)) if plus else self.mdRenderer(text)

    def renderPlus(self, text):
        s = re.search('<p>\![^\!](.*?)</p>',text)
        while s:
            danger= "<div class='alert alert-dismissible alert-warning'>%s</div>"%s.group(1)
            text = self.manualReplace(s.group(0),danger,text)
            s = re.search('<p>\![^\!](.*?)</p>',text)

        s = re.search('<p>\!\!(.*?)</p>',text)
        while s:
            danger= "<div class='alert alert-dismissible alert-danger'>%s</div>"%s.group(1)
            text = self.manualReplace(s.group(0),danger,text)
            s = re.search('<p>\!\!(.*?)</p>',text)

        s = re.search('<blockquote>[\n\s]*<p>[\n\s]*(.*)[\n\s]*</p>[\n\s]*</blockquote>',text,flags=re.M)
        while s:
            if "!-" in s.group(1):
                main = s.group(1).split("!-")[0]
                author = s.group(1).split("!-")[1]
            else:
                main = s.group(1)
                author = None
            quote = "<blockquote class='blockquote' style='margin-left: 1em'>"
            quote += "<p class='mb-0'>%s</p>"%main
            if author:
                quote += "<footer class='blockquote-footer'><cite title='%s'>%s</cite></footer>"%(author,author)
            quote += "</blockquote>"
            text = self.manualReplace(s.group(0),quote,text)
            s = re.search('<blockquote>[\n\s]*<p>[\n\s]*(.*)[\n\s]*</p>[\n\s]*</blockquote>',text)
        return text
