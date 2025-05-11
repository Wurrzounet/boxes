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
        bottom = max(self.settings.sx) / 3
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

class CardBoxV2(Boxes):
    """Box for holding of playing cards, with versatile options"""
    ui_group = "Box"

    description = """
### Description
Versatile Box for holding playing cards. 
For board game insert. Imagined for a flat storage and not tested for other case.
Tree basics cards size are proposed by default : 

Tarot : 70x120mm

Poker : 63.5x89 mm

MiniPoker : 45x68mm

The margin is 3mm for unsleeved card (So a poker card will generate a 63.5x92 space)

The margin for sleeved card is 8mm for the lenght and 4mm for the width (So a poker card will generate a 64.5x97 space) 

#### Building instructions
Place inner walls on floor first (if any). Then add the outer walls. Glue the two walls without finger joins to the inside of the side walls

Example of the empty box
![Details](static/samples/CardBoxV2-detail.jpg)
Full box with the sleeved 7th wonders Cards:
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
            help="size of the card to store, y and x wont be used. Tarot : 70x120mm ; Poker : 63.5x89mm ; minipoker : 45x68mm")
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
    def boxheight(self):
        if self.outside:
            return self.h -  self.thickness
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

    def divider_back_and_front(self):
        t = self.thickness
        sx = self.sx
        y = self.boxheight

        pos =  -0.5 * t
        for i in sx[:-1]:
            pos += i + t
            self.fingerHolesAt(pos, 0, y, 90)

    def divider_front(self):
        t = self.thickness
        y = self.boxheight

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
        h = self.boxheight
        sx = self.sx
        x = self.boxwidth

        s = FingerHoleEdgeSettings(thickness=t, wallheight=h, fingerholedepth=self.fingerholedepth)
        p = FingerHoleEdge(self, s)
        p.char = "A"
        self.addPart(p)

        with self.saved_context():
            self.rectangularWall(x, h + t , "FFeF",callback=[self.divider_back_and_front],
             move="right", label="Back")

        self.rectangularWall(x, h + t, "EEEE", move="up only")

        with self.saved_context():
            self.rectangularWall(y, h + t, "Ffef", move="right", label="Outer Side Left")
            self.rectangularWall(y, h + t, "Ffef", move="right", label="Outer Side Right")
        self.rectangularWall(y, h + t, "fFfF", move="up only")

        with self.saved_context():
            self.rectangularWall(x, y, "ffff", callback=[self.divider_bottom],
                                 move="right", label="Bottom")
        self.rectangularWall(x, y*1.1, "eEEE", move="up only")

        for i in range(len(sx) - 1):
            self.rectangularWall(h, y, "fAff", move="right", label="Divider")

        #Ajout de cache avant, construit comme un rectangle avec un angle coupé,
        #la base fait 1/3 de la case, la largeur sera à rajouter lors de la constuction
        falseBottom= max(self.sx) / 3
        #la largeur de la partie haute sera de 1/3 de la base, soit 1/9eme de la largeur de la case
        top= falseBottom*0.3
        # la hauteur avant l'angle sera de 1/3 de la hauteur total, on ajout l'epaisseur pour raison de construction
        hf = h * 0.3 + self.thickness
        #la partie coupé, on la calcul, on est sur un triangle rectangle. de base on est sur un rectangle de taille Hauteur x 1/3 case.
        #on a déjà coupé 1/3 de la hauteur et de la largeur, donc la coupe sera l'hypothénus du reste qui formera un triangle rectangle.
        panel =math.sqrt( (h*0.7)*(h*0.7)+(falseBottom*0.7)*(falseBottom*0.7))
        #on calcul maintenant l'angle en utilisant les règle du cosinus. adjacent/hypotenus = cos(angle)
        angle = math. degrees(math.acos(falseBottom*0.7/panel))

        # ordre des coté, construit dans le sens trigonometrique.
        borders = [self.thickness,0,falseBottom, 90, hf, 90 - angle, panel, angle, top+self.thickness,
                       90, h,0,self.thickness , 90]

        self.polygonWall(borders, move="right",edge="eFeeeFe", label='front left')
        borders = [falseBottom,0,self.thickness, 90,self.thickness,0,h,90,top+self.thickness,angle,panel,90-angle,hf,90]
        self.polygonWall(borders, move="right", edge="FeeFeee", label='front right')
        borders = [falseBottom, 0, self.thickness,0, falseBottom, 90, hf,90 - angle,panel,angle,top*2+self.thickness,angle,panel,90-angle,hf,90]
        for i in sx[:-1]:
            self.polygonWall(borders, move="right", edge="FeFeeeee",callback=[self.divider_front],)

        if (self.add_lid):
            augment = self.thickness*(1+self.lid_play)
            with self.saved_context():
                self.rectangularWall(y+2*augment, h + augment,"Ffef", move="right", label="lid Side Right")
                self.rectangularWall(y+2*augment, h + augment, "Ffef", move="right", label="lid Side Left")
                self.rectangularWall(x+2*augment, h + augment, "FFeF", move="right", label="lid Side front")
                self.rectangularWall(x+2*augment, h + augment,"FFeF", move="right", label="lid Side back")
            self.rectangularWall(y, h + t, "fFfF", move="up only")
            with self.saved_context():
                self.rectangularWall(x+2*augment, y+2*augment, "ffff", move="right", label="lid top")

