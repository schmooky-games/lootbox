use actix_web::{web, HttpResponse, Result, error};
use redis::AsyncCommands;
use bb8::Pool;
use bb8_redis::RedisConnectionManager;
use cuid2;

use crate::lootbox::models::{WeightedItem, WeightedLootbox, Meta, CreateWeightedLootboxRequest};
use crate::error::ErrorHTTPException;

use super::constants::{EMPTY_LOOTBOX, LOOTBOX_NOT_ACTIVE, LOOTBOX_NOT_FOUND};
use super::models::WeightedItemRequest;
use super::weighted_random::weighted_random;

pub async fn create_lootbox(
    data: web::Json<CreateWeightedLootboxRequest>,
    redis: web::Data<Pool<RedisConnectionManager>>,
) -> Result<HttpResponse> {
    let mut conn = redis.get().await.map_err(actix_web::error::ErrorInternalServerError)?;
    
    let lootbox_items: Vec<WeightedItem> = data.items.iter().map(|item: &WeightedItemRequest| {
        WeightedItem {
            id: cuid2::create_id(),
            data: item.data.clone(),
            meta: Meta {
                name: item.meta.name.clone(),
            },
            weight: item.weight.clone(),
        }
    }).collect();

    let lootbox_id = cuid2::create_id();
    let lootbox = WeightedLootbox {
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
    redis: web::Data<Pool<RedisConnectionManager>>,
) -> Result<HttpResponse> {
    let mut conn = redis.get().await.map_err(error::ErrorInternalServerError)?;

    let lootbox_data: Option<String> = conn.get(&*lootbox_id).await.map_err(error::ErrorInternalServerError)?;

    let mut lootbox: WeightedLootbox = match lootbox_data {
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

    let mut item: Option<WeightedItem> = None;

    if item.is_none() && !lootbox.items.is_empty() {
        let weights: Vec<i32> = lootbox.items.iter().map(|i| i.weight as i32).collect();
        item = weighted_random(&lootbox.items, &weights);
        
        if let Some(drawn_item) = &item {
            lootbox.items.retain(|i| i.id != drawn_item.id);
        }
    }

    if let Some(drawn_item) = item {
        let updated_lootbox_data = serde_json::to_string(&lootbox)?;
        conn.set(&*lootbox_id, updated_lootbox_data).await.map_err(error::ErrorInternalServerError)?;

        Ok(HttpResponse::Ok().json(drawn_item))
    } else {
        Ok(HttpResponse::BadRequest().json(ErrorHTTPException {
            status_code: 400,
            error_code: EMPTY_LOOTBOX,
            detail: "No items left in lootbox".to_string(),
        }))
    }
}