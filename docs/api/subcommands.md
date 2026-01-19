# Subcommands

Subcommands may be implemented with [`tinycli.group`][]. (This is actually just a [`tinycli.command`][] whose implementation checks the first positional argument, and then redispatches to another command. It's just a convenient helper, not anything special.)

::: tinycli.group
