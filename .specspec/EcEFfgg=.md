---
id: EcEFfgg=
type: requirement
parents:
- 1GJRSPU=
---
# Tolerate newline layout while preserving Markdown matching structure

The default replacement comparison equates LF, CRLF and bare CR line endings.
Within ordinary Markdown paragraph text, a parser-recognized soft line break can
match one ordinary ASCII space, in either direction. Other spaces, tabs, paragraph
boundaries and indentation retain their literal significance. Headings, table rows,
code blocks, inline code, HTML syntax and explicit Markdown hard breaks keep their
structural newlines. Container markers and continuation indentation remain literal;
only safely source-mapped paragraph soft breaks participate in wrapping tolerance.

Recognize paragraph and inline structure with CommonMark plus table support through
markdown-it-py. Load the parser on demand for wrapping-aware replacements, retaining
ordinary CLI/host startup and transport owners. Compare raw source text, rather than
rendered or decoded Markdown. Preserve case, Unicode normalization, punctuation and
all characters outside the allowed newline equivalences.

Consider line-ending-only and prose-wrapping matches together. Uniqueness covers all
admissible original spans, even when one has an exact literal spelling. Coalesce the
same original span seen through multiple comparison views. Map comparison positions
back to exact original character boundaries before overlap checks, byte-size checks
and construction. Ambiguous matches reject rather than preferring an exact-layout
occurrence. Every pair still refers to the same original body.

NEW retains literal content and unmatched logical characters remain unchanged.
Comparison normalization preserves paragraph layout. Serialization adapts newline
encoding to the target document; equal OLD/NEW can change a matched prose wrap.
Apply bounds to the actual target-style replacement result and serialized node,
with bounded construction and original-span overlap/uniqueness checks.

Bound Markdown line/token analysis, inline nesting and candidate-comparison work.
Exhausted analysis rejects the invocation explicitly instead of selecting from an
incomplete match set. Source mappings must be proved before allowing soft-break
folding; unmapped structure retains line-ending-only matching. Existing locks, input
budgets, schema checks, graph validity, consent and recoverability remain unchanged.
