import re

from htmlnode import LeafNode, ParentNode
from textnode import TextNode, TextType

def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.NORMAL:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, props={"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", "", props={"src": text_node.url, "alt": text_node.text})
        case _:
            raise ValueError("Can't convert text to html.")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    res = []
    for node in old_nodes:
        if node.text_type != TextType.NORMAL:
            res.append(node)
            continue
        segments = node.text.split(delimiter)
        if len(segments) % 2 == 0:
            raise ValueError("Invalid markdown syntax. Uneven number of delimiters")

        for i in range(len(segments)):
            if i % 2 == 0:
                res.append(TextNode(segments[i], TextType.NORMAL))
            else:
                res.append(TextNode(segments[i], text_type))

    return res

def extract_markdown_images(text):
    regex = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(regex, text)
    
def extract_markdown_links(text):
    regex = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(regex, text)

def split_nodes_image(old_nodes):
    new_nodes = []
    regex = r"(!\[[^\[\]]*\]\([^\(\)]*\))"
    gre = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    for node in old_nodes:
        if node.text_type != TextType.NORMAL:
            new_nodes.append(node)
            continue

        text = node.text
        while re.search(regex, text):
            before, image, after = re.split(regex, text, maxsplit=1)
            if before:
                new_nodes.append(TextNode(before, TextType.NORMAL))
            m = re.match(gre, image)
            if m:
                new_nodes.append(TextNode(m.group(1), TextType.IMAGE, url=m.group(2)))
            text = after
        if text:
            new_nodes.append(TextNode(text, TextType.NORMAL))
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    regex = r"((?<!!)\[[^\[\]]*\]\([^\(\)]*\))"
    gre = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    for node in old_nodes:
        if node.text_type != TextType.NORMAL:
            new_nodes.append(node)
            continue

        text = node.text
        while re.search(regex, text):
            before, link, after = re.split(regex, text, maxsplit=1)
            if before:
                new_nodes.append(TextNode(before, TextType.NORMAL))
            m = re.match(gre, link)
            if m:
                new_nodes.append(TextNode(m.group(1), TextType.LINK, url=m.group(2)))
            text = after
        if text:
            new_nodes.append(TextNode(text, TextType.NORMAL))
    return new_nodes

def text_to_textnodes(text):
    textnode = TextNode(text, TextType.NORMAL)
    nodes = split_nodes_delimiter([textnode], "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)

    return nodes
