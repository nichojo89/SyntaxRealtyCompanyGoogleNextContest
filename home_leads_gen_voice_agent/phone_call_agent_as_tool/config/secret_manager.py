import os


def get_secret(secret_id: str) -> str:
    env_value = os.getenv(secret_id)
    if env_value:
        return env_value

    try:
        from google.cloud import secretmanager
        from google.api_core import retry as retries
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or _get_project_id()
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(
            request={"name": name},
            retry=retries.Retry(deadline=10.0)
        )
        return response.payload.data.decode("utf-8")
    except Exception as e:
        raise RuntimeError(f"Failed to load secret '{secret_id}': {e}")


def _get_project_id() -> str:
    import urllib.request
    req = urllib.request.Request(
        "http://metadata.google.internal/computeMetadata/v1/project/project-id",
        headers={"Metadata-Flavor": "Google"}
    )
    with urllib.request.urlopen(req, timeout=2) as r:
        return r.read().decode()