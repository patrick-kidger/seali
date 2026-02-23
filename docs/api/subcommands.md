# Subcommands

Subcommands may be implemented with [`seali.group`][]. (This is actually just a [`seali.command`][] whose implementation checks the first positional argument, and then redispatches to another command. It's just a convenient helper, not anything special.)

::: seali.group
