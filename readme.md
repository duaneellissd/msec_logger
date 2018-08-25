# A simple logging scheme for debug purposes

Logging system aimed at initial sw development phase of life
It also can log to syslog, but during development syslog is
not always the best place to find things.

That's not what I need, or want. 

* I do want a timestamp in column 0, 
* But not the Year, Month, Day...
* Seconds and milliseconds from program start is good enough
* The log could be written to a file or console or both, or disabled.

## Installation Directly from Git Hub:
```
bash$ pip3 install git+https://github.com/duaneellissd/msec_logger.git
```

## For example

Most pythonic logging is Unix syslog based. That's helpful if that's
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


