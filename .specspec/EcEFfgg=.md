---
id: EcEFfgg=
type: requirement
parents:
- 1GJRSPU=
---
# Match a passage across different line ends and prose wrapping while Markdown structure stays literal

The comparison of a replacement treats LF, CRLF and a lone CR as the same line end. Inside the text of an ordinary Markdown paragraph, a soft line break that the parser recognizes matches one ordinary ASCII space, and a space matches such a break. Every other space, tabs, the boundaries of paragraphs and indentation count literally. Headings, table rows, code blocks, inline code, HTML and explicit hard breaks keep their newlines as structure. The markers of containers such as lists and quotes and the indentation of continuation lines are literal. Only a soft break of a paragraph whose place in the source is mapped safely takes part in the tolerance for wrapping.

Paragraphs and inline structure are recognized by markdown-it-py with CommonMark and tables. The parser is loaded on demand, when a replacement needs the comparison of wrapping, and the ordinary start of the command line and of the editors' channel runs without it. The comparison works on the raw source text of the Markdown, as it is written. Case, punctuation, the Unicode normalization form of the text and every character outside the permitted equivalences of newlines are compared exactly.

Matches that differ in line ends alone and matches that differ in wrapping are considered together. Uniqueness covers every span of the original that the rules admit, also when one of them has the exact spelling of OLD, and an ambiguous OLD is rejected whichever of its matches has the exact layout. One span of the original that is seen through several views of the comparison counts once. Positions of the comparison are mapped back to exact character boundaries of the original before overlap is checked, bytes are counted and the result is built. Every pair refers to the same original body.

NEW keeps its literal content, and the logical characters outside the matches stay unchanged. The normalization that the comparison uses leaves the layout of the paragraphs in the body as it is. Serialization adapts the newline encoding to the document, and a pair with the same OLD and NEW can change the wrapping of the matched prose. The size limits apply to the actual replacement result in the newline style of the document and to the serialized node. The result is built only after a conservative bound on its size has been checked, and overlap and uniqueness are checked on spans of the original.

The analysis of Markdown lines and tokens, the nesting of inline structure and the work of comparing candidates are limited. A match is chosen from a complete analysis alone: an invocation whose analysis reaches a limit is rejected with an explicit error. A soft break is folded into a space only where its mapping to the source is proved, and structure without such a mapping is matched by the equivalence of line ends alone.
