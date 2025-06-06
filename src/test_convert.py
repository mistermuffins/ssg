import unittest

import convert
from convert import text_node_to_html_node, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes
from textnode import TextNode, TextType


class TestConvert(unittest.TestCase):
    def test_convert_normal(self):
        node = TextNode("blah", TextType.NORMAL)

        self.assertEqual(text_node_to_html_node(node).to_html(), "blah")

    def test_convert_bold(self):
        node = TextNode("blah", TextType.BOLD)

        self.assertEqual(text_node_to_html_node(node).to_html(), "<b>blah</b>")

    def test_convert_italic(self):
        node = TextNode("blah", TextType.ITALIC)

        self.assertEqual(text_node_to_html_node(node).to_html(), "<i>blah</i>")

    def test_convert_code(self):
        node = TextNode("blah", TextType.CODE)

        self.assertEqual(text_node_to_html_node(node).to_html(), "<code>blah</code>")

    def test_convert_link(self):
        node = TextNode("blah", TextType.LINK, "https://www.boot.dev")

        self.assertEqual(text_node_to_html_node(node).to_html(), "<a href=\"https://www.boot.dev\">blah</a>")

    def test_convert_image(self):
        node = TextNode("blah", TextType.IMAGE, "https://www.boot.dev/boots.png")

        self.assertEqual(text_node_to_html_node(node).to_html(), "<img src=\"https://www.boot.dev/boots.png\" alt=\"blah\"></img>")

    def test_split_nodes_delimiter(self):
        node = TextNode("This is text with a `code block` word", TextType.NORMAL)

        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)

        self.assertEqual(new_nodes[0].text_type, TextType.NORMAL)
        self.assertEqual(new_nodes[0], TextNode("This is text with a ", TextType.NORMAL))
        self.assertEqual(new_nodes[1].text_type, TextType.CODE)
        self.assertEqual(new_nodes[1], TextNode("code block", TextType.CODE))
        self.assertEqual(new_nodes[2].text_type, TextType.NORMAL)
        self.assertEqual(new_nodes[2], TextNode(" word", TextType.NORMAL))


    def test_extract_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        groups = extract_markdown_images(text)
        self.assertEqual(groups[0][0], "rick roll")
        self.assertEqual(groups[0][1], "https://i.imgur.com/aKaOqIh.gif")
        self.assertEqual(groups[1][0], "obi wan")
        self.assertEqual(groups[1][1], "https://i.imgur.com/fJRm4Vk.jpeg")

    def test_extract_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        groups = extract_markdown_links(text)
        self.assertEqual(groups[0][0], "to boot dev")
        self.assertEqual(groups[0][1], "https://www.boot.dev")
        self.assertEqual(groups[1][0], "to youtube")
        self.assertEqual(groups[1][1], "https://www.youtube.com/@bootdotdev")

    def test_split_nodes_image(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        nodes = split_nodes_image([TextNode(text, TextType.NORMAL)])
        self.assertEqual(nodes[0].text_type, TextType.NORMAL)
        self.assertEqual(nodes[1].text_type, TextType.IMAGE)
        self.assertEqual(nodes[2].text_type, TextType.NORMAL)
        self.assertEqual(nodes[3].text_type, TextType.IMAGE)

    def test_split_nodes_link(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        nodes = split_nodes_link([TextNode(text, TextType.NORMAL)])
        self.assertEqual(nodes[0].text_type, TextType.NORMAL)
        self.assertEqual(nodes[1].text_type, TextType.LINK)
        self.assertEqual(nodes[2].text_type, TextType.NORMAL)
        self.assertEqual(nodes[3].text_type, TextType.LINK)

    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"

        nodes = text_to_textnodes(text)

        expected = [
                TextNode("This is ", TextType.NORMAL),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.NORMAL),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.NORMAL),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.NORMAL),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.NORMAL),
                TextNode("link", TextType.LINK, "https://boot.dev"),
                ]

        self.assertEqual(len(nodes), len(expected))

        for i in range(len(nodes)):
            self.assertEqual(nodes[i], expected[i])

    def test_markdown_to_blocks(self):
        input = """# This is a heading

This is a paragraph of text. It has some **bold** and *italic* words inside of it.

* This is the first list item in a list block
* This is a list item
* This is another list item"""

        output = convert.markdown_to_blocks(input)

        self.assertEqual(len(output), 3)
        self.assertEqual(output[0], "# This is a heading")
        self.assertEqual(output[1], "This is a paragraph of text. It has some **bold** and *italic* words inside of it.")
        self.assertEqual(output[2], "* This is the first list item in a list block\n* This is a list item\n* This is another list item")

    def test_block_to_block_type_header(self):
        input = "### this is a heading"

        output = convert.block_to_block_type(input)

        self.assertEqual(output, "heading")

    def test_block_to_block_type_code(self):
        input = """```
this is a some code
line 2 of code
```"""

        output = convert.block_to_block_type(input)

        self.assertEqual(output, "code")

    def test_block_to_block_type_quote(self):
        input = """> four score
> and twenty years ago
> our forefathers"""

        output = convert.block_to_block_type(input)

        self.assertEqual(output, "quote")

    def test_block_to_block_type_not_quote(self):
        input = """> four score
> and twenty years ago
our forefathers"""

        with self.assertRaises(ValueError):
            output = convert.block_to_block_type(input)

    def test_block_to_block_type_unordered(self):
        input = """* four score
- and twenty years ago
* our forefathers"""

        output = convert.block_to_block_type(input)

        self.assertEqual(output, "unordered")

    def test_block_to_block_type_not_unordered(self):
        input = """* four score
- and twenty years ago
*our forefathers"""

        with self.assertRaises(ValueError):
            output = convert.block_to_block_type(input)

    def test_block_to_block_type_ordered(self):
        input = """1. four score
2. and twenty years ago
3. our forefathers"""

        output = convert.block_to_block_type(input)

        self.assertEqual(output, "ordered")

    def test_block_to_block_type_not_ordered(self):
        input = """1. four score
4. and twenty years ago
3. our forefathers"""


        with self.assertRaises(ValueError):
            output = convert.block_to_block_type(input)

    def test_markdown_to_html_heading(self):
        input = "# heading 1"

        output = convert.markdown_to_html_node(input)

        self.assertEqual(output.to_html(), "<div><h1>heading 1</h1></div>")

    def test_markdown_to_html_code(self):
        input = """```
this is some
code
blah
```"""

        output = convert.markdown_to_html_node(input)

        self.assertEqual(output.to_html(), """<div><pre><code>
this is some
code
blah
</code></pre></div>""")

    def test_markdown_to_html_quote(self):
        input = """> this is a quote
> four score and
> seventy years ago"""

        output = convert.markdown_to_html_node(input)

        self.assertEqual(output.to_html(), """<div><blockquote>this is a quote
four score and
seventy years ago</blockquote></div>""")

    def test_markdown_to_html_unordered(self):
        input = """* this is item 1
* this is item 2"""

        output = convert.markdown_to_html_node(input)

        self.assertEqual(output.to_html(), """<div><ul><li>this is item 1</li><li>this is item 2</li></ul></div>""")

    def test_markdown_to_html_ordered(self):
        input = """1. this is item 1
2. this is item 2"""

        output = convert.markdown_to_html_node(input)

        self.assertEqual(output.to_html(), """<div><ol><li>this is item 1</li><li>this is item 2</li></ol></div>""")

    def test_markdown_to_html_paragraph(self):
        input = """this is some text
blah blah"""

        output = convert.markdown_to_html_node(input)

        self.assertEqual(output.to_html(), """<div><p>this is some text
blah blah</p></div>""")


    def test_extract_title(self):
        input = """# this is the title"""

        output = convert.extract_title(input)

        self.assertEqual(output, "this is the title")

    def test_extract_title2(self):
        input = """blah blah

## this is not the title

# this is the title

# another title"""

        with self.assertRaises(ValueError):
            convert.extract_title(input)


if __name__ == "__main__":
    unittest.main()
