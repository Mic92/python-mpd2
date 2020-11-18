with import <nixpkgs> {};

stdenv.mkDerivation {
  name = "env";
  buildInputs = [
    bashInteractive
    python27
    python36
    python37
    python38
    python39
    pypy
    (python38.withPackages(ps: [ps.setuptools ps.tox ps.wheel ps.twine]))
  ];
}
