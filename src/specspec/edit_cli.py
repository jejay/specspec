"""Parse only editing command chains before invoking any writer or body reader."""

from __future__ import annotations

from contextlib import ExitStack

import click

from .batch import MAX_BATCH_BYTES, MAX_EDITS
from .model import ID_RE

EDIT_COMMANDS = frozenset({"add", "update", "delete"})
EDIT_FLAGS = ("dry_run", "require_valid", "yes", "as_json")


def split_edits(group, parent, argv):
    """Use declared option arities, not bare-word splitting inside option values."""
    try:
        size = sum(len(arg.encode("utf8")) for arg in argv)
    except UnicodeError as error:
        raise click.UsageError("Editing arguments must be valid UTF-8 text.", parent) from error
    if size > MAX_BATCH_BYTES:
        raise click.UsageError("Editing arguments exceed 16 MiB.", parent)
    steps, index = [], 0
    while index < len(argv):
        name, start = argv[index], index + 1
        if name not in EDIT_COMMANDS:
            raise click.UsageError("Only add, update and delete may be combined.", parent)
        command = group.get_command(parent, name)
        options = {
            spelling: param
            for param in command.get_params(parent)
            if isinstance(param, click.Option)
            for spelling in [*param.opts, *param.secondary_opts]
        }
        index, positional = start, False
        while index < len(argv):
            arg = argv[index]
            if arg in group.commands:
                if arg not in EDIT_COMMANDS:
                    raise click.UsageError(
                        f"Only add, update and delete may be combined; got {arg}.", parent
                    )
                break
            index += 1
            if not positional:
                if arg == "--":
                    positional = True
                else:
                    spelling, separator, _ = arg.partition("=")
                    option = options.get(spelling)
                    if option is not None and not option.is_flag:
                        # --option=value supplies one value, not an entire multi-value pair.
                        remaining = option.nargs - bool(separator)
                        index = min(len(argv), index + remaining)
                    # Attached short option values, such as -madd, occupy this token
                    # only. Click subsequently validates all spellings and values.
        steps.append((name, argv[start:index]))
        if len(steps) > MAX_EDITS:
            raise click.UsageError("An editing invocation accepts at most 1024 steps.", parent)
    return steps


class CanonicalIdCommand(click.Command):
    """A complete node ID is data, even if it resembles a short-option cluster."""

    def make_parser(self, ctx):
        parser = super().make_parser(ctx)
        process_options = parser._process_opts

        def process(arg, state):
            if ID_RE.fullmatch(arg):
                state.largs.append(arg)
            else:
                process_options(arg, state)

        parser._process_opts = process
        return parser


class EditInvocation(click.Command):
    """A root edit dispatches through complete preflight, not Click's eager chain writes."""

    def __init__(self, name, command, execute):
        # Preserve Click's ordinary option metadata, including shell completion.
        super().__init__(name, params=command.params)
        self.execute = execute

    def parse_args(self, ctx, args):
        ctx.args = list(args)
        return ctx.args

    def invoke(self, ctx):
        parent = ctx.parent
        steps = split_edits(parent.command, parent, [self.name, *ctx.args])
        with ExitStack() as stack:
            contexts = [
                stack.enter_context(
                    parent.command.get_command(parent, name).make_context(name, args, parent=parent)
                )
                for name, args in steps
            ]
            if len(contexts) == 1:
                return contexts[0].command.invoke(contexts[0])
            flags = {flag: any(c.params[flag] for c in contexts) for flag in EDIT_FLAGS}
            return self.execute(ctx.obj, [(c.info_name, c.params) for c in contexts], **flags)
