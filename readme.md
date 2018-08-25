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
bash$ pip3 install git+https://github.com/duaneellissd/msec_log.git
```

## For example

```python

    import debuglog
	
    class SomeClass(DebugLog):
		def __init__(self):
			DebugLog.__init__(self)
			
		def do_something(self,a,b):
			self.calculate(a,b)
			self.debug_print( "MUL is: %d" % (a * b) )
```

The output would look something like this:
```
     0.000 | Starting Blah.Py
	... [snip] ... 
    45.323 | MUL is: 42
    
```


## usage


