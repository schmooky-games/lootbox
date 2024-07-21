use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone)]
pub struct Meta {
    pub name: String,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct Item {
    pub id: String,
    pub data: serde_json::Value,
    pub meta: Meta,
}

#[derive(Serialize, Deserialize)]
pub struct Lootbox {
    pub id: String,
    pub items: Vec<Item>,
    pub draws_count: Option<i32>,
    pub is_active: bool,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct WeightedItem {
    pub id: String,
    pub data: serde_json::Value,
    pub meta: Meta,
    pub weight: u16,
}

#[derive(Serialize, Deserialize)]
pub struct WeightedLootbox {
    pub id: String,
    pub items: Vec<WeightedItem>,
    pub draws_count: Option<i32>,
    pub is_active: bool,
}

#[derive(Deserialize)]
pub struct MetaRequest {
   pub name: String,
}

#[derive(Deserialize)]
pub struct ItemRequest {
    pub data: serde_json::Value,
    pub meta: MetaRequest,
}

#[derive(Deserialize)]
pub struct WeightedItemRequest {
    pub data: serde_json::Value,
    pub meta: MetaRequest,
    pub weight: u16,
}

#[derive(Deserialize)]
pub struct CreateLootboxRequest {
    pub items: Vec<ItemRequest>,
    pub draws_count: Option<i32>,
}

#[derive(Deserialize)]
pub struct CreateWeightedLootboxRequest {
    pub items: Vec<WeightedItemRequest>,
    pub draws_count: Option<i32>,
}
