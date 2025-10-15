# Hello Country Service (FastAPI)

FastAPI port of the Hello Country service. The app reads phonetic "Hello World" greetings from `data/greetings.json`, chooses one using the `COUNTRY_CODE` environment variable, and exposes it at the root endpoint. Configuration is loaded from environment variables with optional support for a local `.env` file via `python-dotenv`.

## Local Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # optional
python -m app
```

By default the service listens on port `3000` and serves the configured greeting:

```bash
export COUNTRY_CODE=GA
python -m app
# or
uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
```

Query the service:

```bash
curl http://localhost:3000/
```

Example response:

```json
{"code": "GA", "message": "Dia Duit Domhan"}
```

Invalid country codes return a 404 with an error payload:

```json
{"error": "Unknown country code 'XX'"}
```

## Container Build

### Generic Registry
```bash
# Replace <registry>/<repo> with your container registry path
IMAGE=<REGISTRY>/<REPOSITORY>/hello-country-service:latest

podman build -t "$IMAGE" .
# or: docker build -t "$IMAGE" .

podman push "$IMAGE"
# or: docker push "$IMAGE"
```

### OpenShift Local Registry (external route)
```bash
oc project <NAMESPACE>
REGISTRY=$(oc registry info)
podman login -u "$(oc whoami)" -p "$(oc whoami -t)" "$REGISTRY"
IMAGE=${REGISTRY}/<NAMESPACE>/hello-country-service:latest
podman build -t "$IMAGE" .
podman push "$IMAGE"
```

### Build Inside OpenShift (BuildConfig)
```bash
# Point to the project that should own the image
oc project <NAMESPACE>

# Create a Docker strategy BuildConfig (run once)
oc new-build --strategy=docker --binary --name hello-country-service

# Start a build using the local working tree and stream logs
oc start-build hello-country-service --from-dir=. --follow

# Verify the resulting image stream tag
oc get is hello-country-service
```

The successful build publishes the image at:
```
image-registry.openshift-image-registry.svc:5000/<NAMESPACE>/hello-country-service:latest
```

## Deploy to Knative

Update `knative-service.yaml` with your image reference (for OpenShift local registry, set `your-namespace` accordingly), then apply it:

```bash
oc apply -f knative-service.yaml
```

Knative injects a `PORT` environment variable automatically; do not set one in the manifest. Override the greeting via `COUNTRY_CODE`.

Or, using the Knative CLI without modifying the YAML:

```bash
IMAGE=image-registry.openshift-image-registry.svc:5000/<NAMESPACE>/hello-country-service:latest

kn service apply hello-country-service \
  --image "$IMAGE" \
  --env COUNTRY_CODE=EN
```

Retrieve the URL:

```bash
kn service describe hello-country-service -o url
```

Test the service once it is ready:

```bash
curl "$(kn service describe hello-country-service -o url)"
```

To update the greeting later, patch the service:

```bash
kn service update hello-country-service --env COUNTRY_CODE=FR
```
