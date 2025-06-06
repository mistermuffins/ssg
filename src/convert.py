import os
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
    """Takes a list of TextNodes and splits off nodes containing a particular text type."""
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
    nodes = [TextNode(text, TextType.NORMAL)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
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
    elif block[:2] == "* " or block[:2] == "- ":
        for line in block.splitlines():
            if not line:
                continue
            if line[:2] != "* " and line[:2] != "- ":
                raise ValueError("unordered lists must start with \"* \" or \"- \"")
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


def text_to_html_nodes(text):
    text_nodes = text_to_textnodes(text)
    return [text_node_to_html_node(text_node) for text_node in text_nodes]

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    html_nodes = []
    for block in blocks:
        block_type = block_to_block_type(block)

        if block_type == "heading":
            hashes, title = block.split(maxsplit=1)
            html_nodes.append(ParentNode(f"h{len(hashes)}", text_to_html_nodes(title)))
        elif block_type == "code":
            code_node = ParentNode("code", text_to_html_nodes(block[3:-3]))
            pre_node = ParentNode("pre", [code_node])
            html_nodes.append(pre_node)
        elif block_type == "quote":
            quoted = "\n".join(map(lambda line: line[2:], block.split("\n")))
            html_nodes.append(ParentNode("blockquote", text_to_html_nodes(quoted)))
        elif block_type == "unordered":
            children = []
            for line in block.split("\n"):
                li_node = ParentNode("li", text_to_html_nodes(line[2:]))
                children.append(li_node)
            html_nodes.append(ParentNode("ul", children))
        elif block_type == "ordered":
            children = []
            for line in block.split("\n"):
                li_node = ParentNode("li", text_to_html_nodes(line[3:]))
                children.append(li_node)
            html_nodes.append(ParentNode("ol", children))
        elif block_type == "paragraph":
            html_nodes.append(ParentNode("p", text_to_html_nodes(block)))
    return ParentNode("div", html_nodes)

def extract_title(markdown):
    header = markdown.split('\n')[0]
    if header[0] != '#':
        raise ValueError('title not found')

    return header[2:].strip()

def generate_page(basepath, from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path) as f:
        markdown = f.read()

    with open(template_path) as f:
        template = f.read()

    html = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)

    output = template.replace("{{ Title }}", title)
    output = output.replace("{{ Content }}", html)
    output = output.replace("href=\"/", f"href=\"{basepath}")
    output = output.replace("src=\"/", f"src=\"{basepath}")

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(dest_path, 'w') as f:
        f.write(output)

def generate_pages_recursive(basepath, dir_path_content, template_path, dest_dir_path):
    for entry in os.scandir(dir_path_content):
        if entry.is_file() and entry.name[-3:] == ".md":
            generate_page(basepath, entry.path, template_path, os.path.join(dest_dir_path, entry.name)[:-3] + ".html")
        elif entry.is_dir():
            generate_pages_recursive(basepath, entry.path, template_path, os.path.join(dest_dir_path, entry.name))