from pyticli import Program

propositions = [
    """next(always(I==3) and next(next(J==4)))\n and next(I==2)""",
    """next(always(I==3) and next(next(J==4))) and next(J==1)""",
    """next(always(I==1 and next(I<5))) and next(next(next(J==2))) """ \
    """and next(J==3 or I==J+H) and I<4 or next(R<=5)""",
    """next(I // J)""",
]

for proposition in propositions:
    print "\n:> %s" % proposition
    try:
        print Program(proposition).query(verbose=1)
    except Exception, e:
        print e
