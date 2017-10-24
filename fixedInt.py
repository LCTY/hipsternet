##########################################################################
#  This file is part of the deModel library, a Python package for using
#  Python to model fixed point arithmetic algorithms.
#
#  Copyright (C) 2007 Dillon Engineering, Inc.
#  http://www.dilloneng.com
#
#  The deModel library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public License as
#  published by the Free Software Foundation; either version 2.1 of the
#  License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library. 
#  If not, see <http://www.gnu.org/licenses/>
##########################################################################

__author__ = "$Author: guenter $"
__revision__ = "$Revision: 431 $"
__date__ = "$Date: 2007-09-19 19:16:58 +0200 (Wed, 19 Sep 2007) $"

import math
import copy
import numpy


def arrayFixedInt(intWidth, fractWidth, x):
    shape = x.shape
    x = x.flatten().tolist()
    for idx, val in enumerate(x):
        x[idx] = DeFixedInt(intWidth, fractWidth, val)

    x = numpy.array(x)
    return x.reshape(shape)


# def arrayFixedInt(intWidth, fractWidth, N, value=None):
#     if isinstance(N, int):
#
#         retA = numpy.array([DeFixedInt(intWidth, fractWidth) for i in range(N)])
#
#         if value:
#             for i, item in enumerate(retA):
#                 item.value = value
#
#     elif isinstance(N, (list, numpy.ndarray)):
#         retA = numpy.array([DeFixedInt(intWidth, fractWidth, value) \
#                             for value in N])
#
#     else:
#         raise TypeError("type(N) = '%s' not supported" % type(N))
#
#     return retA


class DeFixedIntOverflowError(OverflowError):
    "Used to indicate that a set value exceeds the specified width of DeFixedInt."


