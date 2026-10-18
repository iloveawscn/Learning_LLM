import modal
from modal import Image

# 设置

app = modal.App("hello")
image = Image.debian_slim().pip_install("requests")

# Hello 函数！


@app.function(image=image)
def hello() -> str:
    import requests

    response = requests.get("https://ipinfo.io/json")
    data = response.json()
    city, region, country = data["city"], data["region"], data["country"]
    return f"Hello from {city}, {region}, {country}!!"


# 新增 - 感谢学生的贡献！


@app.function(image=image, region="eu")
def hello_europe() -> str:
    import requests

    response = requests.get("https://ipinfo.io/json")
    data = response.json()
    city, region, country = data["city"], data["region"], data["country"]
    return f"Hello from {city}, {region}, {country}!!"
