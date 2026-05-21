use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Event {
    pub id: String,
    pub payload: String,
}

pub fn normalize_event(event: Event) -> Event {
    Event {
        id: event.id.to_uppercase(),
        payload: event.payload.trim().to_string(),
    }
}
