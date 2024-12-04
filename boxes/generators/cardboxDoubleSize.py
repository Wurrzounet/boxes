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
from gc import callbacks

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

        bottom = self.x/3
        self.edges["f"](bottom)
        self.corner(90)
        self.edge(0)
        self.corner(-180, bottom/2)
        self.edge(0)
        self.corner(90)
        self.edges["f"](bottom)

class CardBoxDoubleSize(Boxes):
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

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser(y=72,x=50, h=40)

        self.argparser.add_argument(
            "--first_case_size", action="store", type=str, default="tarot",
            choices=['tarot','poker', 'minipoker', 'custom'],
            help="size of the card to store, y and x wont be used. Poker : 63.5*89 mm cards.  minipoker : 45*68mm cards")
        self.argparser.add_argument(
            "--first_stage", action="store", type=float, default=0.5,
            help="Height of the first stage, multiple of height"
        )
        self.argparser.add_argument(
            "--second_case_size", action="store", type=str, default="poker",
            choices=['tarot', 'poker', 'minipoker', 'custom'],
            help="size of the card to store, y and x wont be used. Poker : 63.5*89 mm cards.  minipoker : 45*68mm cards")

        self.argparser.add_argument(
            "--sleeved_cards", action="store", type=BoolArg(), default=True,
            help="Add a small gap the case, to allow to put sleeved card in it (add 4mm for the width and 6 mm for the height of the card. Not used for custom card size"
        )

        self.argparser.add_argument(
            "--add_lid", action="store", type=BoolArg(), default=False,
            help="Add a lid to help to keep cards in place."
        )
        self.argparser.add_argument(
            "--lid_play", action="store", type=float, default=0.15,
            help="Add a play between lid and insert. Multiple of thickness"
        )

    @property
    def widthFirstCard(self):
        cardlen = 0
        # taille supplémentaire case en fonction de la presence ou non de sleeves
        vert_up = 8 if (self.sleeved_cards) else 3
        match self.first_case_size:
            case 'poker':
                cardlen = 89 + vert_up
            case 'minipoker':
                cardlen = 68 + vert_up
            case 'tarot':
                cardlen = 120 + vert_up
            case 'custom':
                cardlen = self.x
        return (cardlen)

    @property
    def widthSecondCard(self):
        cardlen = 0
        # taille supplémentaire case en fonction de la presence ou non de sleeves
        vert_up = 8 if (self.sleeved_cards) else 3
        match self.second_case_size:
            case 'poker':
                cardlen = 89 + vert_up
            case 'minipoker':
                cardlen = 68 + vert_up
            case 'tarot':
                cardlen = 120 + vert_up
            case 'custom':
                cardlen = self.x
        return (cardlen)

    @property
    def lenghtFirstCard(self):
        cardlen = 0
        # taille supplémentaire case en fonction de la presence ou non de sleeves
        horiz_up = 4 if (self.sleeved_cards) else 3
        match self.first_case_size:
            case 'poker':
                cardlen = 63.5 + horiz_up
            case 'minipoker':
                cardlen = 45 + horiz_up
            case 'tarot':
                cardlen = 70 + horiz_up
        return cardlen

    @property
    def lenghtSecondCard(self):
        cardlen = 0
        # taille supplémentaire case en fonction de la presence ou non de sleeves
        horiz_up = 4 if (self.sleeved_cards) else 3
        match self.second_case_size:
            case 'poker':
                cardlen = 63.5 + horiz_up
            case 'minipoker':
                cardlen = 45 + horiz_up
            case 'tarot':
                cardlen = 70 + horiz_up
        return cardlen

    #inner dimensions of surrounding box (disregarding inlays)
    @property
    def boxheight(self):
        return self.h
    @property
    def boxwidth(self):
        return (self.x)
    @property
    def boxdepth(self):
        return self.y

    def divider_bottom(self):
        t = self.thickness
        y = self.boxdepth
        pos =  0.5 * t+self.horizontalDif/2
        self.fingerHolesAt(pos, 0, y, 90)
        pos = self.boxwidth-pos
        self.fingerHolesAt(pos, 0, y, 90)

    def divider_back(self):
        self.divider_front_left_c(0)
        self.divider_front_right_c(self.boxwidth,0 )

    def divider_front_left(self):
        self.divider_front_left_c(1)

    def divider_front_left_c(self,thicRatio):
        t = self.thickness
        y = self.heightFirstStar
        w= self.horizontalDif/2
        pos = (thicRatio+0.5) * t+w
        self.fingerHolesAt(pos, t*thicRatio, y, 90)
        pos = (thicRatio+0.5) * t + y
        self.fingerHolesAt(t*thicRatio, pos, w, 0)

    def divider_front_right(self):
        self.divider_front_right_c( (self.boxwidth / 3),1)

    def divider_front_right_c(self,lengPiece,thicRatio):
        t = self.thickness
        y = self.heightFirstStar
        w= self.horizontalDif/2
        pos =  lengPiece-(0.5 * t+w)
        self.fingerHolesAt(pos, t*thicRatio, y, 90)
        posx = (lengPiece)-w
        pos = (thicRatio+0.5) * t + y
        self.fingerHolesAt(posx, pos, w, 0)

    def divider_side(self):
        t = self.thickness
        y = self.heightFirstStar+0.5*t
        self.fingerHolesAt(0, y, self.boxdepth, 0)

    def getcardlenght(self,position):
        if position == 'horizontal' :
            return max(self.widthFirstCard,self.widthSecondCard)
        else:
            return max(self.lenghtSecondCard, self.lenghtFirstCard)
    @property
    def horizontalDif(self):
        return abs(self.widthFirstCard-self.widthSecondCard)

    @property
    def heightFirstStar(self):
        return self.boxheight*self.first_stage

    def render(self):
        #if(self.case_size != 'custom'):
        self.y = self.getcardlenght('vertical')
        self.x = self.getcardlenght('horizontal')

        self.addPart(BoxBottomFrontEdge(self, self))

        t = 0
        y = self.boxdepth
        h = self.boxheight
        x = self.boxwidth

        #s = FingerHoleEdgeSettings(thickness=t, wallheight=h, fingerholedepth=self.fingerholedepth)
        #p = FingerHoleEdge(self, s)
        #p.char = "A"
        #self.addPart(p)

        with self.saved_context():
            self.rectangularWall(x, h + t , "FFeF",callback=[self.divider_back],
             move="right", label="Back")

        self.rectangularWall(x, h + t, "EEEE", move="up only")
        diff = self.horizontalDif/2
        #self.rectangularWall(diff, h + t, "Ffef", move="right", label="Outer Side Left")
        if (diff > t):
            with self.saved_context():
                self.rectangularWall(y, diff, "ffff", move="right", label="premier dessus")
                self.rectangularWall(y, diff, "ffff", move="right", label="deuxieme dessus")
            self.rectangularWall(x, diff*1.1, "EEEE", move="up only")

        if (self.heightFirstStar > t):
            with self.saved_context():
                self.rectangularWall(y, self.heightFirstStar, "ffFf", move="right", label="premier coté Etage")
                self.rectangularWall(y, self.heightFirstStar, "ffFf", move="right", label="deuxieme coté Etage")
            self.rectangularWall(x, self.heightFirstStar, "EEEE", move="up only")

        with self.saved_context():
            self.rectangularWall(y, h + t, "Ffef", move="right", label="Outer Side Left", callback=[self.divider_side])
            self.rectangularWall(y, h + t,"Ffef", move="right", label="Outer Side Right", callback=[self.divider_side])

        self.rectangularWall(y, h + t, "fFfF", move="up only")

        with self.saved_context():
            self.rectangularWall(x, y, "ffbf", callback=[self.divider_bottom], move="right", label="Bottom")
        self.rectangularWall(x, y*1.1, "eEEE", move="up only")


        #Ajout de cache avant, construit comme un rectangle avec un angle coupé,
        #la base fait 1/3 de la case, la largeur sera à rajouter lors de la constuction
        falseBottom= self.boxwidth / 3
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
        borders = [self.thickness,0,falseBottom, 90, hf, 90 - angle, panel, angle, top+self.thickness, 90, h,0,self.thickness , 90]
        self.polygonWall(borders, move="right",edge="eFeeeFe", label='front left',callback=[self.divider_front_left])
        borders = [falseBottom,0,self.thickness, 90,self.thickness,0,h,90,top+self.thickness,angle,panel,90-angle,hf,90]
        self.polygonWall(borders, move="right", edge="FeeFeee", label='front right',callback=[self.divider_front_right])
        #borders = [falseBottom, 0, self.thickness,0, falseBottom, 90, hf,90 - angle,panel,angle,top*2+self.thickness,angle,panel,90-angle,hf,90]


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

