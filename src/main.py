import convert
import fileio
import fileutil
import os
import sys
import textnode


def main():
    print(os.getcwd())
    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    else:
        basepath = "/"
    fileio.copy("static", "docs")
    convert.generate_pages_recursive(basepath, "content", "template.html", "docs")

main()

