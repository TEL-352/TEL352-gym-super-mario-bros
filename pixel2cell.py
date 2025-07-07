def conversion_pixel_baldoza(n_pixel: int, mario_status: str) -> int:
    baldoza_size = 16  
    mario_size = 16 if mario_status == "big" else 12
    
    mario_center = n_pixel + (mario_size // 2)
    
    baldoza = mario_center // baldoza_size
    
    return baldoza