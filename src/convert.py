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

def markdown_to_blocks(markdown):
    blocks = []
    new_block = []
    for line in markdown.splitlines():
        if line == "":
            if new_block:
                blocks.append("\n".join(new_block))
            new_block = []
        else:
            new_block.append(line)
    if new_block:
        blocks.append("\n".join(new_block))
    return blocks

def block_to_block_type(block):
    if re.match(r"#{1,6} .+$", block):
        return "heading"
    elif re.match(r"```.*```", block, flags=re.DOTALL):
        return "code"
    elif block[0] == ">":
        for line in block.splitlines():
            if not line:
                continue
            if line[0] != ">":
                raise ValueError("quote block must all start with >")
        return "quote"
    elif block[0] == "*" or block[0] == "-":
        for line in block.splitlines():
            if not line:
                continue
            if (line[0] != "*" and line[0] != "-") or line[1] != " ":
                raise ValueError("unordered lists must start with \"*\" or \"-\" and a space")
        return "unordered"
    elif block[:2] == "1.":
        i = 1
        for line in block.splitlines():
            if not line:
                continue
            if line[0] != str(i) or line[1:3] != ". ":
                raise ValueError("ordered list must start with a number followed by a period and a space")
            i += 1
        return "ordered"
    else:
        return "paragraph"
        

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    html_nodes = []
    for block in blocks:
        block_type = block_to_block_type(block)

        if block_type == "heading":
            hashes, title = block.split(maxsplit=1)
            html_nodes.append(LeafNode(f"h{len(hashes)}", title))
        elif block_type == "code":
            code_node = LeafNode("code", block[3:-3])
            pre_node = ParentNode("pre", [code_node])
            html_nodes.append(pre_node)
        elif block_type == "quote":
            quoted = "\n".join(map(lambda line: line[2:], block.split("\n")))
            html_nodes.append(LeafNode("blockquote", quoted))
        elif block_type == "unordered":
            children = []
            for line in block.split("\n"):
                li_node = LeafNode("li", line[2:])
                children.append(li_node)
            html_nodes.append(ParentNode("ul", children))
        elif block_type == "ordered":
            children = []
            for line in block.split("\n"):
                li_node = LeafNode("li", line[3:])
                children.append(li_node)
            html_nodes.append(ParentNode("ol", children))
        elif block_type == "paragraph":
            html_nodes.append(LeafNode("p", block))
    return html_nodes
