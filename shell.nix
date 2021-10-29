with import <nixpkgs> {};

stdenv.mkDerivation {
  name = "env";
  buildInputs = [
    bashInteractive
    python37
    (python38.withPackages(ps: [ps.setuptools ps.tox ps.wheel ps.twine]))
    python39
    python310
    pypy3
  ];
  shellHook = ''
    # breaks python36/python37
    unset _PYTHON_SYSCONFIGDATA_NAME
  '';
}
