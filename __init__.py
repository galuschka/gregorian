""" date calculation on Gregorian calendar

This class uses Jan 1st 1 as reference as ordinal 1 (as datetime.date.toordinal).
When starting at Mar 1st, the number of days per month is pure integer artihmetic:
                           |   |   |   |   |
                           v   v   v   v   v
    Mar,Apr,May,Jun,Jul:  31, 30, 31, 30, 31   ∑: 153 days
    Aug,Sep,Oct,Nov,Dec:  31, 30, 31, 30, 31   ∑: 153 days
    Jan,Feb:              31, rest             leap year day just added at end of list
"""

class Gregorian:
    def __init__(self):
        self._ORD1970  = self.jan1st2ord( 1970 )  # UNIX epoch start date
        self._WDAY0    = 6                        # Jan 1st 1 was Monday (6+1)%7==0
        self._DAYS1Y   = 365
        self._DAYS4Y   = self._DAYS1Y   *  4 + 1  #   1461 days - leap year every 4th year
        self._DAYS100Y = self._DAYS4Y   * 25 - 1  #  36524 days - not leap year every 100th year
        self._DAYS400Y = self._DAYS100Y *  4 + 1  # 146097 days - again leap year every 400th year

        #                               +31   +30   +31   +30   +31
        #                              +---+ +---+ +---+ +---+ +--->
        #                              |   | |   | |   | |   | |
        #               - jan, feb, mar|   v |   v |   v |   v |
        self._D_OFF = [ 0,  0,  31, -306, -275, -245, -214, -184,
                                    -153, -122,  -92,  -61,  -31 # jan:0,feb:31
        ] #                         ^  |   ^ |   ^ |   ^ |   ^ |   ^   |     ^
        #                           |  |   | |   | |   | |   | |   |   |     |
        #                  -184 >---+  +---+ +---+ +---+ +---+ +---+   +-----+
        #                    ... +31    +31   +30   +31   +30   +31      +31

    def toordinal( self, year, month, day ):
        y = year - (((month + 9) % 12) // 10)
        return y*365 + y//4 - y//100 + y//400 + self._D_OFF[month] + day

    def jan1st2ord( self, year:int ):
        """ return ordinal of Jan 1st of year
        """
        y = year - 1  # jan/feb: 1 year before y
        return y*365 + (y//4) - (y//100) + (y//400) + 1  # _D_OFF[1] = 0

    def ord2wday( self, ord:int ):
        """ return week day of ordinal
        """
        return (ord + self._WDAY0) % 7  # 0:Monday, ... 6:Sunday

    def time2ord( self, time:float ):
        """ convert UNIX epoch time into ordinal
        """
        return int(time / 86400.0) + self._ORD1970

    def ord2time( self, ord:int ):
        """ convert ordinal into UNIX epoch time (0:00:00 UTC)
        """
        return (ord - self._ORD1970) * 86400.0

    def fromordinal( self, ord:int ):
        """ invert of toordinal(): return year,month,day of given ordinal
        """
        ord += 305                                   # jan 1st 1 = 1 --> mar 1st 0 = 0
        y400, ord = divmod( ord, self._DAYS400Y )
        y100      = min(  ord // self._DAYS100Y, 3 ) # 0..3: 146096/36524==4! - every 4th century has 1 more day
        ord      -=       y100 * self._DAYS100Y
        y4, ord   = divmod( ord, self._DAYS4Y )      # 0..24: (every century has one day less - 24 is max. anyway)
        y1        = min(  ord // self._DAYS1Y, 3 )   # 0..3: 1460/365==4! - every 4th year has 1 more day
        ord      -=         y1 * self._DAYS1Y        # ord here: days past Mar 1st (0..365)
        y = (y400*400) + (y100*100) + (y4*4) + y1    # ==year-1, when jan or feb

        m153, ord = divmod( ord, 153 )  # 0..2: number of 5 months blocks 31,30,31,30,31
        m61,  ord = divmod( ord,  61 )  # 0..2: number of 2 months blocks 31,30
        m31,  ord = divmod( ord,  31 )  # 0..1: number of 31 days months
        m3 = (m153*5) + (m61*2) + m31   # 0=mar, .. 11=feb

        return y + (m3 // 10), ((m3 + 2) % 12) + 1, ord + 1

        # year  = y + (m3 // 10)        # revert year-1 for jan/feb
        # month = ((m3 + 2) % 12) + 1   # 0->3, 1->4, ..., 9->12, 10->1, 11->2
        # day   = ord + 1               # day of month 1..31

        # print( f"{y=}  = {y400=}*400 + {y100=}*100 + {y4=}*4 + {y1=}" )
        # print( f"{m3=} = {m153=}*5 + {m61=}*2 + {m31=} / remaining {ord=}" )

    def yday( self, year:int, month:int, day:int ):
        """ year day: number of days past Jan 1st of given date (==> Jan1 = 0)
        """
        return self.toordinal( year, month, day ) - self.jan1st2ord( year )

    def wday( self, year:int, month:int, day:int ):
        """ week day of given date (0 = Monday)
        """
        return self.ord2wday( self.toordinal( year, month, day ) )
