""" date calculation on Gregorian calendar

This class uses Jan 1st 1 as reference as ordinal 1 (as datetime.date.toordinal).
When starting at Mar 1st, the number of days per month is pure integer artihmetic:
                           |   |   |   |   |
                           v   v   v   v   v
    Mar,Apr,May,Jun,Jul:  31, 30, 31, 30, 31   ∑: 153 days
    Aug,Sep,Oct,Nov,Dec:  31, 30, 31, 30, 31   ∑: 153 days
    Jan,Feb:              31, rest             leap year day just added at end of list
"""

#                                      +31   +30   +31   +30   +31
#                                     +---+ +---+ +---+ +---+ +--->
#                                     |   | |   | |   | |   | |
#                      - jan, feb, mar|   v |   v |   v |   v |
_DAYS_BEFORE_MONTH = [ 0,  0,  31, -306, -275, -245, -214, -184,
                                   -153, -122,  -92,  -61,  -31 # jan:0,feb:31
] #                                ^  |   ^ |   ^ |   ^ |   ^ |   ^   |     ^
#                                  |  |   | |   | |   | |   | |   |   |     |
#                         -184 >---+  +---+ +---+ +---+ +---+ +---+   +-----+
#                           ... +31    +31   +30   +31   +30   +31      +31

def toordinal( year, month, day ):
    y = year - (((month + 9) % 12) // 10)
    return y*365 + y//4 - y//100 + y//400 + _DAYS_BEFORE_MONTH[month] + day

def ordinal_jan1( year:int ):
    """ return ordinal of Jan 1st of year
    """
    y = year - 1  # jan/feb: 1 year before y
    return y*365 + (y//4) - (y//100) + (y//400) + 1  # _DAYS_BEFORE_MONTH[1] = 0

def fromordinal( n:int ):
    """ inverse of toordinal(): return year,month,day of given ordinal
    """
    def divmodmax( n, div, max ):
        i = min( n // div, max )  # integer division with given maximum
        return i, n - (i*div)     # rest (>=div, when number//div > max)

    n += 305                            # shift: jan 1st 1 = 1 --> mar 1st 0 = 0
    c4, n = divmod(    n, 146097 )      # 365*4+1==1461, 1461*25-1==36524, 36524*4+1=146097
    c1, n = divmodmax( n,  36524, 3 )   # 0..3: 146096//36524 ==  4 (every 4th century: 1 more day)
    y4, n = divmod(    n,   1461 )      # 0..24: 36524//1461  == 24 (every century:     1 less day)
    y1, n = divmodmax( n,    365, 3 )   # 0..3:   1460//365   ==  4 (every 4th year:    1 more day)
    m5, n = divmod(    n,    153 )      # 0..2: number of 5 months blocks 31,30,31,30,31
    m2, n = divmod(    n,     61 )      # 0..2: number of 2 months blocks 31,30
    m1, n = divmod(    n,     31 )      # 0..1: number of 31 days months

    m     = m5*5 + m2*2 + m1                         # 0=mar, 1=apr, ... 10=jan, 11=feb
    year  = c4*400 + c1*100 + y4*4 + y1 + (m // 10)  # back shift: ...+1 when jan or feb
    month = ((m + 2) % 12) + 1                       # back shift: mar=0..feb=11 -> jan=1..dec=12
    return year, month, n+1

_ORDINAL_1970 = ordinal_jan1(1970)

def time2ordinal( time:float ):
    """ convert UNIX epoch time into ordinal
    """
    return int(time / 86400.0) + _ORDINAL_1970

def ordinal2time( ord:int ):
    """ convert ordinal into UNIX epoch time (0:00:00 UTC)
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
    """ year day: number of days past Jan 1st of given date (==> Jan1 = 0)
    """
    return toordinal( year, month, day ) - ordinal_jan1( year )
