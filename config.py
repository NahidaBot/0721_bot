from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool

    bot_token: str

    txt_help: str = "(在频道评论区发送) /get_origin 获取原图"

    class Config:
        env_file = ".env"
        case_sensitive = False


config = Settings()

if __name__ == "__main__":
    print(config.dict())
