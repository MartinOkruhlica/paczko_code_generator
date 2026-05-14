Generates a return shipment code by automating a web form using Playwright.

It exposes a FastAPI endpoint and runs inside a Docker container.

### Build image
`docker build -t return-code-service .`

### Run container
`docker run -p 8000:8000 return-code-service`

### Open API docs
`http://localhost:8000/docs`

### Endpoint:
`POST /pl-return-shipment-code`


### Request body:
```json
{
  "order_number": "V-12345678",
  "size": "s",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "777123456",
  "email": "john.doe@email.com"
}
```

### Field descriptions:
| Field        | Type   | Required | Notes                        |
| ------------ | ------ | -------- | ---------------------------- |
| order_number | string | yes      | Order reference used in form |
| size         | string | yes      | "s", "m", or "l"             |
| first_name   | string | yes      | Customer first name          |
| last_name    | string | yes      | Customer last name           |
| phone_number | string | yes      | Phone number without +48     |
| email        | string | yes      | Valid email address          |

## Response 
### Success (200 OK)
```json
{
  "code": "ABC123XYZ"
}
```

### Error response (500)
```json
{
  "detail": "Failed to generate return code: Timeout error..."
}
```

### Notes

- Each request launches a new Playwright browser instance
- Requests are synchronous
- The service depends on the website:
  https://szybkiezwroty.pl/en/PacketaGroup
