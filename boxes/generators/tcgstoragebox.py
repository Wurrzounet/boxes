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


class SlotSettings(edges.Settings):
    """Settings for Divider Slots

    Values:

    * absolute
      * depth : 20 : depth of the slot in mm
      * angle : 0 : angle at which slots are generated, in degrees. 0° is vertical.
      * radius : 2 : radius of the slot entrance in mm
      * extra_slack : 0.2 : extra slack (in addition to thickness and kerf) to help insert dividers in mm"""

    absolute_params = {
        "depth": 10,
        "angle": 0,
        "radius": 1.5,
        "extra_slack": -3.2,
    }


class TCGStorageBox(Boxes):
    """One big box for storing cards from trading card games or other deckbuilding game. (The picture sample is one I made for aeon's end"""

    description = """
Adding '0:' at the start of the sy parameter adds a slot at the very back. Adding ':0' at the end of sy adds a slot meeting the bottom at the very front. This is especially useful if slot angle is set above zero.

There are 4 different sets of dividers rendered:

* With asymmetric tabs so the tabs fit on top of each other
* With tabs of half wall thickness that can go side by side
* With tabs of a full wall thickness
* One single divider spanning across all columns

You will likely need to cut each of the dividers you want multiple times.

Some reworking is still to be made for allowing a different thickness for the inside wall
For estetique improuvement we need to allow the possibilitty to made a "outside" box
"""

    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings, extra_length=0.2)

        self.buildArgParser(h=104, outside=False, sx="70*4", sy="25*14")  # , thickness=0.5)

        self.addSettingsArgs(SlotSettings)
        self.argparser.add_argument(
            "--ratio",
            type=float,
            default=0.6,
            help="ratio for the bottom part (in proportion of the height)",
        )
        self.argparser.add_argument(
            "--left_wall",
            type=boolarg,
            default=True,
            help="generate an additional wall on the left side for divider",
        )

        self.argparser.add_argument(
            "--right_wall",
            type=boolarg,
            default=True,
            help="generate an additional wall on the right side for divider",
        )

    def render(self):

        side_walls_number = len(self.sx) - 1 + sum([self.left_wall, self.right_wall])
        if side_walls_number == 0:
            raise ValueError("You need at least one side wall to generate this tray")

        # We need to adjust height before slot generation
        if self.outside:
            self.h -= self.thickness
        else:
            # If the parameter 'h' is the inner height of the content itself,
            # then the actual tray height needs to be adjusted with the angle
            self.h = self.h * math.cos(math.radians(self.Slot_angle))

        slot_descriptions = SlotDescriptionsGenerator().generate_all_same_angles(
            self.sy,
            self.thickness,
            self.Slot_extra_slack,
            self.Slot_depth,
            self.h,
            self.Slot_angle,
            self.Slot_radius,
        )

        # If measures are outside, we need to readjust slots afterwards
        if self.outside:
            self.sx = self.adjustSize(self.sx, self.left_wall, self.right_wall)
            side_wall_target_length = sum(self.sy) - 2 * self.thickness
            slot_descriptions.adjust_to_target_length(side_wall_target_length)

        self.ctx.save()

        # Facing walls (outer) with finger holes to support side walls
        facing_wall_length = sum(self.sx) + self.get_side_thickness() * (len(self.sx) + 1)#+self.thickness*2
        side_edge = lambda with_wall: "F" if with_wall else "e"
        bottom_edge = ("F")
        upper_edge = ("e")
        for i in range(2):
            for _ in range(2):
                self.rectangularWall(
                    facing_wall_length,
                    self.h * (self.ratio if not _ else 1-self.ratio),
                    [
                        bottom_edge if (not _) else upper_edge,
                        side_edge(self.right_wall),
                        bottom_edge if _ else upper_edge,
                        side_edge(self.left_wall),
                    ],
                    callback=([partial(self.generate_finger_holes, self.h * self.ratio)] if not _ else None),
                    move="up", label=("bottom" if not _ else "upper")+" "+("Front" if i else "Back"),
                )
        # Side walls (outer & inner) with slots to support dividers
        side_wall_length = slot_descriptions.total_length()
        for i in range(2):
            for _ in range(2):
                self.rectangularWall(
                    side_wall_length,
                    self.h * (self.ratio if _ else 1-self.ratio),
                    [
                        bottom_edge if (not _) else upper_edge,
                        "f",
                        bottom_edge if _ else upper_edge,
                        "f"
                    ],
                    move="up", label=("bottom" if _ else "upper")+" "+("right" if i else "left"),
                )


        for _ in range(side_walls_number):
            if _ < side_walls_number - (len(self.sx) - 1):
                be = "e"
            else:
                be = "f"
            se = DividerSlotsEdge(self, slot_descriptions.descriptions)
            self.rectangularWall(
                side_wall_length, self.h * self.ratio*1.1, [be, be, se, be], move="up", label="Sidepiece " + str(_ + 1)
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
                "f" if self.right_wall else "e",
                "f",
                "f" if self.left_wall else "e",
            ],
            callback=[partial(self.generate_finger_holes, side_wall_length)],
            move="up", label="Bottom",
        )
        self.rectangularWall(
            facing_wall_length,
            side_wall_length,
            [
                "f",
                "f" if self.right_wall else "e",
                "f",
                "f" if self.left_wall else "e",
            ],
            move="up", label="UP",
        )
        if self.debug:
            debug_info = ["Debug"]
            debug_info.append(
                "Slot_edge_outer_length:{0:.2f}".format(
                    slot_descriptions.total_length() + 2 * self.thickness
                )
            )
            debug_info.append(
                "Slot_edge_inner_lengths:{0}".format(
                    str.join(
                        "|",
                        [
                            "{0:.2f}".format(e.useful_length())
                            for e in slot_descriptions.get_straight_edges()
                        ],
                    )
                )
            )
            debug_info.append(
                "Face_edge_outer_length:{0:.2f}".format(
                    facing_wall_length
                    + self.thickness * sum([self.left_wall, self.right_wall])
                )
            )
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
        return self.thickness * self.FingerJoint_width

    def generate_finger_holes(self, length):
        posx = self.get_side_thickness()*0.5
        for x in self.sx[:-1]:
            posx += x + self.get_side_thickness()
            self.fingerHolesAt(posx, 0, length)

    def generate_divider(
            self, widths, height, move,
            first_tab_width=0, second_tab_width=0,
            asymmetric_tabs=None):
        total_width = sum(widths) + (len(widths) - 1) * self.thickness + first_tab_width + second_tab_width

        if self.move(total_width, height, move, True):
            return

        play = self.Divider_play
        left_tab_height = right_tab_height = self.Slot_depth
        if asymmetric_tabs:
            left_tab_height = left_tab_height * asymmetric_tabs - play
            right_tab_height = right_tab_height * (1 - asymmetric_tabs)

        # Upper: first tab width
        if asymmetric_tabs:
            self.moveTo(first_tab_width - play)
        else:
            self.edge(first_tab_width - play)
        # Upper edge with a finger notch
        for nr, width in enumerate(widths):
            if nr > 0:
                self.edge(self.thickness)
            DividerNotchesEdge(
                self,
                [width],
            )(width)

        self.polyline(
            # Upper: second tab width if needed
            second_tab_width - play,
            # First side, with tab depth only if there is 2 walls
            90,
            left_tab_height,
            90,
            second_tab_width,
            -90,
            height - left_tab_height,
            90,
        )
        # Lower edge
        for width in reversed(widths[1:]):
            self.polyline(
                width - 2 * play,
                90,
                height - self.Slot_depth,
                -90,
                self.thickness + 2 * play,
                -90,
                height - self.Slot_depth,
                90,
            )

        self.polyline(
            # Second side tab
            widths[0] - 2 * play,
            90,
            height - self.Slot_depth,
            -90,
            first_tab_width,
            90,
            right_tab_height,
            90
        )
        if asymmetric_tabs:
            self.polyline(
                first_tab_width - play,
                -90,
                self.Slot_depth - right_tab_height,
                90
            )

        # Move for next piece
        self.move(total_width, height, move, label="Divider")


