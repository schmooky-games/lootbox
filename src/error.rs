use serde::Serialize;

#[derive(Serialize)]
pub struct ErrorHTTPException {
    pub status_code: u16,
    pub error_code: u16,
    pub detail: String,
}