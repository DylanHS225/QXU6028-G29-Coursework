"""Small, strict converter for the report's supported LaTeX to editable OMML."""
import re
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

SYMBOLS = {'mu':'μ','rho':'ρ','eta':'η','delta':'δ','pi':'π','sigma':'σ',
           'times':'×','pm':'±','le':'≤','ge':'≥','approx':'≈','infty':'∞',
           'int':'∫','propto':'∝','Omega':'Ω','square':'□','cdot':'·',
           'lVert':'‖','rVert':'‖'}

def el(tag, *children):
    x=OxmlElement('m:'+tag)
    for child in children: x.append(child)
    return x

def run(value, roman=False):
    x=el('r')
    pr=el('rPr')
    sty=el('sty');sty.set(qn('m:val'),'p' if roman else 'i');pr.append(sty)
    pr.append(el('nor'))
    x.append(pr)
    wp=OxmlElement('w:rPr')
    fonts=OxmlElement('w:rFonts')
    for tag in ['ascii','hAnsi','cs','eastAsia']: fonts.set(qn('w:'+tag),'Arial')
    wp.append(fonts)
    italic=OxmlElement('w:i');italic.set(qn('w:val'),'0' if roman else '1');wp.append(italic)
    x.append(wp)
    t=el('t');t.set(qn('xml:space'),'preserve');t.text=value;x.append(t)
    return x

class Parser:
    def __init__(self, source):
        self.tokens=re.findall(r'\\[A-Za-z]+|\\.|[0-9]+(?:\.[0-9]+)?|[A-Za-z]|[^\s]',source)
        self.i=0

    def take(self):
        token=self.tokens[self.i];self.i+=1;return token

    def group(self):
        if self.tokens[self.i]=='{':
            self.i+=1;nodes=self.sequence('}');assert self.take()=='}';return nodes
        return self.atom()

    def atom(self):
        token=self.take()
        if token=='{':
            nodes=self.sequence('}');assert self.take()=='}';return nodes
        if token=='\\frac':
            a=self.group();b=self.group();return [el('f',el('num',*a),el('den',*b))]
        if token=='\\sqrt':
            rp=el('radPr');hide=el('degHide');hide.set(qn('m:val'),'1');rp.append(hide)
            return [el('rad',rp,el('deg'),el('e',*self.group()))]
        if token in ['\\bar','\\hat']:
            pr=el('accPr');char=el('chr');char.set(qn('m:val'),'̅' if token=='\\bar' else '̂');pr.append(char)
            return [el('acc',pr,el('e',*self.group()))]
        if token in ['\\mathrm','\\text']:
            assert self.take()=='{'
            text=[]
            while self.tokens[self.i]!='}': text.append(self.take())
            assert self.take()=='}'
            return [run(''.join(text),True)]
        if token in ['\\left','\\right']: return self.atom()
        if token in ['\\,','\\;','\\ ']: return [run(' ',True)]
        if token in ['\\ln','\\exp','\\max','\\mean']:
            return [run(token[1:],True)]
        if token.startswith('\\'):
            name=token[1:]
            if name not in SYMBOLS: raise ValueError('Unsupported math command '+token)
            return [run(SYMBOLS[name],True)]
        return [run(token,roman=not token.isalpha())]

    def sequence(self, end=None):
        nodes=[]
        while self.i<len(self.tokens) and self.tokens[self.i]!=end:
            base=self.atom();sub=sup=None
            while self.i<len(self.tokens) and self.tokens[self.i] in ['_','^']:
                op=self.take();value=self.group()
                if op=='_': sub=value
                else: sup=value
            if sub is not None and sup is not None:
                base=[el('sSubSup',el('e',*base),el('sub',*sub),el('sup',*sup))]
            elif sub is not None: base=[el('sSub',el('e',*base),el('sub',*sub))]
            elif sup is not None: base=[el('sSup',el('e',*base),el('sup',*sup))]
            nodes.extend(base)
        return nodes

def equation(source):
    parser=Parser(source)
    result=el('oMath',*parser.sequence())
    assert parser.i==len(parser.tokens)
    return result

def rich_text(paragraph, text):
    for i,part in enumerate(re.split(r'\$(.*?)\$',text)):
        if i%2: paragraph._p.append(equation(part))
        else: paragraph.add_run(part)
