#!/usr/bin/env python3
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

from __future__ import annotations

import math
from functools import partial

from boxes import Boxes, edges, boolarg, lids

class ComanderBox(Boxes):
    """Deck box for a comander box for magic tgc"""

    description = """
BetaVersion
"""

    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings, extra_length=0.2)

        self.buildArgParser(h=104, outside=False, sx="70*1", y="60")  # , thickness=0.5)


        self.argparser.add_argument(
            "--ratio_front",
            type=float,
            default=0.6,
            help="ratio for the bottom part in the front (in proportion of the height)",
        )
        self.argparser.add_argument(
            "--ratio_back",
            type=float,
            default=0.6,
            help="ratio for the bottom part  in the back (in proportion of the height)",
        )

    def render(self):

        side_walls_number = len(self.sx)
        if side_walls_number == 0:
            raise ValueError("You need at least one side wall to generate this tray")

        # We need to adjust size if outside
        if self.outside:
            self.h -= self.thickness
            self.y -= self.thickness
            self.sx = self.adjustSize(self.sx)

        self.ctx.save()

        # Facing walls (outer) with finger holes to support side walls
        facing_wall_length = sum(self.sx) + self.get_side_thickness() * (len(self.sx) - 1)
        bottom_edge = ("F")
        upper_edge = ("e")
        for i in range(2):
            for _ in range(2):
                self.rectangularWall(
                    facing_wall_length,
                    self.h * (self.ratio_front if not _ else 1-self.ratio_front),
                    [
                        bottom_edge if (not _) else upper_edge,
                        "F",
                        bottom_edge if _ else upper_edge,
                        "F",
                    ],
                    callback=([partial(self.generate_finger_holes, self.h * self.ratio_front)] if not _ else None),
                    move="up", label=("bottom" if not _ else "upper")+" "+("Front" if i else "Back"),
                )
        # Side walls
        side_wall_length = self.y
        for i in range(2):
            for _ in range(2):
                self.rectangularWall(
                    side_wall_length,
                    self.h * (self.ratio_front if _ else 1-self.ratio_front),
                    [
                        bottom_edge if (not _) else upper_edge,
                        "f",
                        bottom_edge if _ else upper_edge,
                        "f"
                    ],
                    move="up", label=("bottom" if _ else "upper")+" "+("right" if i else "left"),
                )


        self.lid(facing_wall_length, side_wall_length)

        # Switch to right side of the file
        self.ctx.restore()
        self.rectangularWall(
            max(facing_wall_length, side_wall_length), self.h, "ffff", move="right only", label="invisible"
        )

        self.rectangularWall(
            facing_wall_length,
            side_wall_length,
            [
                "f",
                "f",
                "f",
                "f",
            ],
            callback=[partial(self.generate_finger_holes, side_wall_length)],
            move="up", label="Bottom",
        )
        self.rectangularWall(
            facing_wall_length,
            side_wall_length,
            [
                "f",
                "f",
                "f",
                "f",
            ],
            move="up", label="UP",
        )
        for _ in range(side_walls_number-1):
            hauteur = self.h * self.ratio_front
            self.rectangularWall(
                side_wall_length, hauteur, ["f","f", "e", "f"], move="up", label="centralpiece " + str(_ + 1)
            )

        if self.debug:
            debug_info = ["Debug"]

            debug_info.append(
                "Face_edge_inner_lengths:{0}".format(
                    str.join("|", ["{0:.2f}".format(e) for e in self.sx])
                )
            )
            debug_info.append("Tray_height:{0:.2f}".format(self.h))
            debug_info.append(
                "Content_height:{0:.2f}".format(
                    self.h / math.cos(math.radians(self.Slot_angle))
                )
            )
            self.text(str.join("\n", debug_info), x=5, y=5, align="bottom left")

    def get_side_thickness(self):
        return self.thickness

    def generate_finger_holes(self, length):
        posx = self.get_side_thickness()*0.5
        for x in self.sx[:-1]:
            posx += x
            self.fingerHolesAt(posx, 0, length)

class Memoizer(dict):
    def __init__(self, computation) -> None:
        self.computation = computation

    def __missing__(self, key):
        res = self[key] = self.computation(key)
        return res