To enter the indicators into MetaStock:
1. In the Tools menu, select Indicator Builder.
2. Click New to open the Indicator Editor for a new indicator.
3. Type the name of the formula.
4. Click in the larger window and type in the formula.
5. Click OK.
6. Repeat steps 2-5 for the remaining two formulas.

Name: Directional Down
Formula:
If(H<Mov(C,20,S),-2,0)

Name: Directional Up
Formula:
If(L>Mov(C,20,S),2,0)

Name: Non-Directional
Formula:
c1:=H>=Mov(C,20,S) AND L<=Mov(C,20,S);
If(c1,1,0);
If(c1,-1,0)

To enter the indicators into MetaStock:
1.  In the Tools menu, select Expert Advisor.
2.  Click New to open the Expert Editor for a new expert.
3.  Type a name for the expert, such as "Directional Breakout."
4.  Click the Highlights tab.
5.  Click New to create a new highlight.
6.  Type the name of the highlight.
7.  Set the color to that specified.
8.  Click in the Condition window and type in the formula.
9.  Click OK.
10.  Repeat steps 5-9 for the remaining two highlights.
11.  Click OK to close the Expert Editor.

Name: Directional Down
Color:  Blue
Formula:
H<Mov(C,20,S)

Name: Directional Up
Color:  Green
Formula:
L>Mov(C,20,S)

Name: Non-Directional
Color:  Red
Formula:
L<=Mov(C,20,S) AND H>=Mov(C,20,S)