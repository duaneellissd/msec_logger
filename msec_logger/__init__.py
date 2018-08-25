'''Most pythonic logging is Unix syslog based. That's helpful if that's
your goal, but it is not always your goal

Often, the syslog based solutions includes a long date/time stamp in
column 0. When debugging, I prefer a different format where "time 0"
is the time the application started. When debugging I am more
interested in a time scale listed in seconds and milliseconds.

Yes, I could write to 'syslog' - but to be honest, why?  I don't want
to read or sort or sift my log messages from countless other log
messages.

To that end, there are a few important features:

Important feature(1) A simple log format, a timestamp in column 0.

```
     23.431 | started processing
     23.480 | finished processing
```
Time zero is when the application started.

The above tells me that at 23.431 seconds since the application started
the application "started processing" (what ever that is)

Important feature(2) simple time based math.

But more importantly, and this is the entire reason I prefer this
method. This format lets me quickly perform "mental math" and
determine that it took about 50 milliseconds "process"

When debugging, the timescales I most commonly deal with are in the
order of seconds or milliseconds between operations, mental math using
hours minutes and seconds is well, challanging I have to stop and
think for minute or two, and "borrow 60" from the next column..

Important feature(3) identify the source

I've often been emailed a logfile from somebody and they ask me to
review the log...  Knowing more detail about the machine and person
who ran the application is important to the debug process.

The timestamp at the start/stop of the log, is often helpful to
determine when exactly the log was created, who did it, and other
system details.

USAGE:

In your startup (main) file do this:

```
    import msec_logger

    def main():
           ...
           # Optionally, send log to stdout
           msec_logger.common_mSecLogger.open_console()
           # Or to a log file..
           msec_logger.common_mSecLogger.open_logfile( "somefilename.txt" )
           # The above, will write to BOTH console and FILE.
           ...

```

Then, within classes where you want to use the debug log, do this:
```
    import msec_logger
    class MyClass( msec_logger.LogHelper ):
         def __init__(self):
             ...
             msec_logger.LogHelper.__init__()
             ...

         def do_something(self):
             # debug_print() auto-appends a newline.
             self.debug_print("The answer is: %d" % 42 )


         def do_foo(self):
             # Where as debug_write() does not append a newline
             self.debug_write("The answer is: %d\n" % 42 )

         def foo(self):
             self.debug_push() # temp disable.
             self.debug_print("This will not print")
             self.debug_pop() # restore.
```
'''


import time
import os
import sys
import time
import platform
import atexit
import getpass

TAB_WIDTH=4

__all__ = [ 'mSecLogger_Base', 'common_mSecLogger', 'LogHelper' ]
            

