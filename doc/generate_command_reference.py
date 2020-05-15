#!/usr/bin/env python

import re
import sys
import os.path
from textwrap import TextWrapper
import urllib.request
try:
    from lxml import etree
except ImportError:
    sys.stderr.write("Please install lxml to run this script.")
    sys.exit(1)

DEPRECATED_COMMANDS = []
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


def get_text(elements, itemize=False):
    paragraphs = []
    highlight_elements = ['varname', 'parameter']
    strip_elements = [
            'returnvalue',
            'command',
            'link',
            'footnote',
            'simpara',
            'footnoteref',
            'function'
    ] + highlight_elements
    for element in elements:
        # put "Since MPD version..." in paranthese
        etree.strip_tags(element, "application")
        for e in element.xpath("footnote/simpara"):
            e.text = "(" + e.text.strip() + ")"

        for e in element.xpath("|".join(highlight_elements)):
            e.text = "*" + e.text.strip() + "*"
        etree.strip_tags(element, *strip_elements)
        if itemize:
            initial_indent = "    * "
            subsequent_indent = "      "
        else:
            initial_indent = "    "
            subsequent_indent = "    "
        wrapper = TextWrapper(subsequent_indent=subsequent_indent,
                              initial_indent=initial_indent)
        text = element.text.replace("\n", " ").strip()
        text = re.subn(r'\s+', ' ', text)[0]
        paragraphs.append(wrapper.fill(text))
    return "\n\n".join(paragraphs)


def main(url):
    header_file = os.path.join(SCRIPT_PATH, "commands_header.txt")
    with open(header_file, 'r') as f:
        print(f.read())

    r = urllib.request.urlopen(url)
    tree = etree.parse(r)
    chapter = tree.xpath('/book/chapter[@id="command_reference"]')[0]
    for section in chapter.xpath("section"):
        title = section.xpath("title")[0].text
        print(title)
        print(len(title) * "-")

        print(get_text(section.xpath("para")))
        print("")

        for entry in section.xpath("variablelist/varlistentry"):
            cmd = entry.xpath("term/cmdsynopsis/command")[0].text
            if cmd in DEPRECATED_COMMANDS:
                continue
            subcommand = ""
            args = ""
            begin_optional = False
            first_argument = True

            for arg in entry.xpath("term/cmdsynopsis/arg"):
                choice = arg.attrib.get("choice", None)
                if choice == "opt" and not begin_optional:
                    begin_optional = True
                    args += "["
                if args != "" and args != "[":
                    args += ", "
                replaceables = arg.xpath("replaceable")
                if len(replaceables) > 0:
                    for replaceable in replaceables:
                        args += replaceable.text.lower()
                elif first_argument:
                    subcommand = arg.text
                else:
                    args += '"{}"'.format(arg.text)
                first_argument = False
            if begin_optional:
                args += "]"
            if subcommand != "":
                cmd += "_" + subcommand
            print(".. function:: MPDClient." + cmd + "(" + args + ")")
            description = get_text(entry.xpath("listitem/para"))
            description = re.sub(r':$', r'::', description, flags=re.MULTILINE)

            print("\n")
            print(description)
            print("\n")

            for screen in entry.xpath("listitem/screen | listitem/programlisting"):
                for line in screen.text.split("\n"):
                    print("        " + line)
            for item in entry.xpath("listitem/itemizedlist/listitem"):
                print(get_text(item.xpath("para"), itemize=True))
                print("\n")

if __name__ == "__main__":
    url = "https://raw.githubusercontent.com/MusicPlayerDaemon/MPD/master/doc/protocol.xml"
    if len(sys.argv) > 1:
        url += "?id=release-" + sys.argv[1]
    main(url)
