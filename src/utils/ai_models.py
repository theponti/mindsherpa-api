llama3_70b_8192 = "llama3-70b-8192"
llama3_8b_8192 = "llama3-8b-8192"
mixtral_8x7b_32768 = "mixtral-8x7b-32768"
gemma_7b_it = "gemma-7b-it"
gemma2_9b_it = "gemma2-9b-it"
groq_whisper_large_v3 = "groq-whisper-large-v3"

open_source_models = [
    llama3_70b_8192,
    llama3_8b_8192,
    mixtral_8x7b_32768,
    gemma_7b_it,
]

audio_models = {
    "groq": "whisper-large-v3",
    "openai": "whisper-1",
}

content_model_options = [model for model in open_source_models]
content_model_options.append(gemma2_9b_it)
