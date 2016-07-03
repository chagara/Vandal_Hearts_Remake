import cocos

'''
CHRIS

Controls what happens when a unit wants to move/attack or pretty
much interact with the map layer or the user.
'''

import DefineGlobals


class Unit:
    def __init__(self, Sprite, Tile, Image, BG, P1, Properties):
        self.Sprite = Sprite
        self.Tile = Tile
        self.Image = Image
        self.bg = BG
        self.MoveRange = Properties['Move']
        self.AttackRange = Properties['AtkRng']
        # Varaibles to record of the unit has moved or attacked.
        self.moved = False
        self.attacked = False
        # Variable to show if unit can be selected
        self.select = True
        # Variable so the unit knows which team it is on.
        self.P1 = P1
        # Variable for units that can pass through enemies.
        self.fly = False
        # Variables for the unit
        self.HP = Properties['HP']
        self.MP = Properties['MP']
        self.AT = Properties['AT']
        self.DF = Properties['DF']
        self.AGL = Properties['AGL']
        self.Update_Label()
        pass

    def Update_Label(self):
        self.label = cocos.text.Label(str(self.HP),
                                      font_name='Font_dark_size12.fnt',
                                      anchor_x="right", anchor_y="bottom")
        self.label.position = (self.Sprite.width / 2, -self.Sprite.height / 2)
        self.Sprite.add(self.label)

    def Hit(self, AtUnit):
        # Simple mechanics for now.
        self.HP -= (AtUnit.AT//2 - self.DF//6)
        self.Sprite.children = []
        self.Update_Label()
        if self.HP <= 0:
            DefineGlobals.unit_layer.remove(self.Sprite)

    def MoveUnit(self, x, y, Unmove=False, Debug='') -> None:
        # Moves the unit the number of tiles specified. Positive x right, positive y up.
        self.Sprite.position = (self.Sprite.position[0] + x * self.Tile.Cell.width,
                                self.Sprite.position[1] + y * self.Tile.Cell.height)
        # Fixes reference to tile
        self.Tile.hasUnit = False
        self.Tile.unit = None
        self.Tile = DefineGlobals.tileData[self.bg.get_key_at_pixel(self.Sprite.x,self.Sprite.y)]
        if Debug != '': print(Debug, self.bg.get_key_at_pixel(self.Sprite.x, self.Sprite.y))
        self.Tile.hasUnit = True
        self.Tile.unit = self
        if Unmove:
            self.moved = False
        else:
            self.moved = True

    def HighlightAvailable(self, Colour=(0, 0, 255)) -> None:
        # Check that the unit can move
        if self.moved: return
        # Highlight the available squares for the unit to move to.
        Q = [self.Tile.Cell]
        P = set()
        M = [self.MoveRange]
        while len(Q) > 0:
            Ind = M.index(max(M))
            Cell = Q.pop(Ind)
            MovLeft = M.pop(Ind)
            P.add(Cell)
            if MovLeft == 0: continue
            Temp = self.bg.get_neighbors(Cell)
            for C in Temp.values():
                if C is None or C in P or (not self.fly and DefineGlobals.tileData[C.i,C.j].hasUnit and
                                                   DefineGlobals.tileData[C.i,C.j].unit.P1!=DefineGlobals.P1Turn):
                    continue
                # Check that the current movement range is not higher...
                if C in Q:
                    M[Q.index(C)] = max(M[Q.index(C)], MovLeft - C.tile.properties['MovementCost'])
                    continue
                if MovLeft - C.tile.properties['MovementCost'] >= 0:
                    Q.append(C)
                    M.append(MovLeft - C.tile.properties['MovementCost'])
        for Cell in P:
            if DefineGlobals.tileData[Cell.i, Cell.j].hasUnit and Cell != self.Tile.Cell: continue
            self.bg.set_cell_color(Cell.i, Cell.j, Colour)
            self.bg.set_cell_opacity(Cell.i, Cell.j, 255)

    def HighlightAttack(self, Test=False, Colour=(255, 0, 0)):
        # Highlight the available squares for the unit to attack.
        Q = [self.Tile.Cell]
        P = set()
        M = [self.AttackRange]
        while len(Q) > 0:
            Ind = M.index(max(M))
            Cell = Q.pop(Ind)
            MovLeft = M.pop(Ind)
            P.add(Cell)
            if MovLeft == 0: continue
            Temp = self.bg.get_neighbors(Cell)
            for C in Temp.values():
                if C is None or C in P:
                    continue
                if Test:
                    # See if there is a unit that can be attacked here
                    if DefineGlobals.tileData[C.i, C.j].hasUnit and \
                                    DefineGlobals.tileData[C.i, C.j].unit.P1 != DefineGlobals.P1Turn:
                        return (True)
                # Check that the current movement range is not higher...
                if C in Q:
                    M[Q.index(C)] = max(M[Q.index(C)], MovLeft - 1)
                    continue
                if MovLeft - 1 >= 0:
                    Q.append(C)
                    M.append(MovLeft - 1)
        if Test: return (False)
        for Cell in P:
            if not DefineGlobals.tileData[Cell.i,Cell.j].hasUnit or \
                            DefineGlobals.tileData[Cell.i, Cell.j].unit.P1 == DefineGlobals.P1Turn: continue
            self.bg.set_cell_color(Cell.i, Cell.j, Colour)
            self.bg.set_cell_opacity(Cell.i, Cell.j, 255)

    def EndTurn(self) -> None:
        self.moved = False
        self.attacked = False

    def Zombie(self) -> None:
        # Start by attacking if possible.
        Q = [self.Tile.Cell]
        P = set()
        M = [self.MoveRange]
        while len(Q) > 0:
            Ind = M.index(max(M))
            Cell = Q.pop(Ind)
            MovLeft = M.pop(Ind)
            P.add(Cell)
            if MovLeft == 0: continue
            Temp = self.bg.get_neighbors(Cell)
            for C in Temp.values():
                if C is None or C in P or (not self.fly and DefineGlobals.tileData[C.i, C.j].hasUnit and
                                                   DefineGlobals.tileData[C.i, C.j].unit.P1 != DefineGlobals.P1Turn):
                    continue
                # Check that the current movement range is not higher...
                if C in Q:
                    M[Q.index(C)] = max(M[Q.index(C)], MovLeft - C.tile.properties['MovementCost'])
                    continue
                if MovLeft - C.tile.properties['MovementCost'] >= 0:
                    Q.append(C)
                    M.append(MovLeft - C.tile.properties['MovementCost'])
        for Cell in P:
            New_Cell = DefineGlobals.tileData[Cell.i, Cell.j]
            if New_Cell.hasUnit and Cell != self.Tile.Cell: continue
            Is_Enemy, Enemy_Cell = self.Enemy_In_Range(Cell)
            if Is_Enemy:
                # Move unit to this square
                self.MoveUnit(Cell.i - self.Tile.Cell.i, Cell.j - self.Tile.Cell.j)
                # Clear out the attacking logic.
                AtUnit = self
                DfUnit = DefineGlobals.tileData[Enemy_Cell.i, Enemy_Cell.j].unit
                DfUnit.Hit(AtUnit)
                if DfUnit.HP <= 0:
                    # Kill the unit, or at least make it disappear
                    DefineGlobals.tileData[Enemy_Cell.i, Enemy_Cell.j].unit = None
                    DefineGlobals.tileData[Enemy_Cell.i, Enemy_Cell.j].hasUnit = False
                else:
                    # Counterattack! If it is possible...
                    if abs(Enemy_Cell.i - Cell.i) + abs(Enemy_Cell.j - Cell.j) <= DfUnit.AttackRange:
                        AtUnit.Hit(DfUnit)
                        if AtUnit.HP <= 0:
                            # This is the ultimate in self-referential dumb-fuckery.  If the unit is killed, then the
                            # unit class will delete all references to itself... hopefully.
                            DefineGlobals.tileData[Cell.i, Cell.j].unit = None
                            DefineGlobals.tileData[Cell.i, Cell.j].hasUnit = False
                return

    def Enemy_In_Range(self, Cell):
        Q = [Cell]
        P = set()
        M = [self.AttackRange]
        while len(Q) > 0:
            Ind = M.index(max(M))
            Cell = Q.pop(Ind)
            MovLeft = M.pop(Ind)
            if DefineGlobals.tileData[Cell.i, Cell.j].hasUnit and \
                            DefineGlobals.tileData[Cell.i, Cell.j].unit.P1 != DefineGlobals.P1Turn:
                return True, Cell
            if MovLeft == 0: continue
            Temp = self.bg.get_neighbors(Cell)
            for C in Temp.values():
                if C is None or C in P:
                    continue
                # Check that the current movement range is not higher...
                if C in Q:
                    M[Q.index(C)] = max(M[Q.index(C)], MovLeft - 1)
                    continue
                if MovLeft - 1 >= 0:
                    Q.append(C)
                    M.append(MovLeft - 1)
        return False, None
