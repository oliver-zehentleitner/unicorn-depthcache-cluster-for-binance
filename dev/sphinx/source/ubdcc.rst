ubdcc CLI
=========

The ``ubdcc`` command-line interface manages a local UBDCC cluster (start,
status, stop, credentials). See the ``start`` subcommand for the interactive
shell commands available at runtime (``add-dcn``, ``remove-dcn``, ``status``,
``restart``, ``stop``, ``help``).

.. autoprogram:: ubdcc.cli:build_parser()
   :prog: ubdcc
