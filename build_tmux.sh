 POSIX-compliant script to build tmux and its dependencies from scratch.
 # Works with tcsh and ensures all required libraries are downloaded and compiled locally.
 # set -e
 #
 # # Configuration variables
 # INSTALL_PATH="$HOME/local_tmux"
 # LIBEVENT_VERSION="libevent-2.1.12-stable"
 # TMUX_VERSION="tmux-3.3a"
 # NCURSES_VERSION="ncurses-6.4"
 # BUILD_DIR="$HOME/build_tmux"
 #
 # # Ensure paths are in the environment
 # export PATH="$INSTALL_PATH/bin:$PATH"
 # export PKG_CONFIG_PATH="$INSTALL_PATH/lib/pkgconfig:$PKG_CONFIG_PATH"
 # export LD_LIBRARY_PATH="$INSTALL_PATH/lib:$LD_LIBRARY_PATH"
 #
 # # Clean up and prepare build directory
 # if [ -d "$BUILD_DIR" ]; then
 #     echo "Cleaning up existing build directory..."
 #         rm -rf "$BUILD_DIR"
 #         fi
 #         mkdir -p "$BUILD_DIR"
 #         cd "$BUILD_DIR"
 #
 #         # Function to download a file if not already present
 #         download() {
 #             URL=$1
 #                 FILENAME=$(basename "$URL")
 #                     if [ ! -f "$FILENAME" ]; then
 #                             echo "Downloading $FILENAME..."
 #                                     curl -LO "$URL"
 #                                         else
 #                                                 echo "$FILENAME already exists, skipping download."
 #                                                     fi
 #                                                     }
 #
 #                                                     # Step 1: Download sources
 #                                                     echo "Downloading sources..."
 #                                                     download "https://invisible-mirror.net/archives/ncurses/$NCURSES_VERSION.tar.gz"
 #                                                     download "https://github.com/libevent/libevent/releases/download/release-2.1.12-stable/$LIBEVENT_VERSION.tar.gz"
 #                                                     download "https://github.com/tmux/tmux/releases/download/3.3a/$TMUX_VERSION.tar.gz"
 #
 #                                                     # Step 2: Extract sources
 #                                                     echo "Extracting sources..."
 #                                                     for archive in *.tar.gz; do
 #                                                         tar -xzf "$archive"
 #                                                         done
 #
 #                                                         # Step 3: Build and install ncurses
 #                                                         echo "Building ncurses..."
 #                                                         cd "$NCURSES_VERSION"
 #                                                         ./configure --prefix="$INSTALL_PATH" --with-shared --without-debug --enable-widec
 #                                                         make -j$(nproc)
 #                                                         make install
 #                                                         cd ..
 #
 #                                                         # Step 4: Build and install libevent
 #                                                         echo "Building libevent..."
 #                                                         cd "$LIBEVENT_VERSION"
 #                                                         ./configure --prefix="$INSTALL_PATH" --disable-openssl
 #                                                         make -j$(nproc)
 #                                                         make install
 #                                                         cd ..
 #
 #                                                         # Step 5: Build and install tmux
 #                                                         echo "Building tmux..."
 #                                                         cd "$TMUX_VERSION"
 #                                                         ./configure --prefix="$INSTALL_PATH" \
 #                                                             PKG_CONFIG="$INSTALL_PATH/bin/pkg-config" \
 #                                                                 CFLAGS="-I$INSTALL_PATH/include" \
 #                                                                     LDFLAGS="-L$INSTALL_PATH/lib"
 #                                                                     make -j$(nproc)
 #                                                                     make install
 #                                                                     cd ..
 #
 #                                                                     # Step 6: Cleanup build directory
 #                                                                     echo "Cleaning up build directory..."
 #                                                                     rm -rf "$BUILD_DIR"
 #
 #                                                                     # Step 7: Add tmux to PATH (for tcsh users)
 #                                                                     echo "Ensure tmux is in your PATH. Add the following to your .tcshrc:"
 #                                                                     echo "setenv PATH $INSTALL_PATH/bin:\$PATH"
 #
 #                                                                     echo "tmux has been successfully built and installed in $INSTALL_PATH!"
 #                                                                     :wq!
 #                                                                     :q!
 #                                                                     :q!
 #                                                                     :wq!
 #
