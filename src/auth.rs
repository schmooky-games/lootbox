use actix_web::{dev::ServiceRequest, Error, web};
use actix_web_httpauth::extractors::bearer::BearerAuth;
use bb8::Pool;
use bb8_redis::RedisConnectionManager;
use redis::AsyncCommands;
use std::time::{Duration, Instant};
use std::sync::Arc;
use tokio::sync::Mutex;
use lru::LruCache;

const TOKEN_EXPIRATION: Duration = Duration::from_secs(3600);
const CACHE_CAPACITY: usize = 10000;

pub struct TokenCache {
    cache: LruCache<String, Instant>,
}

impl TokenCache {
    pub fn new(capacity: usize) -> Self {
        let non_zero_capacity = std::num::NonZeroUsize::new(capacity).expect("Capacity must be non-zero");

        Self {
            cache: LruCache::new(non_zero_capacity),
        }
    }

    pub fn insert(&mut self, token: String) {
        self.cache.put(token, Instant::now());
    }

    pub fn contains(&mut self, token: &str) -> bool {
        if let Some(time) = self.cache.get(token) {
            if time.elapsed() < TOKEN_EXPIRATION {
                return true;
            }
            self.cache.pop(token);
        }
        false
    }
}

pub type SharedTokenCache = Arc<Mutex<TokenCache>>;

pub fn create_token_cache() -> SharedTokenCache {
    Arc::new(Mutex::new(TokenCache::new(CACHE_CAPACITY)))
}

pub async fn validate_token(
    req: ServiceRequest,
    credentials: BearerAuth,
    redis: web::Data<Pool<RedisConnectionManager>>,
    token_cache: web::Data<SharedTokenCache>,
) -> Result<ServiceRequest, (Error, ServiceRequest)> {
    let token = credentials.token();
    
    if token_cache.lock().await.contains(token) {
        return Ok(req);
    }

    let key = format!("token:{}", token);

    let mut conn = match redis.get().await {
        Ok(conn) => conn,
        Err(e) => {
            let error = actix_web::error::ErrorInternalServerError(format!("Redis error: {}", e));
            return Err((error, req));
        }
    };

    let exists: bool = match conn.exists::<&str, bool>(&key).await {
        Ok(exists) => exists,
        Err(e) => {
            let error = actix_web::error::ErrorInternalServerError(format!("Redis error: {}", e));
            return Err((error, req));
        }
    };

    if exists {
        token_cache.lock().await.insert(token.to_string());
        Ok(req)
    } else {
        Err((actix_web::error::ErrorUnauthorized("Invalid token"), req))
    }
}