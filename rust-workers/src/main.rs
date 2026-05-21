use axum::{extract::State, routing::post, Json, Router};
use serde::{Deserialize, Serialize};
use std::{env, net::SocketAddr, sync::Arc};

#[derive(Clone, Default)]
struct AppState;

#[derive(Deserialize)]
struct ProbeRequest { model_pool: String, providers: Vec<ProviderInput> }
#[derive(Deserialize)]
struct ProviderInput { api_key: String }
#[derive(Serialize)]
struct ProbeResponse { providers: Vec<ProviderStatus> }
#[derive(Serialize)]
struct ProviderStatus { api_key: String, available: bool, latency_ms: u64, reason: Option<String> }

async fn probe_providers(State(_state): State<Arc<AppState>>, Json(req): Json<ProbeRequest>) -> Json<ProbeResponse> {
    let _ = req.model_pool;
    let providers = req.providers.into_iter().map(|p| ProviderStatus { api_key: p.api_key, available: true, latency_ms: 1, reason: None }).collect();
    Json(ProbeResponse { providers })
}

#[tokio::main]
async fn main() {
    let state = Arc::new(AppState::default());
    let app = Router::new().route("/v1/probe/providers", post(probe_providers)).with_state(state);
    let port = env::var("PORT").unwrap_or_else(|_| "8081".to_string());
    let addr: SocketAddr = format!("0.0.0.0:{port}").parse().unwrap();
    axum::serve(tokio::net::TcpListener::bind(addr).await.unwrap(), app).await.unwrap();
}
