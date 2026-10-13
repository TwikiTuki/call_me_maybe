
# TODO

## Local model files

Hugging Face caches downloaded model and tokenizer files automatically. To choose the cache
location and prevent any network access after the first download:

```python
from llm_sdk import Small_LLM_Model

model = Small_LLM_Model(
	cache_dir="./models",
	local_files_only=True,
)
```

The first run can use the same `cache_dir` with `local_files_only=False` (the default) to download
the files. Alternatively, pass a local model directory as `model_name`:

```python
model = Small_LLM_Model("./models/Qwen3-0.6B", local_files_only=True)
```

### Technologies
- pydantic
- DONE Qwen
- Makefile
### Optional
- numpy json
