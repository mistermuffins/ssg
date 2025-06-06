import convert
import fileio
import fileutil
import os
import textnode


def main():
    print(os.getcwd())
    # fileutil.rm_children("public")
    fileio.copy("static", "public")
    convert.generate_pages_recursive("content", "template.html", "public")

main()

