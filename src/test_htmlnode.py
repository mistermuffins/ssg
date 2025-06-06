from htmlnode import HTMLNode, LeafNode, ParentNode
import unittest


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_eq(self):
        node = HTMLNode("p", "this is text")
        self.assertEqual(node.props_to_html(), "")


    def test_props_to_html_props(self):
        node = HTMLNode("p", "this is some text", props={"href": "https://www.boot.dev"})

        self.assertEqual(node.props_to_html(), " href=\"https://www.boot.dev\"")

    def test_to_html(self):
        node = HTMLNode("p")

        with self.assertRaises(NotImplementedError):
            node.to_html()

class TestLeafNode(unittest.TestCase):
    def test_to_html_no_tag(self):
        node = LeafNode(None, "This is a paragraph of text.")

        self.assertEqual(node.to_html(), "This is a paragraph of text.")

    def test_to_html_no_value(self):
        node = LeafNode("p", None)

        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_props(self):
        node = LeafNode("p", "This is some text", {"href": "https://www.boot.dev"})

        self.assertEqual(node.to_html(), "<p href=\"https://www.boot.dev\">This is some text</p>")


class TestParentNode(unittest.TestCase):
    def test_to_html_no_tag(self):
        node = ParentNode(None, [])

        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_no_children(self):
        node = ParentNode("div", [])

        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_child(self):
        node = ParentNode("div", [LeafNode("p", "123")])

        self.assertEqual(node.to_html(), "<div><p>123</p></div>")

    def test_to_html_children(self):
        node = ParentNode("div", [LeafNode("p", "123"), LeafNode("p", "456")])

        self.assertEqual(node.to_html(), "<div><p>123</p><p>456</p></div>")


if __name__ == "__main__":
    unittest.main()
