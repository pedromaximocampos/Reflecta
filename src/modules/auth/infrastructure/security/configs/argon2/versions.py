from .config import Argon2Config

def get_argon2_v1_config() -> Argon2Config:
    return Argon2Config(
        time_cost=2,
        memory_cost=102400, #100 MB
        parallelism=4,
        version=1,
    )