class SlottedEdgeDescriptions:
    def __init__(self) -> None:
        self.descriptions: list[str] = []

    def add(self, description: str) -> None:
        self.descriptions.append(description)

    def get_straight_edges(self):
        return [x for x in self.descriptions if isinstance(x, StraightEdgeDescription)]

    def get_last_edge(self):
        return self.descriptions[-1]

    def adjust_to_target_length(self, target_length):
        actual_length = sum([d.tracing_length() for d in self.descriptions])
        compensation = actual_length - target_length

        compensation_ratio = compensation / sum(
            [d.asked_length for d in self.get_straight_edges()]
        )

        for edge in self.get_straight_edges():
            edge.outside_ratio = 1 - compensation_ratio

    def total_length(self):
        return sum([x.tracing_length() for x in self.descriptions])


class StraightEdgeDescription:
    def __init__(
            self,
            asked_length,
            round_edge_compensation=0,
            outside_ratio=1,
            angle_compensation=0,
    ) -> None:
        self.asked_length = asked_length
        self.round_edge_compensation = round_edge_compensation
        self.outside_ratio = outside_ratio
        self.angle_compensation = angle_compensation

    def __repr__(self) -> str:
        return (
            "StraightEdgeDescription({0}, round_edge_compensation={1}, angle_compensation={2}, outside_ratio={3})"
        ).format(
            self.asked_length,
            self.round_edge_compensation,
            self.angle_compensation,
            self.outside_ratio,
        )

    def tracing_length(self):
        """
        How much length should take tracing this straight edge
        """
        return (
                (self.asked_length * self.outside_ratio)
                - self.round_edge_compensation
                + self.angle_compensation
        )

    def useful_length(self):
        """
        Part of the length which might be used by the content of the tray
        """
        return self.asked_length * self.outside_ratio


