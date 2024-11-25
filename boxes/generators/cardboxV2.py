# Copyright (C) 2013-2014 Florian Festi
# Copyright (C) 2018 jens persson <jens@persson.cx>
# Copyright (C) 2023 Manuel Lohoff
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
import math

from docutils.nodes import label

from boxes import BoolArg, Boxes, edges

class FingerHoleEdgeSettings(edges.Settings):
    """Settings for FingerHoleEdge"""
    absolute_params = {
        "wallheight": 0,
        "fingerholedepth": 0,
    }


class FingerHoleEdge(edges.BaseEdge):
    """An edge with room to get your fingers around cards"""
    def __call__(self, length, **kw):
        depth = self.settings.fingerholedepth-10
        self.edge(length/2-10, tabs=2)
        self.corner(90)
        self.edge(depth, tabs=2)
        self.corner(-180, 10)
        self.edge(depth, tabs=2)
        self.corner(90)
        self.edge(length/2-10, tabs=2)

class BoxBottomFrontEdge(edges.BaseEdge):
    char = 'b'
    def __call__(self, length, **kw):

        y = self.boxdepth
        sx = self.sx
        bottom = max(self.settings.sx) / 3

        f = 0.4
        a1 = math.degrees(math.atan(f/(1-f)))
        a2 = 45 + a1
        for i, l in enumerate(self.settings.sx):
            self.edges["f"](bottom)
            self.corner(90)
            self.edge(0)
            self.corner(-180, bottom/2)
            self.edge(0)
            self.corner(90)
            self.edges["f"](bottom)
            if i < len(self.settings.sx)-1:
                self.edges["e"](self.thickness)

    def margin(self) -> float:
        return max(self.settings.sx) * 0.4

