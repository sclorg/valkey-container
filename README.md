Valkey container image
=====================

[![Build and push images to Quay.io registry](https://github.com/sclorg/valkey-container/actions/workflows/build-and-push.yml/badge.svg)](https://github.com/sclorg/valkey-container/actions/workflows/build-and-push.yml)

Images available on Quay are:
* CentOS Stream 10 [valkey-6](https://quay.io/repository/sclorg/valkey-7-c10s)
* Fedora [valkey-7](https://quay.io/repository/fedora/valkey-7)
* Fedora [valkey-8](https://quay.io/repository/fedora/valkey-8)

All published images are multi-arch (amd64 and arm64).

This repository contains Dockerfiles for valkey container image.
Users can choose between RHEL, Fedora and CentOS Stream based images.

For more information about contributing, see
[the Contribution Guidelines](https://github.com/sclorg/welcome/blob/master/contribution.md).
For more information about concepts used in these container images, see the
[Landing page](https://github.com/sclorg/welcome).


Versions
--------
valkey version currently provided are:
* [valkey-7](7)
* [valkey-8](8)

RHEL versions currently supported:
* RHEL10

CentOS Stream versions currently supported are:
* CentOS Stream 10


Installation
------------
To build a valkey image, choose either the CentOS Stream:
    ```

*  **CentOS Stream based image**

    This image is available on quay.io. To download it run:

    ```
    $ podman pull quay.io/sclorg/valkey-7-c10s
    ```

    To build a valkey image from scratch run:

    ```
    $ git clone --recursive https://github.com/sclorg/valkey-container.git
    $ cd valkey-container
    $ git submodule update --init
    $ make build TARGET=c10s VERSIONS=7
    ```

Note: while the installation steps are calling `podman`, you can replace any such calls by `docker` with the same arguments.

**Notice: By omitting the `VERSIONS` parameter, the build/test action will be performed
on all provided versions of valkey.**


Usage
-----

For information about usage of Dockerfile for valkey 7,
see [usage documentation](7).

For information about usage of Dockerfile for valkey 8,
see [usage documentation](8).

Test
----
Users can choose between testing a valkey test application based on CentOS Stream image.

*  **CentOS Stream based image**

    ```
    $ cd valkey-container
    $ git submodule update --init
    $ make test TARGET=c10s VERSIONS=7
    ```

**Notice: By omitting the `VERSIONS` parameter, the build/test action will be performed
on all provided versions of valkey.**
