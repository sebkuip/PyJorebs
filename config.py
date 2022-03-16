try:
    import secrets
except ImportError:
    print("Could not find secrets.py! Using example configuration")
    # TODO: this is probably bad, but it makes the IDE happy
    import secrets_example as secrets

from pathlib import Path

from mergedeep import Strategy, merge as do_merge


def merge(*args, **kwargs):
    return do_merge(*args, strategy=Strategy.ADDITIVE, **kwargs)


schemati_mount = ("/home/mcadmin/actual_schematics", "/schematics")
common_mounts = [
    ("/home/mcadmin/prod/{server}", "/data"),
    ("/home/mcadmin/prod/common", "/common"),
    schemati_mount,
]
dynmap_mount = ("/store/tiles/{server}", "/data/plugins/dynmap/web/tiles")

khttp_hack = "--add-opens java.base/java.net=ALL-UNNAMED --add-opens java.base/sun.net.www.protocol.https=ALL-UNNAMED"

memory_opts = "-Xms{memory} -Xmx{memory}"
paper_command = f"cd /data && exec java {memory_opts} -jar /common/paper-1.17.1-408.jar" + " {extra_args}"
waterfall_command = f"cd /data && exec java {khttp_hack} {memory_opts} -jar " + "/common/waterfall-{waterfall_version}.jar {extra_args}"
velocity_command = f"cd /data && exec java {memory_opts} -jar " + "/common/velocity-{velocity_version}.jar {extra_args}"
podman_jdk_image = "docker.io/library/openjdk:16.0.2-slim"


def paper_server(index, memory):
    return {
        "ports": {
            "game": 30000 + index,
            "rcon": 30100 + index,
        },
        "public": {},
        "extra": {
            "memory": memory,
        },
        "image": podman_jdk_image,
        "run_command": paper_command,
        "mounts": [*common_mounts],
    }


SERVERS = {
    "hub": paper_server(index=0, memory="2G"),
    "build": merge(
        paper_server(index=1, memory="8G"),
        {
            "ports": {
                "dynmap": 30201,
                "schemati": 8080,
            },
            "public": {"dynmap"},
            "mounts": [dynmap_mount],
        },
    ),
    "school": paper_server(index=2, memory="4G"),
    "survival": paper_server(index=3, memory="4G"),
    "play": paper_server(index=4, memory="4G"),
    "boat": paper_server(index=5, memory="4G"),
    "competition": paper_server(index=6, memory="4G"),
    "prodxy": {
        "ports": {
            "game": 25565,
        },
        "public": {"game"},
        "extra": {
            "memory": "1G",
            "waterfall_version": "1.18-466",
        },
        "image": podman_jdk_image,
        "run_command": waterfall_command,
        "mounts": [*common_mounts],
    }
}

SERVICES = {
    **SERVERS,
    "chad": {
        "ports": {},
        "public": {},
        "extra": {},
        "image": podman_jdk_image,
        "run_command": f"cd /data && exec java {khttp_hack} -jar Chad-1.0-all.jar config.yaml",
        "mounts": [("/home/mcadmin/private/chad", "/data")],
    },
    "enginexd": {
        "ports": {
            "http": (42080, 80),
            "https": (42043, 443),
        },
        "public": {"http", "https"},
        "extra": {},
        "image": "docker.io/library/nginx",
        "mounts": [
            ("/home/mcadmin/podshare/nginx", "/etc/nginx/conf.d"),
            ("/home/mcadmin/private/letsencrypt", "/etc/letsencrypt"),
            ("/home/mcadmin/private/wwwcertbot", "/var/www/certbot"),
        ],
    },
    "mchprs": {
        "ports": {
            "game": (42068, 25565),
        },
        "public": {},
        "extra": {},
        "image": "docker.io/stackdoubleflow/mchprs:plot-scale-5",
        "mounts": [
            ("/home/mcadmin/private/mchprs", "/data"),
            ("/home/mcadmin/actual_schematics", "/data/schems"),
        ],
    },
    "devxy": {
        "ports": {
            "game": (42069, 25577),
        },
        "public": "game",
        "extra": {
            "velocity_version": "3.1.1-102",
            "memory": "1G",
        },
        "image": podman_jdk_image,
        "run_command": velocity_command,
        "mounts": [
            ("/home/mcadmin/dev/{server}", "/data"),
            ("/home/mcadmin/dev/common", "/common"),
        ],
    },
}

SERVERS_LOCATION = Path("/home/mcadmin/prod")
DESTINATION = Path("/store/backups")
