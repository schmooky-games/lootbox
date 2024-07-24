use actix_web::{web, App, HttpServer};
use dotenv::dotenv;

mod redis_connection;
mod error;
mod healthchecks;
mod lootbox {
    pub mod models;
    pub mod equal_handlers;
    pub mod weighted_handlers;
    pub mod weighted_random;
    pub mod exclusive_handlers;
    pub mod constants;
}

use redis_connection::redis_connection::create_client as redis_client;
use healthchecks::ping_redis as redis_healthcheck;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenv().ok();
    let redis_client = redis_client().await.expect("Failed to create Redis client");
    let redis_data = web::Data::new(redis_client);

    HttpServer::new(move || {
        App::new()
            .app_data(redis_data.clone())
            .service(redis_healthcheck)
            .service(
                web::scope("equal")
                .route("/create_lootbox", web::post().to(lootbox::equal_handlers::create_lootbox))
                .route("/get_loot/{lootbox_id}", web::get().to(lootbox::equal_handlers::get_loot))
            )
            .service(
                web::scope("weighted")
                .route("/create_lootbox", web::post().to(lootbox::weighted_handlers::create_lootbox))
                .route("/get_loot/{lootbox_id}", web::get().to(lootbox::weighted_handlers::get_loot))
            )
            .service(
                web::scope("exclusive")
                .route("/create_lootbox", web::post().to(lootbox::exclusive_handlers::create_lootbox))
                .route("/get_loot/{lootbox_id}", web::get().to(lootbox::exclusive_handlers::get_loot))
            )
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}