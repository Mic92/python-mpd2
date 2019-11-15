with import <nixpkgs> {};

stdenv.mkDerivation {
  name = "env";
  buildInputs = [
    bashInteractive
    python27
    python35
    python36
    python37
    pypy
    (python.withPackages(ps: [ps.setuptools]))
    python38.pkgs.tox
  ];
  SOURCE_DATE_EPOCH="";
}
