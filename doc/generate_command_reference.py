#!/usr/bin/env python

import re, sys
import os.path
try:
    from lxml import etree
except ImportError:
    sys.stderr.write("Please install lxml to run this script.")
    sys.exit(1)

url = "http://git.musicpd.org/cgit/cirrus/mpd.git/plain/doc/protocol.xml"

if len(sys.argv) > 1:
    url += "?id=release-" + sys.argv[1]

DIR = os.path.dirname(os.path.realpath(__file__))
header_file = os.path.join(DIR, "commands_header.txt")

with open(header_file, 'r') as f:
    print(f.read())

tree = etree.parse(url)
chapter = tree.xpath('/book/chapter/title[text()= "Command reference"]/..')[0]
for section in chapter.xpath("section"):
    title = section.xpath("title")[0].text
    print(title)
    print(len(title) * "-")

    paragraphs = []
    for paragraph in section.xpath("para"):
        etree.strip_tags(paragraph, 'varname', 'command', 'parameter')
        text = paragraph.text.rstrip()
        paragraphs.append(text)
    print("\n".join(paragraphs))
    print()

    for entry in section.xpath("variablelist/varlistentry"):
        cmd = entry.xpath("term/cmdsynopsis/command")[0].text
        args = ""
        begin_optional=False
        for arg in entry.xpath("term/cmdsynopsis/arg"):
            choice = arg.attrib.get("choice", None)
            if choice == "opt" and not begin_optional:
                begin_optional = True
                args += "["
            if args != "" and args != "[":
                args += ", "
            for text in arg.xpath("./*/text()"):
                args += text.lower()
        if begin_optional:
            args += "]"
        print(".. function:: MPDClient." + cmd + "(" + args + ")")
        lines = []
        for para in entry.xpath("listitem/para"):
            etree.strip_tags(para, 'varname', 'command', 'parameter')
            t = [t.rstrip() for t in para.xpath("text()")]
            lines.append(" ".join(t))
        description = "\n".join(lines)
        description = re.sub(r':$',r'::', description,flags=re.MULTILINE)

        print(description)
        print("\n")
        for screen in entry.xpath("listitem/screen | listitem/programlisting"):
            for line in screen.text.split("\n"):
                print("                " + line)
