use bb8::Pool;
use bb8_redis::RedisConnectionManager;
use std::error::Error;

pub async fn create_pool() -> Result<Pool<RedisConnectionManager>, Box<dyn Error>> {
    let redis_uri = std::env::var("REDIS_URI")?;
    // let redis_uri = "redis://localhost:6379";
    let manager: RedisConnectionManager = RedisConnectionManager::new(redis_uri).unwrap();
    let pool = bb8::Pool::builder()
    .max_size(500)
    .connection_timeout(std::time::Duration::from_secs(5))
    .build(manager)
    .await
    .unwrap();
    
    Ok(pool)
}
