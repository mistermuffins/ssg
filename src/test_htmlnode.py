from htmlnode import HTMLNode
import unittest


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_eq(self):
        node = HTMLNode("p", "this is text")
        self.assertEqual(node.props_to_html(), "")


if __name__ == "__main__":
    unittest.main()
