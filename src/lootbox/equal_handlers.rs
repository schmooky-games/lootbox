use actix_web::{web, HttpResponse, Result};
use rand::seq::SliceRandom;
use rand::rngs::OsRng;
use bb8::Pool;
use bb8_redis::RedisConnectionManager;
use redis::AsyncCommands; 

use crate::lootbox::models::{Lootbox, Item, Meta, CreateLootboxRequest};
use crate::error::ErrorHTTPException;

use super::constants::{LOOTBOX_NOT_ACTIVE, LOOTBOX_NOT_FOUND, EMPTY_LOOTBOX};

pub async fn create_lootbox(
    data: web::Json<CreateLootboxRequest>,
    pool: web::Data<Pool<RedisConnectionManager>>,
) -> Result<HttpResponse> {
    let mut conn = pool.get().await.map_err(actix_web::error::ErrorInternalServerError)?;

    let lootbox_items: Vec<Item> = data.items.iter().map(|item| {
        Item {
            id: cuid2::create_id(),
            data: item.data.clone(),
            meta: Meta {
                name: item.meta.name.clone(),
            },
        }
    }).collect();

    let lootbox_id = cuid2::create_id();
    let lootbox = Lootbox {
        id: lootbox_id.clone(),
        items: lootbox_items,
        draws_count: data.draws_count,
        is_active: true,
    };

    let lootbox_json = serde_json::to_string(&lootbox)?;
    conn.set(&lootbox_id, &lootbox_json).await.map_err(actix_web::error::ErrorInternalServerError)?;

    Ok(HttpResponse::Ok().json(lootbox))
}

pub async fn get_loot(
    lootbox_id: web::Path<String>,
    pool: web::Data<Pool<RedisConnectionManager>>,
) -> Result<HttpResponse> {
    // Получение подключения из пула
    let mut conn = pool.get().await.map_err(actix_web::error::ErrorInternalServerError)?;

    let lootbox_data: Option<String> = conn.get(&*lootbox_id).await.map_err(actix_web::error::ErrorInternalServerError)?;

    let lootbox: Lootbox = match lootbox_data {
        Some(data) => serde_json::from_str(&data)?,
        None => return Ok(HttpResponse::BadRequest().json(ErrorHTTPException {
            status_code: 400,
            error_code: LOOTBOX_NOT_FOUND,
            detail: "Lootbox not found".to_string(),
        })),
    };

    if !lootbox.is_active {
        return Ok(HttpResponse::BadRequest().json(ErrorHTTPException {
            status_code: 400,
            error_code: LOOTBOX_NOT_ACTIVE,
            detail: "Lootbox is not active".to_string(),
        }));
    }

    if lootbox.items.is_empty() {
        return Ok(HttpResponse::BadRequest().json(ErrorHTTPException {
            status_code: 400,
            error_code: EMPTY_LOOTBOX,
            detail: "No items in lootbox".to_string(),
        }));
    }

    let drawn_item = lootbox.items.choose(&mut OsRng).unwrap();

    Ok(HttpResponse::Ok().json(drawn_item))
}
