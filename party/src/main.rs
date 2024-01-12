use std::convert::Infallible;
use std::net::SocketAddr;

use http_body_util::Full;
use hyper::body::Bytes;
use hyper::server::conn::http1;
use hyper::service::service_fn;
use hyper::{Request, Response};
use hyper_util::rt::TokioIo;
use tokio::net::TcpListener;

async fn hello(_: Request<hyper::body::Incoming>) -> Result<Response<Full<Bytes>>, Infallible> {
    Ok(Response::new(Full::new(Bytes::from("hey"))))
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let addr = SocketAddr::from(([127, 0, 0, 1], 3000));

    // We create a TcpListener and bind it to 127.0.0.1:3000
    let listener = TcpListener::bind(addr).await?;

    // We start a loop to continuously accept incoming connections
    loop {
        let (stream, _) = listener.accept().await?;

        // Use an adapter to access something implementing `tokio::io` traits as if they implement
        // `hyper::rt` IO traits.
        let io = TokioIo::new(stream);

        // Spawn a tokio task to serve multiple connections concurrently
        tokio::task::spawn(async move {
            // Finally, we bind the incoming connection to our `hello` service
            if let Err(err) = http1::Builder::new()
                // `service_fn` converts our function in a `Service`
                .serve_connection(io, service_fn(hello))
                .await
            {
                println!("Error serving connection: {:?}", err);
            }
        });
    }
}

// TODO main route to serve index
    // this has authorship app on it (source selector + line sculptor)
    // auth only if you want to add your own sources
// TODO authed GET to see list of saved pieces
// TODO authed POST to save a piece
// TODO authed GET source upload form page
// TODO authed POST endpoint to accept a text for phrasing
// TODO POST signup
// TODO GET to trade a secret for a session cookie (from email)

/* what to do about user state
 *
 * I want users to be able to add sources; I want them to be able to keep them private, though.
 *
 * I don't really feel like having a whole user account thing though that might be the correct
 * solution.
 *
 * I think email + sign in links (eg no password) is the way to go with long lived cookie.
 *
 *
 */

