use std::net::{SocketAddr, TcpStream};
use std::time::Duration;

#[tauri::command]
fn backend_ready(host: Option<String>, port: Option<u16>) -> bool {
    let host = host.unwrap_or_else(|| "127.0.0.1".to_string());
    let port = port.unwrap_or(8765);
    let address = format!("{host}:{port}");
    let Ok(socket_address) = address.parse::<SocketAddr>() else {
        return false;
    };

    TcpStream::connect_timeout(&socket_address, Duration::from_millis(700)).is_ok()
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![backend_ready])
        .run(tauri::generate_context!())
        .expect("failed to run Local AI Academic Assistant desktop shell");
}
