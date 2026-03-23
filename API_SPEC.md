# API ??

## ??????

```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

## ????

- ???POST
- ???/api/v1/auth/login
- ?????JSON??

```json
{
  "account": "user@example.com",
  "password": "PlainPassword123"
}
```

- ???200??

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "access_token": "jwt_token",
    "refresh_token": "refresh_token",
    "token_type": "bearer"
  }
}
```

## ????

- ???POST
- ???/api/v1/posts
- Header?Authorization: Bearer <token>
- ?????JSON??

```json
{
  "title": "My First Post",
  "content": "# Hello\nThis is a markdown post",
  "category_id": 1
}
```

- ???200??

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 1,
    "title": "My First Post",
    "category_id": 1
  }
}
```

## ????

- ???GET
- ???/api/v1/comments
- Query?post_id=1
- ???200??

```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "id": 1,
      "post_id": 1,
      "content": "Nice post",
      "parent_id": null,
      "level": 1
    }
  ]
}
```
