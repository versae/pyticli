from pyticli import Program

# g.v(0).out{"initial"}.outE{"next"}.inV.

p = """next(always(I==3) & next(next(J==4)))\n | next(I==2)"""
Program(p).abstract()
print p

p = """next(always(I==3) and next(next(J==4))) and next(J==1)"""
Program(p).abstract()
print p

p = """next(always(I==1 and next(I<5))) and next(next(next(J==2))) and next(J==3 or I==J+H) and I<4 or next(R<=5) """
Program(p).abstract()
print p

p = """next(I // J)"""
Program(p).abstract()
print p
