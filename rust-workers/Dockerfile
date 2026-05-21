FROM rust:1.79 as build
WORKDIR /app
COPY Cargo.toml Cargo.toml
COPY src src
RUN cargo build --release

FROM debian:bookworm-slim
COPY --from=build /app/target/release/rust-workers /usr/local/bin/rust-workers
CMD ["/usr/local/bin/rust-workers"]
