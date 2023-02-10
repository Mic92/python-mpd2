# https://github.com/NixOS/nixpkgs/pull/196360
{ pkgs ? import <nixpkgs> {}
}:

pkgs.stdenv.mkDerivation {
  name = "env";
  buildInputs = with pkgs; [
    bashInteractive
    python38
    python39
    (python310.withPackages(ps: [ps.setuptools ps.tox ps.wheel]))
    python311
    python312
    pypy3
    twine
  ];
  shellHook = ''
    # breaks python36/python37
    unset _PYTHON_SYSCONFIGDATA_NAME
  '';
}
