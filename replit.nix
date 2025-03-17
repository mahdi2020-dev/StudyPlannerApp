{pkgs}: {
  deps = [
    pkgs.zlib
    pkgs.c-ares
    pkgs.cacert
    pkgs.libffi
    pkgs.glibcLocales
    pkgs.borgbackup
    pkgs.grpc
    pkgs.sqlite
    pkgs.postgresql
    pkgs.xcb-util-cursor
    pkgs.dbus
    pkgs.zstd
    pkgs.freetype
    pkgs.fontconfig
    pkgs.libxkbcommon
    pkgs.rustc
    pkgs.pkg-config
    pkgs.openssl
    pkgs.libxcrypt
    pkgs.libiconv
    pkgs.cargo
  ];
}
