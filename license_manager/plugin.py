from glob import glob
import os
import pkg_resources

from tutor import hooks

from .__about__ import __version__


########################################
# CONFIGURATION
########################################

hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        # Where to clone license-manager from when we build it ourselves
        ("LICENSE_MANAGER_REPOSITORY", "https://github.com/openedx/license-manager.git"),
        # Tag we use when the plugin builds the image
        ("LICENSE_MANAGER_BUILT_IMAGE", "{{ DOCKER_REGISTRY }}{{ DOCKER_IMAGE_PREFIX }}license-manager:{{ OPENEDX_COMMON_VERSION }}"),

        # Optional external image. If empty => we build LICENSE_MANAGER_BUILT_IMAGE.
        ("LICENSE_MANAGER_DOCKER_IMAGE", ""),

        ("LICENSE_MANAGER_VERSION", __version__),
        ("LICENSE_MANAGER_HOST", "subscriptions.{{ LMS_HOST }}"),
        ("LICENSE_MANAGER_MYSQL_DATABASE", "license_manager"),
        ("LICENSE_MANAGER_MYSQL_USERNAME", "license_manager"),
        ("LICENSE_MANAGER_OAUTH2_KEY", "license-manager-key"),
        ("LICENSE_MANAGER_OAUTH2_KEY_DEV", "license-manager-key-dev"),
        ("LICENSE_MANAGER_OAUTH2_KEY_SSO", "license-manager-key-sso"),
        ("LICENSE_MANAGER_OAUTH2_KEY_SSO_DEV", "license-manager-key-sso-dev"),
    ]
)

hooks.Filters.CONFIG_UNIQUE.add_items(
    [
        # Add settings that don't have a reasonable default for all users here.
        # For instance: passwords, secret keys, etc.
        # Each new setting is a pair: (setting_name, unique_generated_value).
        # Prefix your setting names with 'LICENSE_MANAGER_'.
        # For example:
        # ("LICENSE_MANAGER_SECRET_KEY", "{{ 24|random_string }}"),
        ("LICENSE_MANAGER_MYSQL_PASSWORD", "{{ 8|random_string }}"),
        ("LICENSE_MANAGER_SECRET_KEY", "{{ 24|random_string }}"),
        ("LICENSE_MANAGER_SOCIAL_AUTH_EDX_OAUTH2_SECRET", "{{ 16|random_string }}"),
        ("LICENSE_MANAGER_BACKEND_SERVICE_EDX_OAUTH2_SECRET", "{{ 16|random_string }}"),
        ("LICENSE_MANAGER_OAUTH2_SECRET", "{{ 16|random_string }}"),
        ("LICENSE_MANAGER_OAUTH2_SECRET_DEV", "{{ 16|random_string }}"),
        ("LICENSE_MANAGER_OAUTH2_SECRET_SSO", "{{ 16|random_string }}"),
        ("LICENSE_MANAGER_OAUTH2_SECRET_SSO_DEV", "{{ 16|random_string }}"),
    ]
)

hooks.Filters.CONFIG_OVERRIDES.add_items(
    [
        # Danger zone!
        # Add values to override settings from Tutor core or other plugins here.
        # Each override is a pair: (setting_name, new_value). For example:
        # ("PLATFORM_NAME", "My platform"),
    ]
)


########################################
# INITIALIZATION TASKS
########################################

# To run the script from templates/license_manager/tasks/myservice/init, add:
hooks.Filters.COMMANDS_INIT.add_item((
        "mysql",
        ("license_manager", "tasks", "mysql", "init"),
 ))

hooks.Filters.COMMANDS_INIT.add_item(
    (
        "lms",
        ("license_manager", "tasks", "lms", "init"),
    )
)
hooks.Filters.COMMANDS_INIT.add_item(
    (
        "license-manager",
        ("license_manager", "tasks", "license_manager", "init"),
    )
)

########################################
# DOCKER IMAGE MANAGEMENT
########################################

# To build an image with `tutor images build license_manager`, add a Dockerfile to templates/license_manager/build/license_manager and write:
@hooks.Filters.IMAGES_BUILD.add()
def add_license_manager_build(images, settings):
    """
    Only build the license_manager image when no external image is configured.

    - If LICENSE_MANAGER_DOCKER_IMAGE is empty: build LICENSE_MANAGER_BUILT_IMAGE.
    - If LICENSE_MANAGER_DOCKER_IMAGE is set: assume the operator owns that image;
      we do NOT build anything for this service.
    """
    external_image = settings.get("LICENSE_MANAGER_DOCKER_IMAGE")
    if external_image:
        # Admin is bringing their own image; don't override it.
        return images

    images.append(
        (
            "license_manager",  # service name, same as before
            ("plugins", "license_manager", "build", "license_manager"),  # Dockerfile context
            settings["LICENSE_MANAGER_BUILT_IMAGE"],  # tag we build
            (),
        )
    )
    return images


# To pull/push an image with `tutor images pull license_manager` and `tutor images push license_manager`, write:
@hooks.Filters.IMAGES_PULL.add()
def add_license_manager_pull(images, settings):
    """
    When an external license manager image is configured, allow
    `tutor images pull license_manager` to pull it.
    """
    external_image = settings.get("LICENSE_MANAGER_DOCKER_IMAGE")
    if external_image:
        images.append(
            (
                "license_manager",
                external_image,
            )
        )
    return images

# hooks.Filters.IMAGES_PUSH.add_item((
#     "license_manager",
#     "docker.io/license_manager:{{ LICENSE_MANAGER_VERSION }}",
# )


########################################
# TEMPLATE RENDERING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

hooks.Filters.ENV_TEMPLATE_ROOTS.add_items(
    # Root paths for template files, relative to the project root.
    [
        pkg_resources.resource_filename("license_manager", "templates"),
    ]
)

hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    # For each pair (source_path, destination_path):
    # templates at ``source_path`` (relative to your ENV_TEMPLATE_ROOTS) will be
    # rendered to ``destination_path`` (relative to your Tutor environment).
    [
        ("license_manager/build", "plugins"),
        ("license_manager/apps", "plugins"),
    ],
)


########################################
# PATCH LOADING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

# For each file in license_manager/patches,
# apply a patch based on the file's name and contents.
for path in glob(
    os.path.join(
        pkg_resources.resource_filename("license_manager", "patches"),
        "*",
    )
):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))
