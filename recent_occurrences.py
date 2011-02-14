#!/usr/bin/env python
"""
Cloudkick plugin to search for occurrences of a message in a log file with an
apache/nginx format timestamp, within the last 5 minutes.

Developed by Daniel Benamy at WNYC.

Source released under the MIT license.

Normally I wouldn't keep commented out lines, but I'm not yet confident of this
program and want to be able to debug it quickly.
"""


from datetime import datetime, timedelta
import sys


def main():
    if len(sys.argv) < 3:
        print "status err Invalid usage. Use '%s \"message\" file'." % sys.argv[0]
        sys.exit()
    message = sys.argv[1]
    file_name = sys.argv[2]
    recent = datetime.now() - timedelta(minutes=5)
#    print 'recent is %s' % recent
    
    lines = read_recent_lines(open(file_name), recent).splitlines()
#    print 'lines:\n%s' % '\n'.join(lines)
    # Filter out any lines earlier than recent
    while len(lines) > 0 and timestamp_of(lines[0]) < recent:
        lines.pop(0)
#    print 'recent lines:\n%s' % '\n'.join(lines)
    occurrences = ''.join(lines).count(message)
    
    print "status ok ok"
    print "metric occurrences int %d" % occurrences


def read_recent_lines(f, recent):
    """
    Returns data from the end of f which includes all lines with a timestamp
    of recent or later. Might also include some earlier lines.
    Returns a string.
    """
    # adapted from http://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-with-python-similar-to-tail
    f.seek(0, 2)
    bytes = f.tell()
#    print 'file has %s bytes' % bytes
    block = -1
    data = [] # blocks of data, not lines
    ts = datetime.now() # earliest timestamp read
    while ts >= recent and bytes + block * 1024 > 0:
        # If your OS is rude about small files, you need this check
        # If your OS does 'the right thing' then just f.seek( block*1024, 2 )
        # is sufficient
        if bytes + block * 1024 > 0:
            # Seek back a block
            f.seek(block * 1024, 2)
        else:
            # Seek to the beginning
            f.seek(0, 0)
        block_data = f.read(1024)
#        print 'read block: %s\n\n' % block_data
        data.append(block_data)
        newline = block_data.find('\n')
        if newline >= 0 and newline + 30 < len(block_data):
            ts = timestamp_of(block_data[newline + 1: newline + 29])
#            print 'earliest ts read: %s' % ts
        block -= 1
    
    if len(data) > 0:
        # Last block read (first in file) likely starts with a partial line. Get
        # rid of it.
        newline = data[-1].find('\n')
        if newline > 0:
            data[-1] = data[-1][newline + 1:]
    
    # Put data in file order
    data.reverse()
    
    return ''.join(data)


def timestamp_of(line):
    """Parses the timestamp of line and returns a datetime."""
    timestamp = line[:19]
    dt = datetime.strptime(timestamp, '%Y/%m/%d %H:%M:%S')
    return dt


main()
