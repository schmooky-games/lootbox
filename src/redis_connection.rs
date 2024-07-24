pub mod redis_connection {
    use redis::Client;

    pub async fn create_client() -> redis::RedisResult<Client> {
        let redis_uri = std::env::var("REDIS_URI").expect("REDIS_URL must be set");
        Client::open(redis_uri)
    }
}