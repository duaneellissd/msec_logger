from unittest import TestCase

import msec_logger

# A simple class to act like a file.
captured_text = ''
class capture_class( object ):
    def __init__(self):
        pass
    def write( self, txt ):
        global captured_text
        captured_text += txt
    def close(self):
        # do nothing
        pass

class class_test( msec_logger.LogHelper ):
    def __init__(self):
        msec_logger.LogHelper.__init__(self)


class Test01(TestCase):
    def test_10_hello(self):
        for x in range(0,8):
            s = ''
            e = ''
            if x & 4:
                s = s + '\n'
                e = e + '| '
            else:
                pass
            s = s + 'Hello'
            e = e + 'Hello'
            if x & 2:
                s = s + '\n'
                e = e + '| '
            else:
                s = s + ' '
                e = e + ' '
            s = s + 'World'
            e = e + 'World'
            if x & 1:
                s = s + '\n'
                e = e + '| '
            foo = class_test()
            global captured_text
            captured_text = ''
            foo.debug_print(s)
            foo.debug_print("END")

            print("RESULT\n-------------\n%s\n-------------------" % captured_text )
            
            
            