class CardBoxV2(Boxes):
    """Box for storage of playing cards, with versatile options"""
    ui_group = "Box"

    description = """
### Description
Versatile Box for Storage of playing cards. Multiple different styles of storage are supported, e.g. a flat storage or a trading card deck box style storage. See images for ideas.

#### Building instructions
Place inner walls on floor first (if any). Then add the outer walls. Glue the two walls without finger joins to the inside of the side walls. Make sure there is no squeeze out on top, as this is going to form the rail for the lid.

Add the top of the rails to the sides (front open) or to the back and front (right side open) and the grip rail to the lid.
Details of the lid and rails
![Details](static/samples/CardBox-detail.jpg)
Whole box (early version still missing grip rail on the lid):
"""

    def generatesection(self,width):

        result = []
        for i in range(self.number_case):
            result.append(float(width))
        return result


    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser(y=72, h=20, outside=False, sx="52*3")

        self.argparser.add_argument(
            "--case_size", action="store", type=str, default="custom",
            choices=['tarot','poker', 'minipoker', 'custom'],
            help="size of the card to store, y and x wont be used. Poker : 63.5*89 mm cards.  minipoker : 45*68mm cards")
        self.argparser.add_argument(
            "--card_position", action="store", type=str, default="vertical",
            choices=['vertical', 'horizontal'],
            help="position of the card in the case. Vertical mean that de short edge of the card will be in the bottom size. Not used for custom card size")
        self.argparser.add_argument(
            "--sleeved_cards", action="store", type=BoolArg(), default=True,
            help="Add a small gap the case, to allow to put sleeved card in it (add 4mm for the width and 6 mm for the height of the card. Not used for custom card size"
        )
        self.argparser.add_argument(
            "--number_case", action="store", type=int, default=3,
            help="Number of case.")
        self.argparser.add_argument(
            "--add_lid", action="store", type=BoolArg(), default=False,
            help="Add a lid to help to keep cards in place."
        )
        self.argparser.add_argument(
            "--lid_play", action="store", type=float, default=0.15,
            help="Add a play between lid and insert. Multiple of thickness"
        )
        self.argparser.add_argument(
            "--fingerhole", action="store", type=str, default="custom",
            choices=['regular', 'deep', 'custom'],
            help="Depth of cutout to grab the cards")
        self.argparser.add_argument(
            "--fingerhole_depth", action="store", type=float, default=10,
            help="Depth of cutout if fingerhole is set to 'custom'. Disabled otherwise.")


    @property
    def fingerholedepth(self):
        if self.fingerhole == 'custom':
            return self.fingerhole_depth
        elif self.fingerhole == 'regular':
            a = self.h/4
            if a < 35:
                return a
            else:
                return 35
        elif self.fingerhole == 'deep':
            return self.h-self.thickness-10

    #inner dimensions of surrounding box (disregarding inlays)
    @property
    def boxhight(self):
        if self.outside:
            return self.h - 3 * self.thickness
        return self.h
    @property
    def boxwidth(self):
        return (len(self.sx)  -1) * self.thickness + sum(self.sx)
    @property
    def boxdepth(self):
        if self.outside:
            return self.y - 2 * self.thickness
        return self.y

    def divider_bottom(self):
        t = self.thickness
        sx = self.sx
        y = self.boxdepth

        pos =  -0.5 * t
        for i in sx[:-1]:
            pos += i + t
            self.fingerHolesAt(pos, 0, y, 90)

    def yHoles(self):
        posy = -0.5 * self.thickness
        for y in reversed(self.sx[1:]):
            posy += y + self.thickness
            self.fingerHolesAt(posy, 0, self.boxhight)

    def divider_back_and_front(self):
        t = self.thickness
        sx = self.sx
        y = self.boxhight

        pos =  -0.5 * t
        for i in sx[:-1]:
            pos += i + t
            self.fingerHolesAt(pos, 0, y, 90)

    def divider_front(self):
        t = self.thickness
        y = self.boxhight

        pos = 0.5* t + max(self.sx) / 3
        self.fingerHolesAt(pos, t, y, 90)

    def getcardlenght(self,position):
        cardlen = 0
        # taille supplémentaire case en fonction de la presence ou non de sleeves
        vert_up = 8 if(self.sleeved_cards) else 3
        horiz_up = 4 if (self.sleeved_cards) else 3
        match self.case_size:
            case 'poker':
                if self.card_position == position:
                    cardlen=89 +vert_up
                else:
                    cardlen =63.5+horiz_up
            case 'minipoker':
                if self.card_position == position:
                    cardlen=68+vert_up
                else:
                    cardlen =45+horiz_up
            case 'tarot':
                if self.card_position == position:
                    cardlen = 120 + vert_up
                else:
                    cardlen = 70 + horiz_up
        return cardlen

    def render(self):
        if(self.case_size != 'custom'):
            self.y = self.getcardlenght('vertical')
            self.sx = self.generatesection(self.getcardlenght('horizontal'))

        self.addPart(BoxBottomFrontEdge(self, self))

        t = 0
        y = self.boxdepth
        h = self.boxhight
        sx = self.sx
        x = self.boxwidth

        s = FingerHoleEdgeSettings(thickness=t, wallheight=h, fingerholedepth=self.fingerholedepth)
        p = FingerHoleEdge(self, s)
        p.char = "A"
        self.addPart(p)

        with self.saved_context():
            self.rectangularWall(x, h + t , [
                "F",
                "F",
                "e",
                "F",
            ],
             callback=[self.divider_back_and_front],
             move="right",
             label="Back")

        self.rectangularWall(x, h + t, "EEEE", move="up only")

        with self.saved_context():
            self.rectangularWall(y, h + t, [
                "F",
                "f",
                "e",
                "f",
            ], move="right", label="Outer Side Left")
            self.rectangularWall(y, h + t,[
                "F",
                "f",
                "e",
                "f",
            ]

            , move="right", label="Outer Side Right")
        self.rectangularWall(y, h + t, "fFfF", move="up only")

        with self.saved_context():
            self.rectangularWall(x, y, "ffbf", callback=[self.divider_bottom],
                                 move="right", label="Bottom")
        self.rectangularWall(x, y*1.1, "eEEE", move="up only")

        for i in range(len(sx) - 1):
            self.rectangularWall(h, y, "fAff", move="right", label="Divider")

        #Ajout de cache avant, construit comme un rectangle avec un angle coupé,
        #angle haut de la piece
        angle=50
        #hauteur de la coupe
        hf=h*0.5
        #"faux" bas, utilisé pour l'encoche,
        falseBottom= max(self.sx) / 3
        # vrai bas total
        bottom=falseBottom+self.thickness

        hauteur=h+self.thickness
        panel = min((hauteur-hf)/math.cos(math.radians(90-angle)),
                    bottom/math.cos(math.radians(angle)))
        top = bottom - panel * math.cos(math.radians(angle))
        # ordre des coté, construit dans le sens trigonometrique.
        borders = [self.thickness,0,falseBottom, 90, hf, 90 - angle, panel, angle, top,
                       90, h,0,self.thickness , 90]

        self.polygonWall(borders, move="right",edge="eFeeeFe", label='front left')
        borders = [falseBottom,0,self.thickness, 90,self.thickness,0,h,90,top,angle,panel,90-angle,hf,90]
        self.polygonWall(borders, move="right", edge="FeeFeee", label='front right')
        borders = [falseBottom, 0, self.thickness,0, falseBottom, 90, hf,90 - angle,panel,angle,top*2-self.thickness,angle,panel,90-angle,hf,90]
        for i in sx[:-1]:
            self.polygonWall(borders, move="right", edge="FeFeeeee",callback=[self.divider_front],)
        if (self.add_lid):
            augment = t*(1+lid_play)
            with self.saved_context():
                self.rectangularWall(y+2*augment, h + augment, ["FfEf"], move="right", label="lid Side Left")
                self.rectangularWall(y+2*augment, h + augment,["FfEf"], move="right", label="lid Side Right")
                self.rectangularWall(x+2*augment, h + augment, ["FFEF"], move="right", label="lid Side front")
                self.rectangularWall(x+2*augment, h + augment,["FFEF"], move="right", label="lid Side back")
            self.rectangularWall(y, h + t, "fFfF", move="up only")
            with self.saved_context():
                self.rectangularWall(x+2*augment, y+2*augment, "ffff", move="right", label="lid top")

