import os
import re

import HTMLParser

__all__ = ['replace_newlines', 'preserve_quotes',
           'remove_meta', 'unescape', 'sanitize']

parser = HTMLParser.HTMLParser()

nlbr_pattern = re.compile(r'\<br( \/)?\>')
quot_pattern = re.compile(r'\<span class=\"quote\"\>(.+?)\<\/span\>')
code_pattern = re.compile(r'\<pre class=\"prettyprint\"\>(.+?)\<\/pre\>')
html_pattern = re.compile(r'\<(\w+)( [^\>]+)?\>.+?\<\/\1\>')

def get_first_group (match):
    """
    Retrieves the first group from the match object.
    """
    return match.group(1)

def replace_newlines (s):
    """
    Replaces <br> and <br /> tags with newlines.
    """
    return nlbr_pattern.sub(os.linesep, s)

def preserve_quotes (s):
    """
    Removes HTML tags around greentext.
    """
    return quot_pattern.sub(get_first_group, s)

def preserve_code (s):
    """
    Removes HTML tags around code.
    """
    return code_pattern.sub(get_first_group, s)

def remove_meta (s):
    """
    Removes matching HTML tags and everything in between them.
    """
    return html_pattern.sub('', s)

def unescape (s):
    """
    Replaces HTML entities with the corresponding character.
    """
    return parser.unescape(s)

def sanitize (s):
    """
    Removes HTML tags, replaces HTML entities and unescapes the text so that
    only human generated content remains.
    """
    s = preserve_quotes(s)
    s = preserve_code(s)
    s = replace_newlines(s)
    s = remove_meta(s)

    return unescape(s)
