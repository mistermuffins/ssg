import convert
import fileio
import textnode

def main():
    fileio.copy("static", "public")
    convert.generate_page("content/index.md", "template.html", "public/index.html")

main()

