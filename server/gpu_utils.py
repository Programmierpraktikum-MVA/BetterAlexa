import logging
import torch

# Hard‑coded footprint estimates (adjust if you change quantisation)
WHISPER_MEDIUM_FP16_GB   = 1.8
LLAMA3_8B_4BIT_GB        = 4.5   # fp16 ≈14 GB, bf16 ≈ 12 GB
SAFETY_MARGIN_GB         = 0.5   # keep a buffer for activations etc.

def gpu_free_gb(device_index: int = 0) -> float:
    """
    Return *current* free VRAM on the given CUDA device in GiB.
    Falls back to torch.cuda.mem_get_info if pynvml is unavailable.
    """
    if not torch.cuda.is_available():
        return 0.0
    torch.cuda.empty_cache()                      # clear unused blocks first
    free_bytes, _ = torch.cuda.mem_get_info(device_index)
    return free_bytes / 1024**3