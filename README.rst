================
publishing-tools
================

.. image:: https://img.shields.io/pypi/pyversions/publishing-tools.svg
    :target: https://img.shields.io/pypi/pyversions/publishing-tools
.. image:: https://badge.fury.io/py/publishing-tools.svg
    :target: https://badge.fury.io/py/publishing-tools

A set of tools that can be used for publishing packages and container images.

------------
Installation
------------

.. code-block:: bash

    pip install publishing-tools

-----
Usage
-----

The package provides a set of complementary tools that can be used as part of publishing packages and container images.
In particular, the package can help with optimizing the workflow for signing, checksumming, and verifying the integrity of artifacts to be published.

The package provides the ``publish``, ``sign``, and ``verify`` tools:

The overall ``publish`` tool can be used to publish a source to a destination, optionally with an associated checksum and/or signature file.
The ``publish`` tool currently supports two types of ``sources``, i.e. either a file or (`Podman <https://docs.podman.io/en/latest/>`_) container image. The selection can be controlled
via the ``--publish-type`` argument that specifies what type of source should be published.

.. code-block:: bash

    $ publish --help
        [-h]
        [--publish-type {file,container_image_archive}]
        [--with-checksum]
        [--checksum-algorithm {sha256,sha512,md5}]
        [--with-signature]
        [--signature-generator {gpg}]
        [--signature-key SIGNATURE_KEY]
        [--signature-args SIGNATURE_ARGS]
        [--verbose]
        source
        destination

        positional arguments:
        source                The source input to publish.
        destination           Path to the destination to publish to.

        options:
        -h, --help            show this help message and exit
        --publish-type {file,container_image_archive}, -pt {file,container_image_archive}
        --with-checksum, -wc  Whether to also publish a checksum file in the destination directory. (default: False)
        --checksum-algorithm {sha256,sha512,md5}, -ca {sha256,sha512,md5}
                                Which checksum algorithm to use when --with-checksum is enabled. (default: sha256)
        --with-signature, -ws
                                Whether to also publish a signed edition of the source to the specified destination directory. (default: False)
        --signature-generator {gpg}, -sg {gpg}
                                Which signaturer to use when --with-signature is enabled. (default: gpg)
        --signature-key SIGNATURE_KEY, -sk SIGNATURE_KEY
                                Which key should be used to sign with when --with-signature is enabled. (default: None)
        --signature-args SIGNATURE_ARGS, -sa SIGNATURE_ARGS
                                Optional arguments to give the selected --signature-generator. (default: --sign)
        --verbose, -v         Flag to enable verbose output. (default: False)


After a source has been published with a checksum and/or signature, the ``verify`` tool can be used to verify the integrity of the source.

.. code-block:: bash

    $ verify --help
        [-h]
        [--verify-command {gpg}]
        [--verify-args VERIFY_ARGS]
        [--verbose]
        file
        key

        positional arguments:
        file                  Path to the file to verify
        key                   Path to the key to verify the file with

        options:
        -h, --help            show this help message and exit
        --verify-command {gpg}, -vc {gpg}
                                Command to verify the file with. Default is 'gpg'. (default: gpg)
        --verify-args VERIFY_ARGS, -va VERIFY_ARGS
                                Additional arguments to pass to the verify command. (default: --verify --batch --status-fd 0 --with-colons)
        --verbose, -v         Flag to enable verbose output. (default: False)




-----------
Extra Tools
-----------