import unittest
from inline_markdown import split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link
from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_code_block(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(result, [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ])

    def test_bold(self):
        node = TextNode("This is text with a **bolded phrase** in the middle", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(result, [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("bolded phrase", TextType.BOLD),
            TextNode(" in the middle", TextType.TEXT),
        ])

    def test_italic(self):
        node = TextNode("This is _italic_ text", TextType.TEXT)
        result = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(result, [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
        ])

    def test_delimiter_at_start(self):
        node = TextNode("`code` at start", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(result, [
            TextNode("code", TextType.CODE),
            TextNode(" at start", TextType.TEXT),
        ])

    def test_delimiter_at_end(self):
        node = TextNode("text at end `code`", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(result, [
            TextNode("text at end ", TextType.TEXT),
            TextNode("code", TextType.CODE),
        ])

    def test_multiple_delimiters(self):
        node = TextNode("a `b` c `d` e", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(result, [
            TextNode("a ", TextType.TEXT),
            TextNode("b", TextType.CODE),
            TextNode(" c ", TextType.TEXT),
            TextNode("d", TextType.CODE),
            TextNode(" e", TextType.TEXT),
        ])

    def test_non_text_node_passthrough(self):
        node = TextNode("already bold", TextType.BOLD)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(result, [TextNode("already bold", TextType.BOLD)])

    def test_mixed_node_list(self):
        nodes = [
            TextNode("plain ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" and `code` here", TextType.TEXT),
        ]
        result = split_nodes_delimiter(nodes, "`", TextType.CODE)
        self.assertEqual(result, [
            TextNode("plain ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" here", TextType.TEXT),
        ])

    def test_missing_closing_delimiter_raises(self):
        node = TextNode("missing `closing delimiter", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_empty_text_node(self):
        node = TextNode("", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(result, [])


class TestExtractMarkdownImages(unittest.TestCase):
    def test_extract_single_image(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_multiple_images(self):
        text = "![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        matches = extract_markdown_images(text)
        self.assertListEqual(
            [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")],
            matches,
        )

    def test_no_images(self):
        matches = extract_markdown_images("Just plain text with no images.")
        self.assertListEqual([], matches)

    def test_does_not_match_links(self):
        matches = extract_markdown_images("A [link](https://example.com) should not match.")
        self.assertListEqual([], matches)

    def test_empty_alt_text(self):
        matches = extract_markdown_images("![](https://example.com/img.png)")
        self.assertListEqual([("", "https://example.com/img.png")], matches)


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_extract_single_link(self):
        matches = extract_markdown_links("A link [to boot dev](https://www.boot.dev) here.")
        self.assertListEqual([("to boot dev", "https://www.boot.dev")], matches)

    def test_extract_multiple_links(self):
        text = "[to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        matches = extract_markdown_links(text)
        self.assertListEqual(
            [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")],
            matches,
        )

    def test_no_links(self):
        matches = extract_markdown_links("Just plain text.")
        self.assertListEqual([], matches)

    def test_does_not_match_images(self):
        matches = extract_markdown_links("An ![image](https://example.com/img.png) should not match.")
        self.assertListEqual([], matches)

    def test_empty_anchor_text(self):
        matches = extract_markdown_links("[](https://example.com)")
        self.assertListEqual([("", "https://example.com")], matches)


if __name__ == "__main__":
    unittest.main()