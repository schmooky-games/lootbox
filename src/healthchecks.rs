use actix_web::{web, HttpResponse};
use redis::Client;
use serde_json::json;

#[actix_web::get("/health/redis")]
async fn ping_redis(client: web::Data<Client>) -> HttpResponse {
    match client.get_async_connection().await {
        Ok(mut con) => {
            let ping_result = redis::cmd("PING").query_async::<_, String>(&mut con).await;
            let info_result: redis::RedisResult<String> = redis::cmd("INFO").query_async(&mut con).await;

            match (ping_result, info_result) {
                (Ok(pong), Ok(info)) => {
                    let info_map: std::collections::HashMap<String, String> = info
                        .lines()
                        .filter(|line| line.contains(':'))
                        .map(|line| {
                            let mut parts = line.splitn(2, ':');
                            (parts.next().unwrap().to_string(), parts.next().unwrap().to_string())
                        })
                        .collect();

                    let response = json!({
                        "status": "healthy",
                        "ping": pong,
                        "version": info_map.get("redis_version").cloned().unwrap_or_default(),
                        "uptime_in_seconds": info_map.get("uptime_in_seconds").cloned().unwrap_or_default(),
                        "connected_clients": info_map.get("connected_clients").cloned().unwrap_or_default(),
                        "used_memory": info_map.get("used_memory_human").cloned().unwrap_or_default(),
                    });

                    HttpResponse::Ok().json(response)
                },
                (Err(e), _) => HttpResponse::InternalServerError().json(json!({
                    "status": "error",
                    "message": format!("Redis ping error: {}", e)
                })),
                (_, Err(e)) => HttpResponse::InternalServerError().json(json!({
                    "status": "error",
                    "message": format!("Redis info error: {}", e)
                })),
            }
        },
        Err(e) => HttpResponse::InternalServerError().json(json!({
            "status": "error",
            "message": format!("Redis connection error: {}", e)
        })),
    }
}