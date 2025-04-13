from fastapi_main import app

@app.get("/plato-dev-bot", tags=["telegram-bot"])
def telegram_plato_dev_bot():
    # print('a', a)
    # print('b', b)
    # print('c', c)
    return {"PLACEHOLDER": "plato-dev-bot"}
