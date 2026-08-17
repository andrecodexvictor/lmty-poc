.PHONY: c-test rust-test clean

c-test:
	$(CC) -std=c11 -O2 -Wall -Wextra c_kernel/lmty_kernel.c c_kernel/test_kernel.c -o c_kernel/test_kernel
	./c_kernel/test_kernel

rust-test:
	cargo test --manifest-path rust_kernel/Cargo.toml

clean:
	rm -f c_kernel/test_kernel
	cargo clean --manifest-path rust_kernel/Cargo.toml