class Memoizer(dict):
    def __init__(self, computation) -> None:
        self.computation = computation

    def __missing__(self, key):
        res = self[key] = self.computation(key)
        return res


class SlotDescription:
    _div_by_cos_cache = Memoizer(lambda a: 1 / math.cos(math.radians(a)))
    _tan_cache = Memoizer(lambda a: math.tan(math.radians(a)))

    def __init__(
            self, width, depth=20, angle=0, radius=0, start_radius=None, end_radius=None
    ) -> None:
        self.depth = depth
        self.width = width
        self.start_radius = radius if start_radius is None else start_radius
        self.end_radius = radius if end_radius is None else end_radius
        self.angle = angle

    def __repr__(self) -> str:
        return "SlotDescription({0}, depth={1}, angle={2}, start_radius={3}, end_radius={4})".format(
            self.width, self.depth, self.angle, self.start_radius, self.end_radius
        )

    def _div_by_cos(self):
        return SlotDescription._div_by_cos_cache[self.angle]

    def _tan(self):
        return SlotDescription._tan_cache[self.angle]

    def angle_corrected_width(self):
        """
        returns how much width is the slot when measured horizontally, since the angle makes it bigger.
        It's the same as the slot entrance width when radius is 0°.
        """
        return self.width * self._div_by_cos()

    def round_edge_start_correction(self):
        """
        returns by how much we need to stop tracing our straight lines at the start of the slot
        in order to do a curve line instead
        """
        return self.start_radius * (self._div_by_cos() - self._tan())

    def round_edge_end_correction(self):
        """
        returns by how much we need to stop tracing our straight lines at the end of the slot
        in order to do a curve line instead
        """
        return self.end_radius * (self._div_by_cos() + self._tan())

    def _depth_angle_correction(self):
        """
        The angle makes one side of the slot deeper than the other.
        """
        extra_depth = self.width * self._tan()
        return extra_depth

    def corrected_start_depth(self):
        """
        Returns the depth of the straight part of the slot starting side
        """
        extra_depth = self._depth_angle_correction()
        return self.depth + max(0, extra_depth) - self.round_edge_start_correction()

    def corrected_end_depth(self):
        """
        Returns the depth of the straight part of the slot ending side
        """
        extra_depth = self._depth_angle_correction()
        return self.depth + max(0, -extra_depth) - self.round_edge_end_correction()

    def tracing_length(self):
        """
        How much length this slot takes on an edge
        """
        return (
                self.round_edge_start_correction()
                + self.angle_corrected_width()
                + self.round_edge_end_correction()
        )


