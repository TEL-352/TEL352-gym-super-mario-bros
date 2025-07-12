def conversion_pixel_baldoza(n_pixel: int, mario_status: str) -> int:
    baldoza_size = 16
    return int(n_pixel // baldoza_size)
