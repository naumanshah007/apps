Cloud-ready stubs (disabled by default)

- Azure Blob stub is initialized only when AZURE_BLOB_ENABLED=true
- AWS S3 stub is initialized only when AWS_S3_ENABLED=true

No credentials are required for local use.

Environment variables (documented, optional):
- AZURE_BLOB_ENABLED=true|false
- AWS_S3_ENABLED=true|false

Health
- The Streamlit Admin page acts as a simple health dashboard. You may also add a `/healthz` page section or query by loading the Admin page programmatically.