class SlotDescriptionsGenerator:
    def generate_all_same_angles(
            self, sections, thickness, extra_slack, depth, height, angle, radius=2,
    ):
        width = thickness + extra_slack

        descriptions = SlottedEdgeDescriptions()

        # Special case: if first slot start at 0, then radius is 0
        first_correction = 0
        current_section = 0
        if sections[0] == 0:
            slot = SlotDescription(
                width, depth=depth, angle=angle, start_radius=0, end_radius=radius,
            )
            descriptions.add(slot)
            first_correction = slot.round_edge_end_correction()
            current_section += 1

        first_length = sections[current_section]
        current_section += 1
        descriptions.add(
            StraightEdgeDescription(
                first_length, round_edge_compensation=first_correction
            )
        )

        for l in sections[current_section:]:
            slot = SlotDescription(width, depth=depth, angle=angle, radius=radius, )

            # Fix previous edge length
            previous_edge = descriptions.get_last_edge()
            previous_edge.round_edge_compensation += slot.round_edge_start_correction()

            # Add this slot
            descriptions.add(slot)

            # Add the straight edge after this slot
            descriptions.add(
                StraightEdgeDescription(l, slot.round_edge_end_correction())
            )

        # We need to add extra space for the divider (or the actual content)
        # to slide all the way down to the bottom of the tray in spite of walls
        end_length = height * math.tan(math.radians(angle))
        descriptions.get_last_edge().angle_compensation += end_length

        return descriptions


class DividerNotchesEdge(edges.BaseEdge):
    """Edge with multiple notches for easier access to dividers"""

    description = "Edge with multiple notches for easier access to dividers"

    def __init__(self, boxes, sx) -> None:

        super().__init__(boxes, None)

        self.sx = sx

    def __call__(self, _, **kw):
        first = True
        for width in self.sx:
            if first:
                first = False
            else:
                self.edge(self.thickness)
            # self.edge_with_notch(width)

    def edge_with_notch(self, width):
        # width (with notch if possible)
        upper_third = (
                              width - 2 * self.Notch_upper_radius - 2 * self.Notch_lower_radius
                      ) / 3
        if upper_third > 0:
            straightHeight = (
                    self.Notch_depth - self.Notch_upper_radius - self.Notch_lower_radius
            )
            self.polyline(
                upper_third,
                (90, self.Notch_upper_radius),
                straightHeight,
                (-90, self.Notch_lower_radius),
                upper_third,
                (-90, self.Notch_lower_radius),
                straightHeight,
                (90, self.Notch_upper_radius),
                upper_third,
            )
        else:
            # if there isn't enough room for the radius, we don't use it
            self.edge(width)


class DividerSlotsEdge(edges.BaseEdge):
    """Edge with multiple angled rounded slots for dividers"""

    description = "Edge with multiple angled rounded slots for dividers"

    def __init__(self, boxes, descriptions) -> None:

        super().__init__(boxes, None)

        self.descriptions = descriptions

    def __call__(self, length, **kw):

        self.ctx.save()

        for description in self.descriptions:
            if isinstance(description, SlotDescription):
                self.do_slot(description)
            elif isinstance(description, StraightEdgeDescription):
                self.do_straight_edge(description)

        # rounding errors might accumulate :
        # restore context and redo the move straight
        self.ctx.restore()
        self.moveTo(length)

    def do_straight_edge(self, straight_edge):
        self.edge(straight_edge.tracing_length())

    def do_slot(self, slot):
        self.ctx.save()

        self.polyline(
            0,
            (90 - slot.angle, slot.start_radius),
            slot.corrected_start_depth(),
            -90,
            slot.width,
            -90,
            slot.corrected_end_depth(),
            (90 + slot.angle, slot.end_radius),
        )

        # rounding errors might accumulate :
        # restore context and redo the move straight
        self.ctx.restore()
        self.moveTo(slot.tracing_length())