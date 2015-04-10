# LinkSelect - selector of multiple targets for symlinks
#
# Copyright (C) 2015  Michal Belica <devel@beli.sk>
#
# This file is part of LinkSelect.
#
# LinkSelect is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LinkSelect is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LinkSelect.  If not, see <http://www.gnu.org/licenses/>.
#
import os
import re
import sys
from pprint import pprint
from pathlib import Path

class LinkSelect(object):
    def __init__(self, link, choices, base='',
            desc_from_content=False,
            desc_regexp=None,
            desc_parse_lines=1,
            refresh=True):
        self.link = link
        self.choices = choices
        self.base = base
        if desc_from_content and not desc_regexp:
            raise Exception('desc_from_content requires desc_regexp specified')
        self.desc_from_content=desc_from_content
        self.desc_cre=re.compile(desc_regexp) if desc_regexp else None
        self.desc_parse_lines=desc_parse_lines
        if refresh:
            self.refresh()
        else:
            self.basepath = None
            self.linkpath = None
            self.choices_list = None

    def refresh(self):
        self.basepath = Path(self.base)
        self.linkpath = Path(self.basepath / self.link)
        if self.linkpath.exists() and not self.linkpath.is_symlink():
            raise Exception('Link path exists, but is not a symlink ({}).'.format(self.linkpath))
        l = list()
        for p in self.basepath.glob(self.choices):
            l.append((self._find_desc(p), str(self._relative(p))))
        self.choices_list = l

    def get_current_choice(self):
        target = Path(os.readlink(str(self.linkpath)))
        if not target.is_absolute():
            target = self.basepath / target
        try:
            target = self._relative(target)
        except ValueError:
            raise Warning('Current link points outside base path.')
            return None, str(target)
        return self._indexof(target), str(target)

    def get_choices(self):
        return self.choices_list

    def set_link(self, choice):
        tmplink = self.linkpath.parent / ('.' + self.linkpath.name + '.' + str(os.getpid()))
        tmplink.symlink_to(choice)
        tmplink.replace(self.linkpath)

    def _indexof(self, path):
        for i, v in enumerate(self.choices_list):
            d, p = v
            if str(path) == p:
                return i
        return None

    def _find_desc(self, path):
        if self.desc_from_content:
            with open(str(path), 'r') as f:
                for i in range(self.desc_parse_lines):
                    l = f.readline()
                    m = self.desc_cre.search(l)
                    if m:
                        return m.group(1)
        relpath = self._relative(path)
        if self.desc_cre:
            m = self.desc_cre.search(str(relpath))
            if m:
                return m.group(1)
        return str(relpath)

    def _relative(self, path):
        return path.relative_to(self.basepath)

