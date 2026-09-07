from pydantic import BaseModel, ConfigDict, EmailStr, Field, StrictBool


class TaskCreate(BaseModel):
	title: str
	description: str | None = None
	completed: StrictBool = False


class TaskUpdate(BaseModel):
	title: str | None = None
	description: str | None = None
	completed: StrictBool | None = None


class TaskResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	task_id: int
	title: str
	description: str | None = None
	completed: bool


class UserCreate(BaseModel):
	username: str
	email: EmailStr
	password: str = Field(min_length=8, max_length=72)


class LoginRequest(BaseModel):
	username: str
	password: str


class TokenResponse(BaseModel):
	access_token: str
	token_type: str


class UserResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	username: str
	email: EmailStr
