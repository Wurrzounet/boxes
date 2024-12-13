# Copyright (C) 2013-2014 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from boxes import *


class BookNode(Boxes):
    """Book Node"""

    ui_group = "Box"

    description = """"""

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser(x="54", y="90", h="137",sx="48:11:4:4.5:4.7", outside=False)

    def divider_left_right(self):
        t = self.thickness
        sx = self.sx
        h = self.h

        pos = -0.5 * t
        for i in sx:
            pos += i + t
            self.fingerHolesAt(pos, 0, h, 90)

    def render(self):

        x, y, h = self.x, self.y, self.h

        if self.outside:
            x = self.adjustSize(x)
            y = self.adjustSize(y)
            h = self.adjustSize(h)

        t = self.thickness

        self.rectangularWall(x, h, "FFFF", move="right", label="Back")
        self.rectangularWall(y, h, "FfFf", move="up",callback=[self.divider_left_right], label="Left")
        self.rectangularWall(y, h, "FfFf", callback=[self.divider_left_right], label="Right")
        self.rectangularWall(x, h, "FFFF", move="left up", label="Front")
        self.rectangularWall(x, y, "ffff", move="right", label="Top")
        self.rectangularWall(x, y, "ffff", move="up",label="Bottom")
        for i in range(len(self.sx)) :
            mo = "" if (i<1) else "right"
            self.rectangularWall(x, h, "efef", move="right", label="Wall "+str(i+1))



