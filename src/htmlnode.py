class HTMLNode():
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        if self.props is None:
            return ""
        return " ".join(f"{key}=\"{value}\"" for (key, value) in self.props.items())

    def __repr__(self):
        res = f"<{self.tag} {self.props_to_html}>"
        if self.value is not None:
            res += f"{self.value}"
        else:
            for child in self.children:
                res += f"\n{child}"
        res += f"\n</{self.tag}>"


class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
         super().__init__(tag, value, children=None, props=props)

    def to_html(self):
        if self.value is None:
            raise ValueError("All leaf nodes must have a value.")
        if self.tag is None:
            return self.value
        else:
            return f"<{self.tag} {self.props_to_html()}>{self.value}</{self.tag}>"