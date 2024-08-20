================
publishing-tools
================

.. image:: https://img.shields.io/pypi/pyversions/publishing-tools.svg
    :target: https://img.shields.io/pypi/pyversions/publishing-tools
.. image:: https://badge.fury.io/py/publishing-tools.svg
    :target: https://badge.fury.io/py/publishing-tools

A set of tools that can be used for optimizing the publishing and verification of files and container archive releases.

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
The ``publish`` tool currently supports two types of ``sources``, i.e. either a file or (`Podman <https://docs.podman.io/en/latest/>`_) container image.
The selection can be controlled via the ``--publish-type`` argument that specifies what type of source should be published.

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
        destination           Path to the destination to publish to, can be either a directory .

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
                                Optional arguments to give the selected --signature-generator. (default: --sign --batch)
        --verbose, -v         Flag to enable verbose output. (default: False)

After a source has been published with a checksum and/or signature, the ``verify`` tool can be used to verify the integrity of the source.
Information for how this tool can be used can be discovered via the normal `--help` flag:

.. code-block:: bash

    verify --help
        [-h]
        [--verify-command {gpg}]
        [--verify-args VERIFY_ARGS]
        [--with-checksum]
        [--checksum-digest-file CHECKSUM_DIGEST_FILE]
        [--checksum-original-file CHECKSUM_ORIGINAL_FILE]
        [--checksum-algorithm {sha256,sha512,md5}]
        [--verbose]
        file
        key

        positional arguments:
        file                  Path to the file to verify.
        key                   The key that the --verify-command should use to verify the file with.

        options:
        -h, --help            show this help message and exit
        --verify-command {gpg}, -vc {gpg}
                                Command to verify the file with. Default is 'gpg'. (default: gpg)
        --verify-args VERIFY_ARGS, -va VERIFY_ARGS
                                Additional arguments to pass to the verify command. (default: --verify --batch --status-fd 0 --with-colons)
        --with-checksum, -wc  Whether to also verify a checksum file. (default: False)
        --checksum-digest-file CHECKSUM_DIGEST_FILE, -cdf CHECKSUM_DIGEST_FILE
                                Path to the file that contains the digest to validate against when --with-checksum is enabled. If none is provided, the checksum file will be assumed to be in the same directory as
                                the verify file with the same base name and the selected --checksum-algorithm extension. (default: None)
        --checksum-original-file CHECKSUM_ORIGINAL_FILE, -cof CHECKSUM_ORIGINAL_FILE
                                Path to the file to validate the --checksum-digest-file content against when --with-checksum is enabled. (default: None)
        --checksum-algorithm {sha256,sha512,md5}, -ca {sha256,sha512,md5}
                                Which checksum algorithm to use for verification when --with-checksum is enabled. (default: sha256)
        --verbose, -v         Flag to enable verbose output. (default: False)

--------
Examples
--------

The following examples illustrate how the tools can be used to publish a file, a container image, and how to verify the integrity of the published source.

Publishing a file
-----------------

Publishing a file with a checksum and signature, this requires that a valid signature key is available to sign the file with.
If GPG is used as the signature generator, the list of available keys can be discovered via the command ``gpg --list-keys``.

First we create a dummy file to publish:

.. code-block:: bash

    $ echo "Hello, World!" > /tmp/hello.txt

Then we can publish the file with a checksum and signature:

.. code-block:: bash

    $ publish --publish-type file --with-checksum --with-signature --signature-key <key_id_or_name> /tmp/hello.txt /tmp/hello_published.txt

This command will generate a checksum file and a signature file in the destination directory:

.. code-block:: bash

    $ ls /tmp/hello_published.txt*
    hello.txt
    hello.txt.gpg
    hello.txt.sha256

Publishing a container image
----------------------------

To publish a container image, the publish tool expects that the ``--publish-type container_image_archive`` flag is set.
In addition, the required positional `source` argument is expected to be set to the container image name or it's id.
Finally, the destination should be set to the path where the container image archive should be published.

.. code-block:: bash

    $ publish --publish-type container_image_archive --with-checksum --with-signature --signature-key <key_id_or_name> <container_image_name_or_id> /tmp/container_image.tar

The result of this command will be a container image archive, a checksum file which content is calculated based on the generated container image archive file,
and finally a version of the archived file that has been signed in the destination directory:

.. code-block:: bash

    $ ls /tmp/container_image.tar*
    container_image.tar
    container_image.tar.gpg
    container_image.tar.sha256


Verifing a file publication
---------------------------

To verify a signed file publication, the ``verify`` tool can be used.
The tool expects a path to the file that should be verified and a valid key that should be used to verify the file via the selected ``--verify-command``.
Currently the tool only supports GPG as the verification command, but this can be extended in the future.
In addition to signature verification, the tool can also verify a checksum file if the ``--with-checksum`` flag is set.
When this flag is set, the tool requires that both the signature and checksum checks will pass for the verification to be successful.

An example of a simple verification of a signed file with an associated checksum file can be seen below:

.. code-block:: bash

    $ verify --with-checksum /tmp/hello_published.txt.gpg <key_id_or_name>

With this command, the verify tool will automatically try to discover the checksum digest file and the original published file in the same directory as the file to verify.
If the expected files are not present in the same directory, then the ``--checksum-digest-file``/``--checksum-original-file`` arguments can be used to specify the paths to the required files.

The result of the verification will be a message that indicates if the verification was successful or not.

Verifying a container image publication
---------------------------------------

Similarly to the file verification, the container image verification can be done with the ``verify`` tool.
After a container image achive has been published, the verification can be done with the following command:

.. code-block:: bash

    $ verify --with-checksum /tmp/container_image.tar.gpg <key_id_or_name>

The expectations for the verification are the same as for the file verification, i.e. that the signature and checksum checks will pass for the verification to be successful.
