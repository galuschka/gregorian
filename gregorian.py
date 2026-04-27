""" date calculation on Gregorian calendar

This module uses Jan 1st 1 as ordinal 1 (same as datetime.date.toordinal).
For internal calculation, we shit to (imaginary) Mar 1st 0 as offset 0.
When starting at Mar 1st, the number of days per month is pure integer artihmetic:
                           |   |   |   |   |
                           v   v   v   v   v
    Mar,Apr,May,Jun,Jul:  31, 30, 31, 30, 31   ∑: 153 days
    Aug,Sep,Oct,Nov,Dec:  31, 30, 31, 30, 31   ∑: 153 days
    Jan,Feb:              31, rest             leap year day just added at end of list
"""
#     toordinal( 1, 1, 1 )          = 1  (to match same as datetime.date.toordinal)
# ==> 0 + _DAYS_BEFORE_MONTH[1] + 1 = 1  (see [j])
# ==>     _DAYS_BEFORE_MONTH[1]     = 0
#
# using range 0..13 to allow month ± 1: 0 = dec:year-1 / 13 = jan:year+1
# e.g. ultimo(year,month) = toordinal( year, month+1, 0 )
#
#                        -31   +31           -31   -30   -31   -30   -31
#                       +---+ +---+         +---+ +---+ +---+ +---+ +-< -153
#                       v   | |   v         |   | |   | |   | |   | |
#               year-1:dec, jan, feb,   mar v   | v   | v   | v   | v
_DAYS_BEFORE_MONTH = [ -31,   0,  31,    -306, -275, -245, -214, -184,
                                         -153, -122,  -92,  -61,  -31,  0 # jan:year+1
] #                                      |  ^   | ^   | ^   | ^   | ^   |
#                                        |  |   | |   | |   | |   | |   |
#                                      <-+  +---+ +---+ +---+ +---+ +---+
#                                            -31   -30   -31   -30   -31

def toordinal( year, month, day ):
    """ return ordinal of given date as datetime.date.toordinal: Jan 1st 1 = 1
        month in range 0..13: 0 = dec:year-1 / 13 = jan:year+1
    """
    # (month + 11) % 14: 0->11, 1->12, 2->13, 3->0, 4->1, .. 12->10
    year -= (((month + 11) % 14) // 11)                   # ...-1 when month <= 2
    return year*365 + year//4 - year//100 + year//400 + _DAYS_BEFORE_MONTH[month] + day

def ordinal_jan1( year:int ):
    """ return ordinal of Jan 1st of year
    """
    year -= 1                                              # ...-1 since jan
    return year*365 + year//4 - year//100 + year//400 + 1  # [j] ==> _DAYS_BEFORE_MONTH[1] = 0

def fromordinal( n:int ):
    """ inverse of toordinal(): return year,month,day of given ordinal
    """
    n += 305                    # shift: jan 1st 1 = 1 --> mar 1st 0 = 0
    c4, n = divmod( n,146097 )  # 365*4+1==1461, 1461*25-1==36524, 36524*4+1=146097
    c1, n = divmod( n, 36524 )  # 0..4!: 146096//36524 == 4 (1 more day every 4th century)
    y4, n = divmod( n,  1461 )  # 0..24:  36524//1461 == 24 (1 less day every century)
    y1, n = divmod( n,   365 )  # 0..4!:   1460//365  ==  4 (1 more day  every 4th year)
    m5, n = divmod( n,   153 )  # 0..2: number of 5 months blocks 31,30,31,30,31
    m2, n = divmod( n,    61 )  # 0..2: number of 2 months blocks 31,30
    m1, n = divmod( n,    31 )  # 0..1: number of 31 days months

    m     = m5*5 + m2*2 + m1                         # 0=mar, 1=apr, ... 10=jan, 11=feb
    year  = c4*400 + c1*100 + y4*4 + y1 + (m // 10)  # back shift: ...+1 when jan or feb
    month = ((m + 2) % 12) + 1                       # mar=0..feb=11 -> jan=1..dec=12
    leap  = (c1|y1) // 4                             # is Feb 29th ? 1 : 0
    return year, month - leap, n+1 + leap*28         # y,3,1 -> y,2,29 when Feb 29th

_ORDINAL_1970 = ordinal_jan1(1970)

def time2ordinal( time:float ):
    """ convert UNIX epoch time into ordinal
    """
    return int(time / 86400.0) + _ORDINAL_1970

def ordinal2time( ord:int ):
    """ convert ordinal (0:00:00 UTC) into UNIX epoch time
    """
    return (ord - _ORDINAL_1970) * 86400.0

def ordinal2wday( ord:int ):
    """ return week day of ordinal
    """
    return (ord + 6) % 7  # 0:Monday, ... 6:Sunday

def wday( year:int, month:int, day:int ):
    """ week day of given date (0 = Monday)
    """
    return ordinal2wday( toordinal( year, month, day ) )

def yday( year:int, month:int, day:int ):
    """ year day: day number of given date (==> Jan1 = 1)
    """
    return toordinal( year, month, day ) - ordinal_jan1( year ) + 1
