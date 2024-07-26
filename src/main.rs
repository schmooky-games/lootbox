use actix_web::{web, App, HttpServer};
use actix_web_httpauth::middleware::HttpAuthentication;
use dotenv::dotenv;

mod redis_connection;
mod error;
mod healthchecks;
mod auth;
mod lootbox {
    pub mod models;
    pub mod equal_handlers;
    pub mod weighted_handlers;
    pub mod weighted_random;
    pub mod exclusive_handlers;
    pub mod constants;
}

use auth::{validate_token, create_token_cache};
use healthchecks::redis_status as redis_healthcheck;
use redis_connection::create_pool as redis_pool;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenv().ok();
    let pool = redis_pool().await.expect("Failed to create Redis pool");
    let pool_data = web::Data::new(pool.clone()); 
    let token_cache = web::Data::new(create_token_cache());

    HttpServer::new(move || {
        let auth = HttpAuthentication::bearer({
            let pool_data = pool_data.clone();
            let token_cache = token_cache.clone();
            move |req, credentials| {
                validate_token(req, credentials, pool_data.clone(), token_cache.clone())
            }
        });

        App::new()
            .app_data(web::Data::new(pool.clone()))
            .service(redis_healthcheck)
            .service(
                web::scope("equal")
                    .wrap(auth.clone())
                    .route("/create_lootbox", web::post().to(lootbox::equal_handlers::create_lootbox))
                    .route("/get_loot/{lootbox_id}", web::get().to(lootbox::equal_handlers::get_loot))
            )
            .service(
                web::scope("weighted")
                    .wrap(auth.clone())
                    .route("/create_lootbox", web::post().to(lootbox::weighted_handlers::create_lootbox))
                    .route("/get_loot/{lootbox_id}", web::get().to(lootbox::weighted_handlers::get_loot))
            )
            .service(
                web::scope("exclusive")
                    .wrap(auth.clone())
                    .route("/create_lootbox", web::post().to(lootbox::exclusive_handlers::create_lootbox))
                    .route("/get_loot/{lootbox_id}", web::get().to(lootbox::exclusive_handlers::get_loot))
            )
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}