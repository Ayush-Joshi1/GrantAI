# API Notes

## Available endpoints

The API exposes the following Sprint 2 agent endpoints:

- POST /api/v1/recommend
- POST /api/v1/eligibility/check
- POST /api/v1/proposal/generate
- POST /api/v1/deadline
- POST /api/v1/notifications

## Notes

- Each endpoint is a thin FastAPI adapter over an application service.
- Request and response schemas live under apps/api/src/api/v1/schemas.
- Errors are mapped consistently to validation and upstream error responses.
- OpenAPI is exposed at /api/v1/openapi.json.
