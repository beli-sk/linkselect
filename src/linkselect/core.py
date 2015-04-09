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
import sys
from pathlib import Path

class LinkSelect(object):
    def __init__(self, link, choices, base='', refresh=True):
        self.link = link
        self.choices = choices
        self.base = base
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
        self.choices_list = list(self.basepath.glob(self.choices))

    def get_current_choice(self):
        if self.linkpath.exists():
            target = Path(os.readlink(str(self.linkpath)))
            if not target.is_absolute():
                target = self.basepath / target
            try:
                target = self._relative(target)
            except ValueError:
                raise Warning('Current link points outside base path.')
                return str(target)
            return str(target)

    def get_choices(self):
        return (str(self._relative(x)) for x in self.choices_list)

    def set_link(self, choice):
        tmplink = self.linkpath.parent / ('.' + self.linkpath.name + '.' + str(os.getpid()))
        tmplink.symlink_to(choice)
        tmplink.replace(self.linkpath)

    def _relative(self, path):
        return path.relative_to(self.basepath)

