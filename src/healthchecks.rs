use actix_web::{web, HttpResponse};
use bb8::Pool;
use bb8_redis::{
    bb8,
    redis::cmd,
    RedisConnectionManager
};
use serde_json::json;

#[actix_web::get("/health/redis")]
pub async fn redis_status(pool: web::Data<Pool<RedisConnectionManager>>) -> actix_web::HttpResponse {
    let mut conn = match pool.get().await {
        Ok(conn) => conn,
        Err(e) => {
            return HttpResponse::InternalServerError().json(json!({
                "status": "error",
                "message": format!("Failed to get Redis connection from pool: {}", e)
            }));
        }
    };

    let ping_result: String = cmd("PING").query_async(&mut *conn).await.unwrap();
    let info_result: String = cmd("INFO").query_async(&mut *conn).await.unwrap();

    let info_map: std::collections::HashMap<String, String> = info_result
        .lines()
        .filter(|line| line.contains(':'))
        .map(|line| {
            let mut parts = line.splitn(2, ':');
            (parts.next().unwrap_or_default().to_string(), parts.next().unwrap_or_default().to_string())
        })
        .collect();

    let response = json!({
        "status": "healthy",
        "ping": ping_result,
        "version": info_map.get("redis_version").cloned().unwrap_or_default(),
        "uptime_in_seconds": info_map.get("uptime_in_seconds").cloned().unwrap_or_default(),
        "connected_clients": info_map.get("connected_clients").cloned().unwrap_or_default(),
        "used_memory": info_map.get("used_memory_human").cloned().unwrap_or_default(),
    });

    HttpResponse::Ok().json(response)
}