class DeFixedInt(object):
    __slots__ = ('__intWidth', '__fractWidth', '__roundMode', '__value')

    def __init__(self, intWidth=0, fractWidth=15, value=0, roundMode='round_even'):
        # Test for proper parameter
        # Setting the value will be tested through the property function
        if intWidth < 0:
            raise ValueError("Integer width needs to be >= 0!")
        if fractWidth < 0:
            raise ValueError("Fractional width needs to be >= 0!")

        if ((roundMode != 'trunc') and
                (roundMode != 'round_even') and
                (roundMode != 'round')):
            raise ValueError("Round mode '%s' not supported!" % roundMode)

        self.__intWidth = intWidth
        self.__fractWidth = fractWidth
        self.__roundMode = roundMode
        self._setValue(value)

    ######################################################################
    # properties
    ######################################################################

    def _getValue(self):
        return self.__value

    def _setValue(self, value):
        if isinstance(value, float):
            # print "float value"
            self._fromFloat(value)

        elif isinstance(value, int):
            # print "int value"
            self.__value = value
        else:
            print("unkown type: ", type(value))

        self._overflowCheck()

    value = property(_getValue, _setValue)

    def _getFloatValue(self):
        return self._toFloat()

    fValue = property(_getFloatValue)

    def _getIntWidth(self):
        return self.__intWidth

    intWidth = property(_getIntWidth)

    def _getFractWidth(self):
        return self.__fractWidth

    fractWidth = property(_getFractWidth)

    def _getWidth(self):
        return self.__intWidth + self.__fractWidth + 1

    width = property(_getWidth)

    def _getRep(self):
        return "A(%d,%d)" % (self.intWidth, self.fractWidth)

    rep = property(_getRep)

    ######################################################################
    # overloaded functions
    ######################################################################

    def __copy__(self):
        retValue = DeFixedInt(self.intWidth, self.fractWidth, self.value)
        return retValue

    def __getitem__(self, key):
        if isinstance(key, int):
            i = key
            if i >= self.width or i < (-self.width):
                raise IndexError("list index %d out of range %d ... %d" % \
                                 (i, -self.width, (self.width - 1)))

            if i < 0:
                shift = self.width + i
            else:
                shift = i

            return (self.value >> shift) & 0x1

        elif isinstance(key, slice):
            msb, lsb = key.start, key.stop

            # first determine the new value
            if lsb == None:
                lsb = 0
            if lsb < 0:
                raise ValueError("DeFixedInt[msb:lsb] requires lsb >= 0\n" \
                                 "            lsb == %d" % lsb)
            if msb == None or msb == self.width:
                if msb == None:
                    msb = self.width
                newValue = (self.value >> lsb)
            else:
                newValue = None

            if msb <= lsb:
                raise ValueError("DeFixedInt[msb:lsb] requires msb > lsb\n" \
                                 "            [msb:lsb] == [%d:%d]" % (msb, lsb))

            if msb > self.width:
                raise ValueError("DeFixedInt[msb:lsb] requires msb <= %d\n" \
                                 "            msb == %d" % (self.width, msb))

            if not newValue:
                newValue = (self.value & (1 << msb) - 1) >> lsb

            # then the new intWidth and fractWidth
            if lsb < self.fractWidth:
                if msb > self.fractWidth:
                    newFractWidth = self.fractWidth - lsb

                    if msb > self.intWidth + self.fractWidth:
                        newIntWidth = self.intWidth
                    else:
                        newIntWidth = msb - self.fractWidth

                else:
                    newIntWidth = 0
                    newFractWidth = msb - lsb

            else:
                newFractWidth = 0

                if msb > (self.intWidth + self.fractWidth):
                    newIntWidth = msb - lsb - 1
                else:
                    newIntWidth = msb - lsb

            # create new instance and return it
            retValue = DeFixedInt(newIntWidth, newFractWidth, newValue)

            return retValue

        else:
            raise TypeError("DeFixedInt item/slice index must be integer")

    def __repr__(self):
        str = "<%d" % self.__value
        # str += " (%.3f)" % (self.fValue)
        str += " A(%d,%d)>" % (self.__intWidth, self.__fractWidth)
        return str

    def __str__(self):
        str = "<%d" % self.__value
        str += " (%.3f)" % self.fValue
        str += " A(%d,%d)>" % (self.__intWidth, self.__fractWidth)
        return str

    def __hex__(self):
        width = self.width
        mask = int(2 ** width) - 1
        fStr = '0x%%.%dX' % (int(math.ceil(width / 4)))
        return fStr % (self.value & mask)

    def __mul__(self, other):
        retValue = DeFixedInt()

        if isinstance(other, DeFixedInt):

            # print "__mult__: other is DeFixedInt"
            retValue.__intWidth = self.__intWidth + other.__intWidth + 1
            retValue.__fractWidth = self.__fractWidth + other.__fractWidth
            retValue.__roundMode = self.__roundMode

            retValue.value = self.value * other.value

        elif isinstance(other, (int, float)):

            # print "__mult__: other is '%s' "% type(other)
            b = DeFixedInt(self.__intWidth, self.__fractWidth, other, self.__roundMode)
            retValue = self * b

        else:
            msg = "'%s' not supported as operator for DeFixedInt multiplication" % type(other)
            raise TypeError(msg)

        return retValue

    # def __div__(self, other):
    #  """Fixed point division

    #  Fixed pont representation is calculated based on:

    #  A(a1, b1) / A(a2, b2) = A(a1+b2+1, a2+b1)

    #  @type other   : - DeFixedInt
    #                  - int;        will be first converted to DeFixedInt based on
    #                                operand A intWidth/fractWidth
    #                  - float;      will be scaled and converted to DeFixedInt based
    #                                on intWidth/fractWidth of operand A

    #  @param other  : Operand B

    #  @rtype  : DeFixedInt
    #  @return : A / B
    #  """
    #  retValue = DeFixedInt()

    #  if(isinstance(other, DeFixedInt)):

    #    retValue.__intWidth = self.__intWidth + other.fractWidth + 1
    #    retValue.__fractWidth = self.__fractWidth + other.__intWidth
    #    retValue.__roundMode = self.__roundMode

    #    retValue.value = self.value / other.value

    #  else:
    #    msg = "'%s' not supported as operator for DeFixedInt division"%type(other)
    #    raise TypeError, msg

    #  return retValue




    def __add__(self, other):
        retValue = DeFixedInt(self.intWidth + 1, self.fractWidth)
        # print
        # print "before change: self: %s \n--> other: %s" %(self, other)
        temp = copy.copy(other)
        temp.newRep(self.intWidth, self.fractWidth)
        # print "after change: self: %s \n--> other: %s"% (self, other)
        # print "after change: self: %s \n--> temp: %s"% (self, temp)
        retValue.value = self.value + temp.value

        return retValue

    def __sub__(self, other):
        retValue = DeFixedInt(self.intWidth + 1, self.fractWidth)

        temp = copy.copy(other)
        temp.newRep(self.intWidth, self.fractWidth)

        retValue.value = self.value - temp.value

        return retValue

    def __lshift__(self, other):

        # check for the other value, only support 'int' type
        if not isinstance(other, int):
            msg = "unsupported operand type(s) for <<: 'DeFixedInt' and '%s'" % type(other)
            raise TypeError(msg)

        if other < 0:
            raise ValueError("negative shift count")

        retValue = DeFixedInt()

        width = self.width

        retValue.__intWidth = self.intWidth
        retValue.__fractWidth = self.fractWidth
        retValue.__roundMode = self.__roundMode

        retValue.value = self.value << other

        return retValue

    def __rshift__(self, other):
        if not isinstance(other, int):
            msg = "unsupported operand type(s) for <<: 'DeFixedInt' and '%s'" % type(other)
            raise TypeError(msg)

        if other < 0:
            raise ValueError("negative shift count")

        retValue = DeFixedInt()

        width = self.width

        retValue.__intWidth = self.intWidth
        retValue.__fractWidth = self.fractWidth
        retValue.__roundMode = self.__roundMode

        if other > 0:
            if self.__roundMode == 'round':
                roundBit = self[other - 1]  # take the msb that would get lost
                retValue.value = (self.value >> other) + roundBit  # and add it

            elif self.__roundMode == 'round_even':
                newBitZero = self[other]
                msbTrunc = self[other - 1]
                remainTrunc = self[other - 1:0]

                # TODO: should the 'not' work just for DeFixedInt?
                if msbTrunc and not remainTrunc.value:  # truncing 100..-> round even
                    retValue.value = (self.value >> other) + \
                                     (newBitZero & msbTrunc)

                else:  # not .500.. case, round normal
                    retValue.value = (self.value >> other) + msbTrunc

            else:  # __roundMode == 'trunc'
                retValue.value = self.value >> other

        else:
            retValue = self

        return retValue

    def __lt__(self, other):
        temp = copy.copy(other)
        temp.newRep(self.intWidth, self.fractWidth)
        if temp.value > self.value:
            return True
        else:
            return False

    def __le__(self, other):
        if self < other or self == other:
            return True
        else:
            return False

    def __eq__(self, other):
        temp = copy.copy(other)
        temp.newRep(self.intWidth, self.fractWidth)
        if temp.value == self.value:
            return True
        else:
            return False

    def __ne__(self, other):
        temp = copy.copy(other)
        temp.newRep(self.intWidth, self.fractWidth)
        if temp.value != self.value:
            return True
        else:
            return False

    def __gt__(self, other):
        temp = copy.copy(other)
        temp.newRep(self.intWidth, self.fractWidth)
        if temp.value < self.value:
            return True
        else:
            return False

    def __ge__(self, other):
        if self > other or self == other:
            return True
        else:
            return False

    ######################################################################
    # private methods
    ######################################################################

    def _fromFloat(self, value):
        self.__value = self.round(value * 2.0 ** self.__fractWidth)

    def _toFloat(self):
        return self.__value / (2.0 ** self.__fractWidth)

    def _overflowCheck(self):
        maxNum = 2 ** (self.width - 1) - 1
        minNum = - 2 ** (self.width - 1)

        if self.value > maxNum or self.value < minNum:
            msg = "Value: %d exeeds allowed range %d ... %d" % \
                  (self.value, minNum, maxNum)
            raise DeFixedIntOverflowError(msg)

    ######################################################################
    # public methods (interface)
    ######################################################################

    def isOverflowing(self, intWidth, fractWidth):
        maxNum = 2 ** (intWidth + fractWidth) - 1
        minNum = - 2 ** (intWidth + fractWidth)

        retValue = False

        if self.value > maxNum or self.value < minNum:
            retValue = True

        return retValue

    def newRep(self, intWidth, fractWidth):
        # first adjust the fractional width
        if fractWidth > self.fractWidth:
            n = fractWidth - self.fractWidth
            # need to grow first to avoid overflow
            self.__fractWidth = fractWidth
            self.value = self.value << n
        elif fractWidth < self.fractWidth:
            # here we might loose precision
            n = self.fractWidth - fractWidth
            self.value = self.value >> n
            self.__fractWidth = fractWidth

        # next adjust the integer width
        if intWidth > self.intWidth:
            self.__intWidth = intWidth
        elif intWidth < self.intWidth:

            # in case of a smaller intWidth we need to check for possible overflow
            if self.isOverflowing(intWidth, self.fractWidth):
                msg = "New intWidth: %d will overflow current value: %d" % \
                      (intWidth, self.value)
                raise DeFixedIntOverflowError(msg)

            self.__intWidth = intWidth

    def round(self, value):
        if self.__roundMode == 'trunc':
            retVal = int(value)

        elif self.__roundMode == 'round_even':
            # if value is .50 round to even, if not, round normal
            fract, integer = math.modf(value)
            absIValue = int(abs(integer))
            if int(integer) < 0:
                sign = -1
            else:
                sign = 1

            # TODO: look for a better way to compare here for 0.500
            # floating point compare does not seem to be so good
            if (abs(fract) - 0.5) == 0.0:
                if (absIValue % 2) == 0:  # even
                    retVal = absIValue * sign
                else:  # odd
                    retVal = (absIValue + 1) * sign
            else:
                retVal = round(value)

        elif self.__roundMode == 'round':
            retVal = round(value)

        else:
            raise "ERROR: DeFixedInt.round(): '%s' not supported round mode!" % \
                  self.__roundMode

        return int(retVal)

    def showRange(self):
        min = -2 ** self.intWidth
        max = 2 ** self.intWidth - 1.0 / 2.0 ** self.fractWidth
        print("A(%d, %d): " % (self.intWidth, self.fractWidth), end=' ')
        print("%f ... %f" % (min, max))

    def showValueRange(self):
        fract = 2 ** self.fractWidth
        min = -2 ** self.intWidth
        for i in range(2 ** self.width):
            print("i: %d --> %f" % (i, (min + i / 2.0 ** self.fractWidth)))

    def bit(self):
        pass


if __name__ == '__main__':
    a = DeFixedInt()
    a.value = 1

    print("Showing range:")
    a.showRange()
    print("printing a: ", a)

    a = DeFixedInt(8, 0, 1)
    print("Showing range:")
    a.showRange()
    print("printing a: ", a)

    a = DeFixedInt(8, 3, 1.2)
    print("Showing range: ")
    a.showRange()
    print("printig a: ", a)

    a = DeFixedInt(8, 2)
    print("Representation a: ", a.rep)

    b = DeFixedInt(8, 0)
    print("Representation b: ", b.rep)
    c = a + b
    print("Representation c: ", c.rep)
    a = 1.25
    b = 2.0
    c = a + b
    print(c)
