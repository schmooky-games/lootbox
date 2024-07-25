use bb8::Pool;
use bb8_redis::RedisConnectionManager;
use std::error::Error;

pub async fn create_pool() -> Result<Pool<RedisConnectionManager>, Box<dyn Error>> {
    let redis_uri = std::env::var("REDIS_URI")?;
    let manager = RedisConnectionManager::new(redis_uri).unwrap();
    let pool = bb8::Pool::builder().build(manager).await.unwrap();
    
    Ok(pool)
}
