from podman import PodmanClient
from podman.domain.images import Image
from podman.errors import ImageNotFound, APIError, BuildError

from publish.utils.io import i_write


def container_publish_to_registry(
    source, destination, container_client_kwargs=None, verbose=False
):
    """
    Publishes a container image from source to destination.
    The source is the image name and tag of the pre-built image that is to be published.
    The destination is the registry URL and the image name and tag to publish the image to.
    """
    image = get_image(source, container_client_kwargs=container_client_kwargs)
    if not image:
        return False

    # PodmanClient expects a user avaiable socket by default.
    # This means that when executed by a non-root user, the podman socket should be started
    # as a user service. e.g. systemctl --user enable/start podman
    # Another socket option can be set via the base_url parameter.
    # https://podman-py.readthedocs.io/en/stable/podman.client.html
    with PodmanClient(**container_client_kwargs) as client:
        try:
            return client.images.push(image, destination=destination)
        except APIError as error:
            if verbose:
                print(f"Error publishing image: {error}")
            return False
    return False


def container_publish_to_archive(
    source, destination, container_client_kwargs=None, verbose=False
):
    if not container_client_kwargs:
        container_client_kwargs = {}

    image = get_image(source, container_client_kwargs=container_client_kwargs)
    if not image:
        return False

    try:
        # Returns a tarball of the image
        tarball = image.save()
        return i_write(destination, tarball, mode="wb")
    except APIError as error:
        if verbose:
            print(f"Error saving image: {error}")
        return False
    return False


def build_image(container_client_kwargs=None, **build_kwargs):
    # Options for the possible build_kwargs can be seen at
    # https://podman-py.readthedocs.io/en/stable/podman.domain.images_manager.html#podman.domain.images_manager.ImagesManager.build
    if not container_client_kwargs:
        container_client_kwargs = {}

    with PodmanClient(**container_client_kwargs) as client:
        try:
            image = client.images.build(**build_kwargs)
            return isinstance(image[0], Image)
        except (BuildError, APIError, TypeError) as error:
            print(f"Error building image: {error}")
            return False
    return False


def remove_image(name_or_id, container_client_kwargs=None, verbose=False):
    if not container_client_kwargs:
        container_client_kwargs = {}

    with PodmanClient(**container_client_kwargs) as client:
        try:
            results = client.images.remove(name_or_id)
            for result in results:
                if result.get("ExitCode") == 0:
                    return True
        except (APIError, ImageNotFound) as error:
            if verbose:
                print(f"Error removing image: {error}")
            return False
    return False


def exists_image(image_id, container_client_kwargs=None):
    with PodmanClient(**container_client_kwargs) as client:
        return client.images.exists(image_id)


def get_image(image_name_or_id, container_client_kwargs=None):
    if not container_client_kwargs:
        container_client_kwargs = {}

    with PodmanClient(**container_client_kwargs) as client:
        try:
            return client.images.get(image_name_or_id)
        except ImageNotFound:
            return None
    return None


# def podman_client(container_client_kwargs=None, verbose=False):
#     if "XDG_RUNTIME_DIR" not in os.environ:
#         if verbose:
#             print("XDG_RUNTIME_DIR is not set. Podman client may not work as expected. Suggesting that it be set to a user available runtime directory such as /run/user/<user_id>")
#     return PodmanClient(**container_client_kwargs)
