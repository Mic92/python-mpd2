with import <nixpkgs> {};

stdenv.mkDerivation {
  name = "env";
  buildInputs = [
    bashInteractive
    python36
    python37
    (python38.withPackages(ps: [ps.setuptools ps.tox ps.wheel ps.twine ps.mypy]))
    python39
    pypy3
  ];
}
