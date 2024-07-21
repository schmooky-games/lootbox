use actix_web::{web, App, HttpServer, HttpResponse, Result, error};
use serde::{Deserialize, Serialize};
use rand::seq::SliceRandom;
use redis::AsyncCommands;
use uuid::Uuid;
use dotenv::dotenv;

mod redis_connection;
use redis_connection::redis_connection::create_client as redis_client;

#[derive(Serialize)]
struct ErrorHTTPException {
    status_code: u16,
    error_code: u16,
    detail: String,
}

#[derive(Serialize, Deserialize, Clone)]
struct Meta {
    name: String,
}

#[derive(Serialize, Deserialize, Clone)]
struct Item {
    id: String,
    data: serde_json::Value,
    meta: Meta,
}

#[derive(Serialize, Deserialize)]
struct Lootbox {
    id: String,
    items: Vec<Item>,
    draws_count: Option<i32>,
    is_active: bool,
}

#[derive(Serialize, Deserialize, Clone)]
struct WeightedItem {
    id: String,
    data: serde_json::Value,
    meta: Meta,
    weight: u16,
}

#[derive(Serialize, Deserialize)]
struct WeightedLootbox {
    id: String,
    items: Vec<WeightedItem>,
    draws_count: Option<i32>,
    is_active: bool,
}

#[derive(Deserialize)]
struct CreateLootboxRequest {
    items: Vec<serde_json::Value>,
    draws_count: Option<i32>,
}

const WRONG_LOOTBOX_TYPE: u16 = 1005;

async fn create_lootbox(
    data: web::Json<CreateLootboxRequest>,
    redis: web::Data<redis::Client>,
) -> Result<HttpResponse> {
    let mut conn = redis.get_async_connection().await.map_err(error::ErrorInternalServerError)?;
    
    let lootbox_items: Vec<Item> = data.items.iter().map(|item| {
        Item {
            id: Uuid::new_v4().to_string(),
            data: item.get("data").cloned().unwrap_or_default(),
            meta: Meta {
                name: item.get("meta").and_then(|m| m.get("name")).and_then(|n| n.as_str()).unwrap_or("").to_string(),
            },
        }
    }).collect();

    let lootbox_id = Uuid::new_v4().to_string();
    let lootbox = Lootbox {
        id: lootbox_id.clone(),
        items: lootbox_items,
        draws_count: data.draws_count,
        is_active: true,
    };

    let lootbox_json = serde_json::to_string(&lootbox)?;
    conn.set(&lootbox_id, &lootbox_json).await.map_err(error::ErrorInternalServerError)?;

    Ok(HttpResponse::Ok().json(lootbox))
}

async fn get_loot(
    lootbox_id: web::Path<String>,
    redis: web::Data<redis::Client>,
) -> Result<HttpResponse> {
    let mut conn = redis.get_async_connection().await.map_err(error::ErrorInternalServerError)?;

    let lootbox_data: Option<String> = conn.get(&*lootbox_id).await.map_err(error::ErrorInternalServerError)?;

    let lootbox: Lootbox = match lootbox_data {
        Some(data) => serde_json::from_str(&data)?,
        None => return Ok(HttpResponse::BadRequest().json(ErrorHTTPException {
            status_code: 400,
            error_code: 1001,
            detail: "Lootbox not found".to_string(),
        })),
    };

    if !lootbox.is_active {
        return Ok(HttpResponse::BadRequest().json(ErrorHTTPException {
            status_code: 400,
            error_code: 1003,
            detail: "Lootbox is not active".to_string(),
        }));
    }

    if lootbox.items.is_empty() {
        return Ok(HttpResponse::BadRequest().json(ErrorHTTPException {
            status_code: 400,
            error_code: 1004,
            detail: "No items in lootbox".to_string(),
        }));
    }

    let drawed_item = lootbox.items.choose(&mut rand::thread_rng()).unwrap();

    Ok(HttpResponse::Ok().json(drawed_item))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenv().ok();
    let redis_client = redis_client().expect("Failed to create Redis client");

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(redis_client.clone()))
            .route("/create_lootbox", web::post().to(create_lootbox))
            .route("/get_loot/{lootbox_id}", web::get().to(get_loot))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}