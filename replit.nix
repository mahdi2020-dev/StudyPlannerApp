{pkgs}: {
  deps = [
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
