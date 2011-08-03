from pyticli import Program

#p = """next(always(I==3) and next(next(J==4)))\n and next(I==2)"""
#print Program(p).query()
#print p

#p = """next(always(I==3) and next(next(J==4))) and next(J==1)"""
#print Program(p).query()
#print p

#p = """next(always(I==1 and next(I<5))) and next(next(next(J==2))) """ \
#    """and next(J==3 or I==J+H) and I<4 or next(R<=5) """
#print Program(p).query()
#print p

#p = """next(I // J)"""
#print Program(p).query()
#print p

p = """next(always(I==3) and next(next(J==4)))"""
print Program(p).query()
print p