class mSecLogger_Base( object ):
    '''
    Base logging class for the milliSecond logger.
    Often this should be a singleton within your application.
    '''
    def __init__(self):
        self.start_time = time.time()
        self.fp_console = None
        self.fp_file = None
        self.column = 0
        self._disable_quasi_stack = 0
        self._first_log = True
        self.dup2syslog = False
        self._current_line = ''
        atexit.register( self.close_logfile )

    def disable_push( self ):
        '''
        Temporarily stop logging...
        '''
        self._disable_quasi_stack += 1
        # help catch runaways...
        assert( self._disable_quasi_stack < 50 )

    def disable_pop( self ):
        '''
        Re-enable logging after a disable push.
        '''
        self._disable_quasi_stack -= 1
        assert( self._disable_quasi_stack >= 0 )

    def _write_raw( self, s, timestamp=False ):
        # internal function - not public
        # Tabs have been expanded.. newlines handled...
        # We just write to the places we should write
        if self._first_log:
            # do not repeat.
            self._first_log = False
            self._identify()

        # do we write to syslog?
        if (not timestamp) and self.dup2syslog:
            if s == '\n':
                syslog.syslog( self._current_line )
                self._current_line = ''
            else:
                self._current_line += s
                
        self.column += len(s)
        if self._disable_quasi_stack == 0:
            for fp in (self.fp_console, self.fp_file):
                if fp:
                    fp.write(s)

    def _expand_tabs(self,s):
        # internal function - not public
        # Expand tabs to TAB_WIDTH.
        assert( isinstance(s,str) )

        if self.column == 0:
            self._write_timestamp()
            
        parts = s.split('\t')
        last_element  = parts.pop()
        for p in parts:
            self._write_raw(p)
            n = (TAB_WIDTH - self.column) % TAB_WIDTH
            if n:
                self._write_raw( ' ' * n )
        if len(last_element) == 0:
            # string ended with a tab, nothing to do
            pass
        else:
            self._write_raw( last_element )

        
    def open_console( self ):
        '''
        Start logging to the console.
        '''
        self.fp_console = sys.stdout

    def close_console( self ):
        '''
        Stop logging to the console.
        '''
        self.fp_console = sys.stdout
        
    def close_logfile(self):
        '''
        Closes the log file
        '''
        self.write_ln("#========================================")
        self.write_ln("# File closed: %s" % time.strftime("%y-%m-%d %H:%M:%S"))
        self.write_ln("#========================================")
        if self.fp_file:
            try:
                self.fp_file.close()
            except:
                pass
            self.fp_file = None
        
    def open_logfile( self, filename ):
        '''
        Open a log file... and identify 
        '''
        self.close_logfile()
        if filename is None:
            return

        # backup incase 'filename' is not a 'file' class.
        txt_filename = "(unknown-filename)"
        if isinstance( filename, str ):
            if filename in ('-', '/dev/stdout'):
                self.fp_file = sys.stdout
            else:
                filename = os.path.abspath(filename)
                sys.fp_file =open( filename, 'w' )
            txt_filename = filename
        else:
            # it must have a "write" operator.
            if not hasattr( filename, 'write' ):
                raise ValueError("the 'filename' object does not have a write method")
            self.fp_file = filename
            # Try to determine the filename
            try:
                fn = filename.name
                if filename.__class__.__name__ == 'file':
                    txt_filename = os.path.abspath( filename.name )
            except:
                # No clue what this is
                pass
        # startup banner
        self._identify('Filename: %s' % txt_filename)

    def _write_timestamp(self):
        # internal function, not public
        # Log timestamp in seconds & milliseconds.
        # each line in the log file looks like this example
        #     "  23.023 | Some message here"
        # This function writes the " timestamp | " portion.
        #
        msecs = time.time() - self.start_time
        secs  = int(msecs)
        msecs = int((msecs - secs) * 1000.0)
        s = "%4d.%03d | " % (secs,msecs)
        # This is a timestamp..
        self._write_raw(s,True)
        
    def write( self, msg ):
        '''
        Write text (without a terminal newline) to log.
        In contrast, write_ln() appends a terminal newline.

        msg may be a string, a list of strings, or tuple of strings.
        '''
        if isinstance( msg, (list, tuple)):
            for m in msg:
                self.write(msg)
            return
        if not isinstance( msg, str ):
            raise ValueError("expecting strings only in base log write()")

        # Look for the LAST newline
        newline = msg.rfind('\n')
        if newline < 0:
            # none, just write it
            self._expand_tabs( msg )
            return

        parts = msg.split('\n')
        last = parts.pop()

        for p in parts:
            if len(p) > 0:
                self._expand_tabs(p)
            self._write_raw('\n')
            self._column = 0
        if len(last) == 0:
            # string ended in a newline, do nothing
            pass
        else:
            # string did nto end in a newline
            self._expand_tabs(p)
        
    def write_ln(self, msg):
        '''
        Write message with terminal newline.
        '''
        # Expand nested iterables
        if isinstance( msg, (list, tuple)):
            for m in msg:
                self.write_ln(m)
            return
        
        self.write( msg )
        self._write_raw( '\n' )
        self.column = 0

    def wallclock( self ):
        '''
        Write the current date/time to the log.
        '''
        self.write_ln( "Now(wallclock):  %s" % time.strftime("%y-%m-%d %H:%M:%S"))
        
    def _identify(self, msg=None):
        # Internal function to write a log header
        self._first_log = False
        self.write_ln( "#========================================")
        self.write_ln( "# started: %s" % time.strftime("%y-%m-%d %H:%M:%S"))
        self.write_ln( "# machine: %s" % platform.node())
        self.write_ln( "#     pid: %d" % os.getpid())
        self.write_ln( "#    user: %s" % getpass.getuser() )
        self.write_ln( "#     cwd: %s" % os.getcwd() )
        if msg:
            self.write_ln(" # %s" % msg )
        self.write_ln( "#  Python: %s" % sys.executable )
        self.write_ln( "# Version: %d.%d.%d" % (sys.version_info[0],sys.version_info[1],sys.version_info[2]))
        self.write_ln( "#---------")
        for n,v in enumerate( sys.argv ):
            self.write_ln( "# argv[%d] = %s" % (n,v))
        self.write_ln( "#---------")
        self.write_ln( "#========================================")
        self.write_ln("")

common_mSecLogger = mSecLogger_Base()

class LogHelper(object):
    '''
    Simple helper class to perform debug logging with a class.
    '''
    
    def __init__( self, logger = common_mSecLogger ):
        print("")
        print("start of LogHelper.__init__()")
        print("In loghelp init")
        self._debug_log_enabled = True
        self._logger = logger
        print("done loghelp init")
        print('dirself: %s' % dir(self))
        print("end of LogHelper.__init__()")


    def debug_print( self, msg ):
        print("in LogHelper.debug_print(), dir: %s" % dir(self))
        if self._debug_log_enabled and (self._logger != None):
            self._logger.write_ln(msg)

    def debug_write( self, msg ):
        if self._debug_log_enabled and (self._logger != None):
            self._logger.write(msg)

    def debug_push(self):
        if self._logger != None:
            self._logger.disable_push()

    def debug_pop(self):
        if self._logger != None:
            self._logger.disable_pop()
            
    def debug_wallclock( self ):
        if self._debug_log_enabled and (self._logger != None):
            self._logger.wallclock()
