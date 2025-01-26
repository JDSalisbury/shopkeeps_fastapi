import subprocess
from typing import Union, Annotated

from fastapi import FastAPI, HTTPException, Depends
from openai import AsyncOpenAI
from sqlmodel import Session
from models.db_setup import get_session, create_db_and_tables
from models.shop_keep import ShopKeep, Item
from contextlib import asynccontextmanager
import logging
from colorama import Fore, Style, Back
import json
from sqlmodel import select
from prompts.sk_prompts import GENERATE_SHOPKEEP, GENERATE_INVENTORY_FOR_SHOPKEEP
from fastapi.middleware.cors import CORSMiddleware
from funcs import file_workrflows
from dotenv import load_dotenv
import os
SessionDep = Annotated[Session, Depends(get_session)]

if os.getenv("LOCAL_DEV"):
    logging.basicConfig(
        level=logging.INFO,
        format=f"     {Back.GREEN}{Fore.WHITE} %(levelname)s {
            Style.RESET_ALL}  %(message)s",
    )

logger = logging.getLogger("app")

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        logger.info("Database migrations applied successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to apply migrations: {e}")
        raise RuntimeError("Database migration failed.") from e

    logger.info("Startup DB task completed.")

    yield
    logger.info("App shutdown tasks completed.")

app = FastAPI(lifespan=lifespan)

# get api key from .env file

oapi_key = os.getenv("OPENAI_API_KEY")


client = AsyncOpenAI(
    api_key=oapi_key,
)


app.add_middleware(
    CORSMiddleware,
    # Update with your React app's URL
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@app.get("/")
def heartbeat():
    return {"status": "ok"}


@app.get("/shopkeeps_full")
def get_shopkeeps(session: SessionDep):
    # Use a select() statement to fetch all ShopKeep records
    statement = select(ShopKeep)
    shopkeeps = session.exec(statement).all()
    return {"shopkeeps": [shopkeep.model_dump() for shopkeep in shopkeeps]}


@app.get("/shopkeeps")
def list_shopkeeps(session: SessionDep):
    shopkeeps = session.exec(select(ShopKeep)).all()
    return [{"id": shopkeep.id, "name": shopkeep.name, "image_url": shopkeep.image_url, "shop_type": shopkeep.shop_type, "location": shopkeep.location} for shopkeep in shopkeeps]


@app.get("/shopkeep/{shopkeep_id}")
async def get_shopkeep_and_inventory(shopkeep_id: int, session: SessionDep):
    # Fetch the shopkeeper from the database
    shopkeep = session.get(ShopKeep, shopkeep_id)
    if not shopkeep:
        raise HTTPException(status_code=404, detail="Shopkeep not found.")

    # Fetch the shopkeeper's inventory
    statement = select(Item).where(Item.shopkeep_id == shopkeep_id)
    items = session.exec(statement).all()

    return {
        "shopkeep": shopkeep.model_dump(),
        "inventory": [item.model_dump() for item in items],
    }


@app.patch("/shopkeep/image/{shopkeep_id}")
async def add_shopkeep_image_url(shopkeep_id: int, session: SessionDep, image_url: str = None):
    # Fetch the shopkeeper from the database
    shopkeep = session.get(ShopKeep, shopkeep_id)
    if not shopkeep:
        raise HTTPException(status_code=404, detail="Shopkeep not found.")

    # Update the shopkeeper's image URL
    # shopkeep.image_url = image_url
    if image_url:
        shopkeep.image_url = image_url
    else:
        shopkeep.image_url = file_workrflows.get_random_image(
            shopkeep.sex, shopkeep.character_class)
    session.add(shopkeep)
    session.commit()
    session.refresh(shopkeep)

    return {"shopkeep": shopkeep.model_dump()}


@app.post("/generate_shopkeep")
async def generate_shopkeep(location: str, session: SessionDep):

    statement = select(ShopKeep)
    shopkeep_models = session.exec(statement).all()
    shopkeeps = {"shopkeeps": [shopkeep.model_dump()
                               for shopkeep in shopkeep_models]}
    try:
        # Query ChatGPT for a random shopkeeper
        response = await client.chat.completions.create(**GENERATE_SHOPKEEP(location, shopkeeps))

        # Parse the JSON response
        message_content = response.choices[0].message.content
        print("message_content", message_content)
        try:
            shopkeep_data = json.loads(message_content)  # Safer than eval
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500, detail="Failed to parse GPT response as JSON.")

        # Create a ShopKeep instance
        shopkeep_data['image_url'] = file_workrflows.get_random_image(
            shopkeep_data['sex'], shopkeep_data['character_class'])
        shopkeep = ShopKeep(**shopkeep_data)

        # Save to the database
        session.add(shopkeep)
        session.commit()
        session.refresh(shopkeep)  # Refresh to get the generated ID

        return {"shopkeep": shopkeep.model_dump()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_inventory/{shopkeep_id}")
async def generate_shopkeep_inventory(shopkeep_id: int, session: SessionDep):
    try:
        # Fetch the shopkeeper from the database
        shopkeep = session.get(ShopKeep, shopkeep_id)
        if not shopkeep:
            raise HTTPException(status_code=404, detail="Shopkeep not found.")

        # Query ChatGPT for inventory
        response = await client.chat.completions.create(
            **GENERATE_INVENTORY_FOR_SHOPKEEP(shopkeep)
        )

        # Parse the response
        message_content = response.choices[0].message.content
        logger.info(f"ChatGPT Response: {message_content}")

        try:
            items_data = json.loads(message_content)  # Parse as JSON
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GPT response as JSON: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to parse GPT response as JSON."
            )

        # Ensure inventory is a list
        if not isinstance(items_data.get("inventory"), list):
            raise HTTPException(
                status_code=500, detail="Invalid format: 'inventory' key missing or not a list."
            )

        # Save items to the database
        created_items = []
        for item_data in items_data["inventory"]:
            try:
                item = Item(**item_data, shopkeep_id=shopkeep_id)
                session.add(item)
                created_items.append(item.model_dump())
            except Exception as e:
                logger.error(f"Failed to add item to database: {e}")
                raise HTTPException(
                    status_code=500, detail="Error saving item to database."
                )

        session.commit()
        return {"inventory": [item for item in created_items]}

    except Exception as e:
        logger.error(f"Error in generate_inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))
