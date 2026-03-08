import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile
from starlette.responses import FileResponse

from models import ProductPost, ProductUpdate, Product

app = FastAPI()
products = {}
content_types = {}
next_id = 1

@app.post("/product")
async def add_product(product: ProductPost) -> Product:
    global next_id
    product = Product(
        id = len(products) + 1,
        name = product.name,
        description = product.description,
    )
    products[next_id] = product
    next_id += 1
    return product

@app.get("/product/{id}")
async def get_product(id: int) -> Product:
    if id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    return products[id]

@app.put("/product/{id}")
async def update_product(id: int, product: ProductUpdate) -> Product:
    if id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.name is not None:
        products[id].name = product.name
    if product.description is not None:
        products[id].description = product.description
    return products[id]

@app.delete("/product/{id}")
async def delete_product(id: int) -> Product:
    if id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    product = products[id]
    del products[id]
    return product

@app.get("/products")
async def get_products() -> list[Product]:
    return [await get_product(id) for id in products]

@app.post("/product/{id}/image")
async def upload_image(id: int, icon: UploadFile) -> Product:
    with open(f"images/{id}", "wb") as file:
        file.write(await icon.read())
    content_types[id] = icon.content_type
    products[id].image = icon.filename
    return products[id]

@app.get("/product/{id}/image")
async def get_product_image(id: int) -> FileResponse:
    if id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    if products[id].image is None:
        raise HTTPException(status_code=404, detail="Product image not found")
    return FileResponse(f"images/{id}", media_type=content_types[id])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)