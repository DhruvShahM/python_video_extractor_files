from gpt4all import GPT4All

# Correct model path
model_path = r"C:\models\demo.gguf"

# Load the model correctly
model = GPT4All(model_path, allow_download=False, device="cpu")

# Test a prompt
response = model.generate("Python में variables क्या होते हैं?")
print(response)
