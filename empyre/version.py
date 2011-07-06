MAJOR = 0
MINOR = 5
PATCH = 0
RELEASE = ''

def version():
    v = "%d.%d.%d" % (MAJOR, MINOR, PATCH)
    if RELEASE:
        return v + "-" + RELEASE
    else:
        return v
